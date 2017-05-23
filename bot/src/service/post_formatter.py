import html

from telegram.parsemode import ParseMode

from src.domain.entities import Channel
from src.domain.post import Post, PostInfo


class PostFormatter:
    """
    Formats a telegram message into text representation.
    Supported text types: MARKDOWN, HTML, None (plain text)
    """
    MAX_MESSAGE_LENGTH = 4096

    def __init__(self, channel: Channel, post_info: PostInfo):
        self.channel = channel
        self.post_info = post_info

    def format(self) -> Post:
        """
        Format a json_object into text representation.
        :return: Text type ('html', 'markdown', None) and formatted json_object as str
        """
        has_links, text = self.__make_text()

        return Post(
            text=text,
            type=ParseMode.HTML,
            preview_enabled=has_links
        )

    def __make_text(self):
        first_link = self.__extract_first_link()
        header = self.__generate_header()
        text = self.__extract_text()

        return first_link != "", self.__shorten_text(first_link + header + text)

    def __generate_header(self) -> str:
        return f"<b>new in</b> <a href=\"https://t.me/{self.channel.url}/{self.post_info.raw['id_']}\">{html.escape(self.channel.name)}</a>"

    def __extract_text(self) -> str:
        text = None
        raw = self.post_info.raw

        if 'text_' in raw['content_']:
            text = raw['content_']['text_']
        elif 'caption_' in raw['content_']:
            text = raw['content_']['caption_']

        return "\n\n" + html.escape(text) if text is not None and text is not False else ""

    def __extract_first_link(self) -> str:
        link = None
        raw = self.post_info.raw

        if 'photo_' in raw['content_']:
            photos = raw['content_']['photo_']['sizes_']
            for k in sorted(photos, reverse=True):
                link = photos[k]['photo_']['persistent_id_']
                break
        elif 'entities_' in raw['content_']:
            entities = raw['content_']['entities_']
            for entity in entities.values():
                if entity['ID'] == 'MessageEntityUrl':
                    offset = entity['offset_']
                    length = entity['length_']
                    text = raw['content_']['text_'].encode('utf-16-le')
                    link = text[offset * 2:(length + offset) * 2].decode('utf-16-le')
                    break

        return f"<a href=\"{html.escape(link)}\">\xad</a>" if link is not None else ""

    def __shorten_text(self, text) -> str:
        if len(text) <= self.MAX_MESSAGE_LENGTH:
            return text

        return text[:self.MAX_MESSAGE_LENGTH - 6].strip() + ' [...]'
