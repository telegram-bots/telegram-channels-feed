from telegram.parsemode import ParseMode
from typing import List as TList

from src.component.config import subscriptions
from src.domain.entities import Channel
from src.exception.subscription_exception import GenericSubscriptionError
from . import Base


# TODO. Добавить пагинацию и возможность нажать кнопку отписаться прямо там же, напротив каждого пункта из списка
class List(Base):
    name = 'list'
    aliases = ['l']

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            channels = subscriptions.list(command)
            self.reply(command, self.__format_to_string(channels), parse_mode=ParseMode.MARKDOWN)
        except GenericSubscriptionError as e:
            self.reply(command, str(e))

    @staticmethod
    def __format_to_string(channels: TList[Channel]) -> str:
        if len(channels) == 0:
            return "You don't have active subscriptions."

        channels.sort(key=lambda c: c.name)

        result = []
        counter = 1
        for ch in channels:
            result.append(
                f"{counter}. *{ch.name}* ([@{ch.url}](https://t.me/{ch.url}))"
            )
            counter += 1

        return "\n".join(result)
