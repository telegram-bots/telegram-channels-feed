class Post:
    def __init__(self, text, type=None, keyboard=None, preview_enabled=False):
        self.text = text
        self.type = type
        self.keyboard = keyboard
        self.preview_enabled = preview_enabled
