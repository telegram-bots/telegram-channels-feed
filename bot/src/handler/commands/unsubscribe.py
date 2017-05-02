from . import Base
from src.config import subscriptions


class Unsubscribe(Base):
    name = 'unsubscribe'

    @staticmethod
    def execute(bot, command):
        if not command.is_private():
            Unsubscribe.reply(bot, command, 'Groups currently are not supported!')

        try:
            channel_name = subscriptions.unsubscribe(command)
            Unsubscribe.reply(bot, command, 'Successfully unsubscribed from "{}"'.format(channel_name))
        except IndexError:
            Unsubscribe.reply(bot, command, "That's not valid channel id. Try again.")
        except:
            Unsubscribe.reply(bot, command, "Failed to unsubscribe. Please try again later.")
