from . import Base
from src.config import subscriptions


class Subscribe(Base):
    name = 'subscribe'

    @staticmethod
    def execute(bot, command):
        if not command.is_private():
            Subscribe.reply(bot, command, 'Groups currently are not supported!')

        try:
            channel_name = subscriptions.subscribe(command)
            Subscribe.reply(bot, command, 'Successfully subscribed to "{}"'.format(channel_name))
        except NameError:
            Subscribe.reply(bot, command, "Illegal channel url! Type /help")
        except:
            Subscribe.reply(bot, command, "Failed to subscribe. Please try again later.")
