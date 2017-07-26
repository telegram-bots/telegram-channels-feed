from src.config import settings
from src.exception.settings_exception import GenericSettingsError
from . import Base


class RemoveRedirect(Base):
    name = 'remove_redirect'

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            settings.remove_channel_redirect(command)
            self.reply(command, f"Successfully removed redirect")
        except GenericSettingsError as e:
            self.reply(command, str(e))
