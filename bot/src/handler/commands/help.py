import os

from telegram.parsemode import ParseMode
from src.utils import read_to_string
from . import Base


class Help(Base):
    name = 'help'
    text = read_to_string(os.path.join('resources', 'info', 'help.md'))

    def execute(self, command):
        self.reply(command, self.text, parse_mode=ParseMode.MARKDOWN)
