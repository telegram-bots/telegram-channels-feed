from telegram import ParseMode
from . import Base
from src.exception.subscription_exception import GenericSubscriptionError
from src.config import subscriptions


# TODO. Добавить пагинацию и возможность нажать кнопку отписаться прямо там же, напротив каждого пункта из списка
class List(Base):
    name = 'list'

    def execute(self, command):
        if not command.is_private():
            self.reply(command, 'Groups currently are not supported!')

        try:
            subs = subscriptions.list(command)
            self.reply(command, self.__format_to_string(subs), parse_mode=ParseMode.MARKDOWN)
        except GenericSubscriptionError as e:
            self.reply(command, str(e))

    def __format_to_string(self, subs):
        result = []
        counter = 1
        for sub in subs:
            result.append(
                "{}. *{}* ([{}](https://t.me/{}))"
                    .format(counter, sub['name'], "@" + sub['url'], sub['url']))
            counter += 1

        return "\n".join(result)
