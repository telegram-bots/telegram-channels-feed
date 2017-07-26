from sqlalchemy import or_
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload
from typing import Generator

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

    def has(self, user_id: int, channel_url: str) -> bool:
        return db.session \
           .execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM Subscriptions AS sub
                    JOIN Users AS u ON u.id = sub.user_id
                    JOIN Channels AS ch ON ch.id = sub.channel_id
                    WHERE u.id = :user_id AND ch.url = :channel_url
                    """
                ),
                {'user_id': user_id, 'channel_url': channel_url}
            ).fetchone()[0] > 0

    def all(self, channel_telegram_id: int, message_id: int) -> Generator[Subscription, None, None]:
        query = db.session \
            .query(Subscription) \
            .options(joinedload(Subscription.user)) \
            .join(Subscription.channel) \
            .filter(Channel.telegram_id == channel_telegram_id) \
            .filter(or_(Channel.last_message_id < message_id, Channel.last_message_id == None)) \
            .filter(or_(Subscription.last_message_id < message_id, Subscription.last_message_id == None))

        return db.get_lazy(query)

    def set_message_id(self, user_id: int, channel_id: int, message_id: int):
        db.session \
            .query(Subscription) \
            .filter(Subscription.user_id == user_id) \
            .filter(Subscription.channel_id == channel_id) \
            .filter(or_(Subscription.last_message_id < message_id, Subscription.last_message_id == None)) \
            .update({Subscription.last_message_id: message_id})
