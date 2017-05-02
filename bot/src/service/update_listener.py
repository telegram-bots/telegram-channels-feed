import logging
import json
import select
import psycopg2
import psycopg2.extensions

from src.config import db
from src.utils import threaded


class UpdateListener:
    CHANNEL = "events"

    """
    Listen to updates and send them
    """
    def __init__(self, subscriptions):
        self.subscriptions = subscriptions

    def instance(self, bot):
        self.bot = bot
        self.conn = db.connection()
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.__listener()

        return self

    @threaded
    def __listener(self):
        """Listen to a channel."""
        cursor = self.conn.cursor()
        cursor.execute("LISTEN %s;" % self.CHANNEL)

        while True:
            if select.select([self.conn], [], [], 1) != ([], [], []):
                self.conn.poll()
                self.__handler(self.conn.notifies)

    def __handler(self, updates):
        """Handle channel updates"""
        while updates:
            update = updates.pop(0)
            payload = json.loads(update.payload)
            channel_tg_id = payload['data']['channel_telegram_id']
            message_id = payload['data']['message_id']
            subscribers = self.subscriptions.list_subscribers(channel_tg_id)

            # logging.info("Got NOTIFY: " + str(update.pid))
            print(subscribers)

            for _, tg_id in subscribers:
                self.bot.send_message(chat_id=tg_id, text=str(payload['data']['raw']))
            print("PRINT NOTIFY", update.pid, update.channel, update.payload)


class Listener:
    def __init__(self):
        pass


class Handler:
    def __init__(self):
        pass


class Update:
    def __init__(self, data):
        pass
