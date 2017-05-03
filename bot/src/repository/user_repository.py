from src.config import db


class UserRepository:
    def __init__(self):
        self.conn = db.connection()

    def get_or_create(self, tg_id):
        return db.execute_and_get(lambda cur: cur.execute(
            """
            INSERT INTO Users (telegram_id)
            VALUES (%(tg_id)s)
            ON CONFLICT DO NOTHING;
            SELECT *
            FROM Users
            WHERE telegram_id = %(tg_id)s;
            """,
            {'tg_id': tg_id}
        ))
