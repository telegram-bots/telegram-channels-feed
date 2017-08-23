class Post:
    def __init__(self, dictionary):
        self.text = dictionary['text']
        self.file_id = dictionary['fileId']
        self.preview_enabled = dictionary['previewEnabled']
        self.mode = self.get_parse_mode(dictionary['mode'])

    def get_parse_mode(self, mode):
        if mode == 'HTML':
            return 'HTML'
        elif mode == 'MARKDOWN':
            return 'Markdown'
        else:
            return None

    def __str__(self):
        return str(self.__dict__)


class PostGroup:
    def __init__(self, dictionary):
        self.channel_id = dictionary['channelId']
        self.message_id = dictionary['messageId']
        self.posts = {type: [Post(post) for post in posts] for type, posts in dictionary['posts'].items()}

    def __str__(self):
        return str(self.__dict__)
