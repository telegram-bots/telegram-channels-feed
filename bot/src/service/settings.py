import logging

from src.config import db, user_repository
from src.domain.command import Command
from src.exception.settings_exception import *


class Settings:
    """
    User settings management
    """
    def __init__(self):
        pass

    def add_channel_redirect(self, command: Command):
        def callback():
            user = user_repository.get_or_create(telegram_id=command.chat_id)
            user_repository.change_settings(telegram_id=user.telegram_id, redirect_url=f"@{command.channel_url}")

        try:
            db.execute_in_transaction(callback)
        except Exception as e:
            logging.error(f"Failed to add redirect: {e}")
            raise RedirectChangeError("Failed to add redirect")

    def remove_channel_redirect(self, command: Command):
        def callback():
            user = user_repository.get(telegram_id=command.chat_id)
            if user is None or user.redirect_url is None:
                raise RedirectChangeError("You don't have added redirect!")

            user_repository.change_settings(telegram_id=user.telegram_id, redirect_url=None)

        try:
            db.execute_in_transaction(callback)
        except Exception as e:
            logging.error(f"Failed to remove redirect: {e}")
            raise RedirectChangeError("Failed to remove redirect")
