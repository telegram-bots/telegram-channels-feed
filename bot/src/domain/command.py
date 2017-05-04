import re


class Command:
    """
    Special class for message which contains command
    """
    def __init__(self, message):
        self.chat_id = message.chat.id
        self.chat_type = message.chat.type
        self.message = message
        self.name = Command.parse_name(message)
        self.args = Command.parse_args(message)
        self.channel_url = Command.parse_channel_url(self.args)

    def is_private(self):
        """Returns True if chat type is private.
        """
        return self.message.chat.type == 'private'

    def is_editing(self):
        """Returns True if the message was edited.
        """
        return self.message.edit_date is not None

    @staticmethod
    def parse_name(message):
        """
        Parses command name from given message
        :param message: Telegram message object
        :return: Name of command
        """
        return message.text[1:].split(' ')[0].split('@')[0]

    @staticmethod
    def parse_args(message):
        """
        Parses command args from given message
        :param message: Telegram message object
        :return: List of command args
        """
        return message.text.split()[1:]

    @staticmethod
    def parse_channel_url(args):
        """
        Parses channel URL from args or None if empty
        :param args: Parsed args
        :return: URL of channel
        """
        try:
            url = re.search('(?:.*)(?:t.me\/|@)(.*)', args[0]).group(1).strip()
            return None if url == '' else url
        except:
            return None
