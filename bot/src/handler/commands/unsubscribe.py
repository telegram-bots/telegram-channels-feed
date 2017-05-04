from . import Base
from src.config import subscriptions
from src.exception.subscription_exception import GenericSubscriptionError


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
        except GenericSubscriptionError as e:
            Unsubscribe.reply(bot, command, str(e))
