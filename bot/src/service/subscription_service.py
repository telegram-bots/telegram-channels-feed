import logging

from ..config import config, subscription_repository


class SubscriptionService:
    """
    Subscriptions management
    """
    def __init__(self):
        self.subscription_repository = subscription_repository

    def subscribe(self):
        self.subscription_repository.add()
        pass

    def unsubscribe(self):
        self.subscription_repository.delete()
        pass
