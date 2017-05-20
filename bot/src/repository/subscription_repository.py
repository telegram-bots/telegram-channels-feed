from datetime import datetime
from typing import Generator
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from src.config import db
from src.domain.entities import Subscription, Channel


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

    def all(self, channel_telegram_id: int, timestamp: datetime) -> Generator[Subscription, None, None]:
        query = db.session \
            .query(Subscription) \
            .options(joinedload(Subscription.user)) \
            .options(joinedload(Subscription.channel)) \
            .join(Subscription.channel) \
            .filter(Channel.telegram_id == channel_telegram_id) \
            .filter(or_(Channel.last_update < timestamp, Channel.last_update == None)) \
            .filter(or_(Subscription.last_update < timestamp, Subscription.last_update == None))

        return db.get_lazy(query)

    def set_timestamp(self, user_id: int, channel_id: int, timestamp: datetime):
        db.session \
            .query(Subscription) \
            .filter(Subscription.user_id == user_id) \
            .filter(Subscription.channel_id == channel_id) \
            .filter(or_(Subscription.last_update < timestamp, Subscription.last_update == None)) \
            .update({Subscription.last_update: timestamp})
