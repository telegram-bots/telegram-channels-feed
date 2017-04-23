import logging

from ..config import config, db


class SubscriptionService:
    """
    Subscriptions management
    """
    def __init__(self):
        pass

    def subscribe(self, command):
        user_telegram_id = command.chat_id
        channel_telegram_id = command.args[0]
        channel_name = "#TODO"

        #return nothing

    def unsubscribe(self, command):
        user_telegram_id = command.chat_id
        channel_telegram_id = command.args[0]

        #return nothing

    def list_subscriptions(self, command):
        user_telegram_id = command.chat_id

        #return [(channel_name 1, channel_id 1), (channel_name 1, channel_id 1), ... (channel_name N, channel_id N))
