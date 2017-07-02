from src.domain.callback import Callback
from telegram.ext import CallbackQueryHandler


class CallbackHandler(CallbackQueryHandler):
    def __init__(self):
        super(CallbackHandler, self).__init__(self.handle)

    def handle(self, bot, update):
        cb = Callback(update)

        if cb.data == 'mark':
            bot.delete_message(chat_id=cb.chat_id, message_id=cb.message_id)
