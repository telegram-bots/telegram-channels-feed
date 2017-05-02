import logging
import json
import select
import psycopg2
import psycopg2.extensions

from src.config import db
from src.utils import threaded


class Notifications:
    CHANNEL = "events"

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

        data = self.subscriptions.get_subscription_data(update.channel_tg_id)
        print(data)
        print(list(data))

        # for _, tg_id in subscribers:
        #     self.bot.send_message(chat_id=tg_id, text=str(update.raw))


class Update:
    def __init__(self, data):
        self.pid = data.pid
        self.channel = data.channel
        payload = json.loads(data.payload)['data']
        self.channel_tg_id = payload['channel_telegram_id']
        self.message_id = payload['message_id']
        self.raw = payload['raw']

    def __str__(self):
        return "Pid: {}, DB Channel: {}, TG Channel ID: {}, Message ID: {}, Raw: {}".\
            format(self.pid,
                   self.channel,
                   self.channel_tg_id,
                   self.message_id,
                   self.raw
                   )
