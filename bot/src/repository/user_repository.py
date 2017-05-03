from src.config import db


class UserRepository:
    def __init__(self):
        self.conn = db.connection()

    def get(self, telegram_id):
        return db.get_one("SELECT * FROM USERS WHERE telegram_id = %s" % telegram_id)

    def get_or_create(self, telegram_id):
        return db.execute_and_get(lambda cur: cur.execute(
            """
            INSERT INTO Users (telegram_id)
            VALUES (%(telegram_id)s)
            ON CONFLICT DO NOTHING;
            SELECT *
            FROM Users
            WHERE telegram_id = %(telegram_id)s;
            """,
            {'telegram_id': telegram_id}
        ))
