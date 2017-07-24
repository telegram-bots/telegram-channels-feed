from datetime import datetime


class Post:
    def __init__(self, text, mode=None, type=None, keyboard=None, preview_enabled=False, file_id=None):
        self.text = text
        self.mode = mode
        self.type = type
        self.keyboard = keyboard
        self.preview_enabled = preview_enabled
        self.file_id = file_id

    def __str__(self):
        return str(self.__dict__)


class PostType:
    TEXT = 'text'
    PHOTO = 'photo'
    VIDEO = 'video'


class PostInfo:
    def __init__(self, channel_telegram_id: int, message_id: int, date: datetime, content, update: bool):
        self.channel_telegram_id = channel_telegram_id
        self.message_id = message_id
        self.date = date
        self.content = content
        self.update = update

    def __str__(self):
        return str(self.__dict__)
