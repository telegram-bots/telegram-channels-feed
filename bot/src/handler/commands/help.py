import os
from . import Base
from src.utils import read_to_string


class Help(Base):
    name = 'help'
    text = read_to_string(os.path.join('resources', 'info', 'help.txt'))

    def execute(self, command):
        self.reply(command, self.text)
