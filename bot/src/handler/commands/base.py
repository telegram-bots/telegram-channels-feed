import logging
from abc import ABC, abstractmethod


class Base(ABC):
    name = None
    aliases = []
    bot = None

    @abstractmethod
    def execute(self, command):
        pass

    def reply(self, command, text, parse_mode=None, disable_web_page_preview=True):
        logging.debug("[Chat %s %s command] %s: %s" %
                      (command.chat_type,
                       command.chat_id,
                       command.name,
                       text))

        self.bot.send_message(
            chat_id=command.chat_id,
            reply_to_message_id=command.message.message_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )
