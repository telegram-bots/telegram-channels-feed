from telegram import ParseMode
from . import Base
from src.exception.subscription_exception import GenericSubscriptionError
from src.config import subscriptions


# TODO. Добавить пагинацию и возможность нажать кнопку отписаться прямо там же, напротив каждого пункта из списка
class List(Base):
    name = 'list'

    @staticmethod
    def execute(bot, command):
        if not command.is_private():
            List.reply(bot, command, 'Groups currently are not supported!')

        try:
            subs = subscriptions.list(command)
            List.reply(bot, command, List.format_to_string(subs), parse_mode=ParseMode.MARKDOWN)
        except GenericSubscriptionError as e:
            List.reply(bot, command, str(e))

    @staticmethod
    def format_to_string(subscriptions):
        result = []
        counter = 1
        for sub in subscriptions:
            result.append(
                "{}. *{}* ([{}](https://t.me/{}))"
                    .format(counter, sub['name'], "@" + sub['url'], sub['url']))
            counter += 1

        return "\n".join(result)
