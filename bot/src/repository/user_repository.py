from sqlalchemy.sql import text
from typing import Optional

from src.component.config import db
from src.domain.entities import User


class UserRepository:
    def get(self, telegram_id: int) -> Optional[User]:
        """
        Find user by his telegram_id
        :param telegram_id: User telegram_id
        :rtype: Optional[User]
        :return: Found user or None
        """
        return db.session \
            .query(User) \
            .from_statement(text("""SELECT * FROM users WHERE telegram_id = :telegram_id""")) \
            .params(telegram_id=telegram_id) \
            .first()

    def get_or_create(self, telegram_id: int) -> User:
        """
        Creates user if he doesn't exists or simply returns found user
        :param telegram_id: User telegram_id
        :rtype: User
        :return: Created or existing user
        """
        return db.session \
            .query(User) \
            .from_statement(text(
                """
                INSERT INTO users (telegram_id)
                VALUES (:telegram_id)
                ON CONFLICT DO NOTHING;
                SELECT * FROM users WHERE telegram_id = :telegram_id;
                """
            )) \
            .params(telegram_id=telegram_id) \
            .first()

    def change_settings(self, telegram_id: int, redirect_url: Optional[str]) -> bool:
        """
        Change user settings
        :param telegram_id: User telegram ID
        :param redirect_url: Redirect URL. Can be None
        :rtype: bool
        :return: Update successful or not
        """
        return db.session \
            .execute(
                text("""UPDATE users SET redirect_url = :redirect_url WHERE telegram_id = :telegram_id"""),
                {'telegram_id': telegram_id, 'redirect_url': redirect_url}
            ) \
            .rowcount > 0
