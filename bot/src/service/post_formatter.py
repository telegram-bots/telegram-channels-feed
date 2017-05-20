from typing import Optional, Tuple
import pprint


class PostFormatter:
    """
    Formats a telegram message into text representation.
    Supported text types: MARKDOWN, HTML, None (plain text)
    """
    MAX_MESSAGE_LENGTH = 4096

    def __init__(self):
        pass

    def format(self, json_obj) -> Tuple[Optional[str], str]:
        """
        Format a json_object into text representation.
        :param json_obj: JSON object to format 
        :return: Text type ('html', 'markdown', None) and formatted json_object as str
        """
        return None, str(pprint.pformat(json_obj, indent=4))[:self.MAX_MESSAGE_LENGTH]
