from typing import Generator
from datetime import datetime
from sqlalchemy.orm import subqueryload

from src.config import db
from src.domain.entities import Subscription, Channel, User


class SubscriptionRepository:
    def create(self, user_id: int, channel_id: int):
        """
        Create subscription relation
        :param user_id: ID of user
        :param channel_id: ID of channel
        :throws sqlalchemy.exc.InvalidRequestError if subscription already exists
        """
        db.session.add(Subscription(user_id=user_id, channel_id=channel_id))

    def remove(self, user_id: int, channel_id: int) -> int:
        """
        Remove subscription relation
        :param user_id: ID of user
        :param channel_id: ID of channel
        :rtype: int
        :return How many left subscribers to this channel
        """
        db.session \
            .query(Subscription) \
            .filter(Subscription.user_id == user_id) \
            .filter(Subscription.channel_id == channel_id) \
            .delete()

        return db.session\
            .query(Subscription)\
            .filter(Subscription.channel_id == channel_id)\
            .count()

    def all(self, channel_telegram_id: int, timestamp: datetime):
        query = db.session \
            .query(Subscription) \
            .options(subqueryload("channel").subqueryload("user")) \
            .join(Subscription.channel) \
            .join(Subscription.user) \
            .filter(Channel.telegram_id == channel_telegram_id)

        print(str(query))
