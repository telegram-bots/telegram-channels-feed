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
        logging.debug(f"Reply to command [{command}]: {text}")

        self.bot.send_message(
            chat_id=command.chat_id,
            reply_to_message_id=command.message.message_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )
