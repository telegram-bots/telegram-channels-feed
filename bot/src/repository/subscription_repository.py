from src.config import db


class SubscriptionRepository:
    def __init__(self):
        self.conn = db.connection()

    def create(self, user_id, channel_id):
        db.execute(lambda cur: cur.execute(
            """
            INSERT INTO Subscriptions (user_id, channel_id)
            VALUES (%(user_id)s, %(channel_id)s)
            ON CONFLICT DO NOTHING;
            """,
            {'user_id': user_id, 'channel_id': channel_id}
        ))

    def remove(self, user_id, channel_id):
        return db.execute_and_get(lambda cur: cur.execute(
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

    def list(self, user_telegram_id):
        return db.get_all(
            """
            SELECT ch.id, ch.url, ch.name
            FROM Subscriptions AS sub
            JOIN Users AS u ON u.id = sub.user_id
            JOIN Channels AS ch ON ch.id = sub.channel_id
            WHERE u.telegram_id = %d
            """ % user_telegram_id
        )
