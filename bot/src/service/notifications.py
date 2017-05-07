import json
import logging

import pprint
import select
from datetime import datetime
from retry import retry
from telegram.error import NetworkError

from src.utils import threaded


class Notifications:
    """
    Listen to updates and send them
    """
    def __init__(self, subscriptions):
        self.subscriptions = subscriptions
        # self.conn = db.connection()
        # self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def instance(self, bot):
        # handler = Handler(bot=bot, subscriptions=self.subscriptions)
        # listener = Listener(conn=self.conn, handler=handler)
        # listener.listen()

        return self


class Listener:
    CHANNEL = "events"

    def __init__(self, conn, handler):
        self.conn = conn
        self.handler = handler

    @threaded
    def listen(self):
        """Listen to a channel."""
        # cursor = self.conn.cursor()
        # cursor.execute("LISTEN %s;" % self.CHANNEL)

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

        subs = self.subscriptions.all(update.channel_tg_id)
        for sub in subs:
            if sub.channel.last_update is not None and sub.channel.last_update >= update.timestamp:
                break
            if sub.last_update is not None and sub.last_update >= update.timestamp:
                continue

            self.__send_message(chat_id=sub.user.telegram_id, data=update.raw)
            #SQL: Обновляем timestamp у subscription_last_update
            #SQL: Удаляем сообщение из БД

        #SQL: Обновляем timestamp у channel_last_update
        print(list(subs))

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
        return str(self.__dict__)
