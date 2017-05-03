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
            (user_id, channel_id)
        ))
