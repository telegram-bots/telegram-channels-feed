from telegram.ext import MessageHandler as ParentHandler, Filters


class MessageHandler(ParentHandler):
    def __init__(self):
        super(MessageHandler, self).__init__(Filters.text, self.handle)

    def handle(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         reply_to_message_id=update.message.message_id,
                         text="I don't understand this. Please type /help")
