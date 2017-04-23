from . import PostgreRepository
from ..config import config


class SubscriptionRepository(PostgreRepository):
    def __init__(self):
        PostgreRepository.__init__(self)

    def add(self):
        pass

    def delete(self):
        pass
