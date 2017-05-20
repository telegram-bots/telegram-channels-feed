from . import Base
from src.config import subscriptions
from src.exception.subscription_exception import GenericSubscriptionError


class Subscribe(Base):
    name = 'subscribe'
    aliases = ['s']

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            channel = subscriptions.subscribe(command)
            self.reply(command, f"Successfully subscribed to {channel.name} (@{channel.url})")
        except GenericSubscriptionError as e:
            self.reply(command, str(e))
