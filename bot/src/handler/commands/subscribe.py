from . import Base
from src.config import subscriptions
from src.exception.subscription_exception import GenericSubscriptionError


class Subscribe(Base):
    name = 'subscribe'

    @staticmethod
    def execute(bot, command):
        if not command.is_private():
            Subscribe.reply(bot, command, 'Groups currently are not supported!')

        try:
            channel = subscriptions.subscribe(command)
            Subscribe.reply(bot, command,
                            'Successfully subscribed to "{}" (@{})'.format(channel['name'], channel['url']))
        except GenericSubscriptionError as e:
            Subscribe.reply(bot, command, str(e))
