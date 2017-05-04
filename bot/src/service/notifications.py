import logging
import json
import select
import psycopg2
import psycopg2.extensions
from telegram.error import NetworkError
from retry import retry
import pprint
from datetime import datetime

from src.config import db
from src.utils import threaded


class Notifications:
    """
    Listen to updates and send them
    """
    def __init__(self, subscriptions):
        self.subscriptions = subscriptions
        self.conn = db.connection()
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def instance(self, bot):
        handler = Handler(bot=bot, subscriptions=self.subscriptions)
        listener = Listener(conn=self.conn, handler=handler)
        listener.listen()

        return self


class Listener:
    CHANNEL = "events"

    def __init__(self, conn, handler):
        self.conn = conn
        self.handler = handler

    @threaded
    def listen(self):
        """Listen to a channel."""
        cursor = self.conn.cursor()
        cursor.execute("LISTEN %s;" % self.CHANNEL)

        while True:
            if select.select([self.conn], [], [], 1) != ([], [], []):
                self.conn.poll()
                while self.conn.notifies:
                    self.handler.handle(Update(self.conn.notifies.pop(0)))


class Handler:
    def __init__(self, bot, subscriptions):
        self.bot = bot
        self.subscriptions = subscriptions

    def handle(self, update):
        """Handle channel update"""
        logging.debug("Received update: {}".format(update))
        print(update)

        data = self.subscriptions.get_subscription_data(update.channel_tg_id)
        for row in data:
            if row['ch_last_update'] is not None and row['ch_last_update'] >= update.timestamp:
                break
            if row['sub_last_update'] is not None and row['sub_last_update'] >= update.timestamp:
                continue

            self.__send_message(chat_id=row['user_tg_id'], data=update.raw)
            #SQL: Обновляем timestamp у subscription_last_update
            #SQL: Удаляем сообщение из БД

        #SQL: Обновляем timestamp у channel_last_update
        print(list(data))

    @retry(NetworkError, tries=5, delay=10)
    def __send_message(self, chat_id, data):
        self.bot.send_message(chat_id=chat_id, text=pprint.pformat(data, indent=4))


class Update:
    def __init__(self, data):
        self.pid = data.pid
        self.channel = data.channel
        payload = json.loads(data.payload)['data']
        self.channel_tg_id = payload['channel_telegram_id']
        self.message_id = payload['message_id']
        self.timestamp = datetime.strptime(payload['timestamp'], "%Y-%m-%dT%H:%M:%S")
        self.raw = payload['raw']

    def __str__(self):
        return "Pid: {}, DB Channel: {}, TG Channel ID: {}, Message ID: {}, Timestamp: {}, Raw: {}".\
            format(self.pid,
                   self.channel,
                   self.channel_tg_id,
                   self.message_id,
                   self.timestamp,
                   self.raw
                   )
