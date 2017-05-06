class Channel:
    def __init__(self, data):
        self.id = data['id']
        self.telegram_id = data['telegram_id']
        self.url = data['url']
        self.name = data['name']
        self.last_update = data['last_update']

    def __str__(self):
        return str(self.__dict__)


class User:
    def __init__(self, data):
        self.id = data['id']
        self.telegram_id = data['telegram_id']

    def __str__(self):
        return str(self.__dict__)


class Subscription:
    def __init__(self, data):
        self.user = User({k.replace('user_', ''): v for k, v in data.items() if 'user_' in k})
        self.channel = Channel({k.replace('channel_', ''): v for k, v in data.items() if 'channel_' in k})
        self.last_update = data['last_update']

    def __str__(self):
        return str(self.__dict__)

