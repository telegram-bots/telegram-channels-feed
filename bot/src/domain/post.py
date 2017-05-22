from datetime import datetime


class Post:
    def __init__(self, text, type=None, keyboard=None, preview_enabled=False):
        self.text = text
        self.type = type
        self.keyboard = keyboard
        self.preview_enabled = preview_enabled

    def __str__(self):
        return str(self.__dict__)


class PostInfo:
    def __init__(self, channel_telegram_id: int, message_id: int, date: datetime, raw):
        self.channel_telegram_id = channel_telegram_id
        self.message_id = message_id
        self.date = date
        self.raw = raw

    def __str__(self):
        return str(self.__dict__)
