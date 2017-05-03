from . import Base
from src.config import subscriptions


class Unsubscribe(Base):
    name = 'unsubscribe'

    @staticmethod
    def execute(bot, command):
        if not command.is_private():
            Unsubscribe.reply(bot, command, 'Groups currently are not supported!')

        try:
            channel = subscriptions.unsubscribe(command)
            Unsubscribe.reply(bot, command,
                              'Successfully unsubscribed from "{}" (@{})'.format(channel['name'], channel['url']))
        except NameError:
            Unsubscribe.reply(bot, command, "Illegal channel url! Type /help")
        except IndexError:
            Unsubscribe.reply(bot, command, "You are not subscribed to this channel.")
        except:
            Unsubscribe.reply(bot, command, "Failed to unsubscribe. Please try again later.")
