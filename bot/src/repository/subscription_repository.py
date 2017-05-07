from typing import Generator

from src.config import db
from src.domain.entities import Subscription


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

    def all(self, channel_telegram_id: int) -> Generator[Subscription, None, None]:
        return db.get_lazy(
            lambda cur: cur.execute(
                """
                SELECT
                 ch.id AS channel_id,
                 ch.telegram_id AS channel_telegram_id,
                 ch.url AS channel_url,
                 ch.name AS channel_name,
                 ch.last_update as channel_last_update,
                 u.id AS user_id,
                 u.telegram_id AS user_telegram_id,
                 sub.last_update AS last_update
                FROM Channels AS ch
                JOIN Subscriptions AS sub ON sub.channel_id = ch.id
                JOIN Users AS u ON u.id = sub.user_id
                WHERE ch.telegram_id = %s
                """,
                [channel_telegram_id]
            ),
            mapper=Subscription
        )
