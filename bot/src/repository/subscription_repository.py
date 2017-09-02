from sqlalchemy.sql import text
from typing import List

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

    def list(self, user_telegram_id: int) -> List[Channel]:
        """
            Get list of channels user subscribed to
            :param user_telegram_id: Telegram ID of user
            :rtype: List[Channel]
            :return: List of channels
            """
        return db.session \
            .query(Channel) \
            .from_statement(text(
                """
                SELECT ch.id, ch.telegram_id, ch.url, ch.name, ch.last_message_id
                FROM Subscriptions AS sub
                JOIN Users AS u ON u.id = sub.user_id
                JOIN Channels AS ch ON ch.id = sub.channel_id
                WHERE u.telegram_id = :user_telegram_id
                """
            )) \
            .params(user_telegram_id=user_telegram_id) \
            .all()
