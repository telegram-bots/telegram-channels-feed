import logging
import re

from src.config import config


class SubscriptionService:
    """
    Subscriptions management
    """
    def __init__(self, db, tg_cli):
        self.db = db
        self.tg_cli = tg_cli

    def subscribe(self, command):
        user_telegram_id = command.chat_id
        channel_url = self.__parse_channel_url(command)
        channel_telegram_id, channel_name = self.tg_cli.lookup_channel(channel_url)
        self.tg_cli.subscribe_to_channel(channel_telegram_id)

        #SQL HERE

        return channel_name

    def unsubscribe(self, command):
        user_telegram_id = command.chat_id
        channel_url = self.__parse_channel_url(command)
        channel_telegram_id, channel_name = self.tg_cli.lookup_channel(channel_url)

        #SQL HERE

        #return nothing

    def list_subscriptions(self, command):
        user_telegram_id = command.chat_id

        #return [(channel_name 1, channel_id 1), (channel_name 1, channel_id 1), ... (channel_name N, channel_id N))

    def __parse_channel_url(self, command):
        try:
            url = re.search('(?:.*)(?:t.me\/|@)(.*)', command.args[0]).group(1).strip()

            if url == '':
                raise NameError()

            return url
        except IndexError:
            raise NameError()
