class Callback:
    """
    Special class for message which contains query
    """
    def __init__(self, update):
        self.chat_id = update.callback_query.message.chat_id
        self.callback_query = update.callback_query
        self.data = update.callback_query.data
        self.message_id = update.callback_query.message.message_id

    def __str__(self):
        return str(self.__dict__)
