from . import Base
from src.config import subscription_service


class Unsubscribe(Base):
    name = 'unsubscribe'

    @staticmethod
    def execute(bot, command):
        if not command.is_private():
            Unsubscribe.reply(bot, command, 'Groups currently are not supported!')

        try:
            channel_name = subscription_service.unsubscribe(command)
            Unsubscribe.reply(bot, command, 'Successfully unsubscribed from "{}"'.format(channel_name))
        except:
            Unsubscribe.reply(bot, command, "Failed to unsubscribe. Please try again later.")
