import logging

from src.component.config import db, user_repository, subscription_repository
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

            has_subscription = subscription_repository.has(user_id=user.id, channel_url=command.channel_url)
            if has_subscription:
                raise RedirectNotAllowed()

            user_repository.change_settings(user_id=user.id, redirect_url=command.channel_url)

        try:
            db.execute_in_transaction(callback)
        except GenericSettingsError:
            raise
        except Exception as e:
            logging.exception("Failed to add redirect")
            raise RedirectChangeError("Failed to add redirect")

    def remove_channel_redirect(self, command: Command):
        def callback():
            user = user_repository.get(telegram_id=command.chat_id)
            if user is None or user.redirect_url is None:
                raise RedirectChangeError("You haven't added a redirect!")

            user_repository.change_settings(user_id=user.id, redirect_url=None)

        try:
            db.execute_in_transaction(callback)
        except GenericSettingsError:
            raise
        except Exception as e:
            logging.exception("Failed to remove redirect")
            raise RedirectChangeError("Failed to remove redirect")
