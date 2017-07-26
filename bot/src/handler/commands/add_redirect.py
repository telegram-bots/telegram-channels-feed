from src.config import settings
from src.exception.settings_exception import *
from telegram.error import Unauthorized
from . import Base
import logging


class AddRedirect(Base):
    name = 'add_redirect'

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            self.__try_post_message(command)
            settings.add_channel_redirect(command)
            self.reply(command, f"Successfully added redirect to @{command.channel_url})")
        except GenericSettingsError as e:
            self.reply(command, str(e))

    def __try_post_message(self, command):
        if command.channel_url is None:
            raise IllegalChannelUrlError()

        try:
            logging.debug(f"Trying to post message to channel...")
            self.bot.send_message(chat_id=f"@{command.channel_url}", text="Hello there :3")
        except Unauthorized:
            raise BotNotAddedAsAdminError()
