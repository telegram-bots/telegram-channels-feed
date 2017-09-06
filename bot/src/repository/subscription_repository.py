from sqlalchemy.sql import text
from typing import List

from src.component.config import db
from src.domain.entities import Channel


class SubscriptionRepository:
    def has(self, user_id: int, channel_id: int) -> bool:
        """
        Check if such subscription relation exists
        :param user_id: ID of user
        :param channel_id: ID of channel
        :return: Is subscription exists
        """
        return db.session \
            .execute(
                text("""SELECT COUNT(*) FROM subscriptions WHERE user_id = :user_id AND channel_id = :channel_id"""),
                {'user_id': user_id, 'channel_id': channel_id}
            ) \
            .fetchone()[0] > 0

    def create(self, user_id: int, channel_id: int) -> bool:
        """
        Create subscription relation
        :param user_id: ID of user
        :param channel_id: ID of channel
        :throws sqlalchemy.exc.InvalidRequestError if subscription already exists
        :rtype: bool
        :return: Create successful or not
        """
        return db.session \
            .execute(
                text("""INSERT INTO subscriptions (user_id, channel_id) VALUES (:user_id, :channel_id)"""),
                {'user_id': user_id, 'channel_id': channel_id}
            ) \
            .rowcount > 0

    def remove(self, user_id: int, channel_id: int) -> int:
        """
        Remove subscription relation
        :param user_id: ID of user
        :param channel_id: ID of channel
        :rtype: int
        :return How many left subscribers to this channel
        """
        return db.session \
            .execute(
                text(
                    """
                    DELETE FROM subscriptions WHERE user_id = :user_id AND channel_id = :channel_id;
                    SELECT COUNT(*) FROM subscriptions WHERE channel_id = :channel_id;
                    """
                ),
                {'user_id': user_id, 'channel_id': channel_id}
            ) \
            .fetchone()[0]

    def list(self, user_id: int) -> List[Channel]:
        """
        Get list of channels user subscribed to
        :param user_id: ID of user
        :rtype: List[Channel]
        :return: List of channels
        """
        return db.session \
            .query(Channel) \
            .from_statement(text(
                """
                SELECT ch.*
                FROM Subscriptions AS sub
                JOIN Channels AS ch ON ch.id = sub.channel_id
                WHERE sub.user_id = :user_id
                """
            )) \
            .params(user_id=user_id) \
            .all()
