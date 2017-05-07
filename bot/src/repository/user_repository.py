from sqlalchemy.sql import text

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
        return db.session\
            .query(User) \
            .filter(User.telegram_id == telegram_id) \
            .first()

    def get_or_create(self, telegram_id: int) -> User:
        """
        Creates user if he doesn't exists or simply returns found user
        :param telegram_id: User telegram_id
        :rtype: dict
        :return: User
        """
        return db.session \
            .query(User) \
            .from_statement(text(
                """
                INSERT INTO Users (telegram_id)
                VALUES (:telegram_id)
                ON CONFLICT DO NOTHING;
                SELECT *
                FROM Users
                WHERE telegram_id = :telegram_id;
                """
            )) \
            .params(telegram_id=telegram_id) \
            .first()
