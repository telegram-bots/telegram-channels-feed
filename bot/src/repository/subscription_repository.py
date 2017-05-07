from src.config import db
from src.domain.entities import Subscription
from typing import Generator


class SubscriptionRepository:
    def create(self, user_id: int, channel_id: int):
        """
        Create subscription relation
        :param user_id: ID of user
        :param channel_id: ID of channel
        :throws psycopg2.IntegrityError if subscription already exists
        """
        db.execute(lambda cur: cur.execute(
            """
            INSERT INTO Subscriptions (user_id, channel_id)
            VALUES (%(user_id)s, %(channel_id)s)
            """,
            {'user_id': user_id, 'channel_id': channel_id}
        ))

    def remove(self, user_id: int, channel_id: int) -> int:
        """
        Remove subscription relation
        :param user_id: ID of user
        :param channel_id: ID of channel
        :rtype: int
        :return How many left subscribers to this channel
        """
        return db.get_one(lambda cur: cur.execute(
            """
            DELETE FROM Subscriptions
            WHERE
              user_id = %(u_id)s
              AND channel_id = %(c_id)s;
            SELECT COUNT(*)
            FROM Subscriptions
            WHERE channel_id = %(c_id)s;
            """,
            {'u_id': user_id, 'c_id': channel_id}
        ))[0]

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
