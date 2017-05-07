from src.config import db
from src.domain.entities import User


class UserRepository:
    def get(self, telegram_id: int) -> User:
        """
        Find user by his telegram_id
        :param telegram_id: User telegram_id
        :rtype: dict
        :return: Found user or None
        """
        return db.get_one(
            lambda cur: cur.execute("SELECT * FROM USERS WHERE telegram_id = %s", [telegram_id]),
            mapper=User
        )

    def get_or_create(self, telegram_id: int) -> User:
        """
        Creates user if he doesn't exists or simply returns found user
        :param telegram_id: User telegram_id
        :rtype: dict
        :return: User
        """
        return db.get_one(
            lambda cur: cur.execute(
                """
                INSERT INTO Users (telegram_id)
                VALUES (%(telegram_id)s)
                ON CONFLICT DO NOTHING;
                SELECT *
                FROM Users
                WHERE telegram_id = %(telegram_id)s;
                """,
                {'telegram_id': telegram_id}
            ),
            mapper=User
        )
