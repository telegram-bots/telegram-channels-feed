class Post:
    def __init__(self, dictionary):
        self.text = dictionary['text']
        self.preview_enabled = dictionary['previewEnabled']
        self.mode = self.get_parse_mode(dictionary['mode'])

    def get_parse_mode(self, mode):
        if mode == 'HTML':
            return 'HTML'
        elif mode == 'MARKDOWN':
            return 'Markdown'
        elif mode == "AS_IS":
            return "AS_IS"
        else:
            return None

    def __str__(self):
        return str(self.__dict__)


class PostGroup:
    def __init__(self, dictionary):
        self.channel_id = dictionary['channelId']
        self.channel_url = dictionary['channelUrl']
        self.post_id = dictionary['postId']
        self.posts = {t: Post(post) for t, post in dictionary['posts'].items()}

    def __str__(self):
        return str(self.__dict__)
