import logging

import csv
import os
import os.path

from abc import ABC, abstractmethod
from telegram.parsemode import ParseMode
from typing import List as TList

from src.config import subscriptions
from src.domain.entities import Channel
from src.exception.subscription_exception import GenericSubscriptionError
from src.utils import read_to_string


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


class Start(Base):
    name = 'start'

    def execute(self, command):
        pass


class Help(Base):
    name = 'help'
    text = read_to_string(os.path.join('resources', 'info', 'help.txt'))

    def execute(self, command):
        self.reply(command, self.text)


# TODO. Добавить пагинацию и возможность нажать кнопку отписаться прямо там же, напротив каждого пункта из списка
class List(Base):
    name = 'list'

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            channels = subscriptions.list(command)
            self.reply(command, self.__format_to_string(channels), parse_mode=ParseMode.MARKDOWN)
        except GenericSubscriptionError as e:
            self.reply(command, str(e))

    def __format_to_string(self, channels: TList[Channel]) -> str:
        if len(channels) == 0:
            return "You don't have active subscriptions."

        result = []
        counter = 1
        for ch in channels:
            result.append(
                f"{counter}. *{ch.name}* ([@{ch.url}](https://t.me/{ch.url}))"
            )
            counter += 1

        return "\n".join(result)


class Export(Base):
    name = 'export'

    def execute(self, command):
        rows = subscriptions.list(command)
        if len(rows) == 0:
            self.reply(command, "You don't have active subscriptions.")

        file = f"{command.chat_id}_export.csv"
        self.__create_csv(file, subscriptions.list(command))
        self.bot.send_document(chat_id=command.chat_id,
                               document=open(file, 'rb'))
        os.remove(file)

    def __create_csv(self, file: str, rows: TList[Channel]):
        with open(file, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SHORT_URL', 'URL', 'TITLE'])
            for row in rows:
                writer.writerow([f"@{row.url}", f"https://t.me/{row.url}", row.name])


class Subscribe(Base):
    name = 'subscribe'

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            channel = subscriptions.subscribe(command)
            self.reply(command, f"Successfully subscribed to {channel.name} (@{channel.url})")
        except GenericSubscriptionError as e:
            self.reply(command, str(e))


class Unsubscribe(Base):
    name = 'unsubscribe'

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            channel = subscriptions.unsubscribe(command)
            self.reply(command, f"Successfully unsubscribed from {channel.name} (@{channel.url})")
        except GenericSubscriptionError as e:
            self.reply(command, str(e))


commands = {}
for clazz in Base.__subclasses__():
    command_name = getattr(clazz, 'name')
    command_aliases = getattr(clazz, 'aliases')
    instance = clazz()

    if command_name is not None:
        commands[command_name] = instance
    for command_alias in command_aliases:
        commands[command_alias] = instance
