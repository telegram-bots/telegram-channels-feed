import html

from telegram.parsemode import ParseMode

from src.domain.entities import Channel
from src.domain.post import Post, PostInfo, PostType


class PostFormatter:
    """
    Formats a telegram message into text representation.
    """
    MAX_MESSAGE_LENGTH = {
        PostType.PHOTO: 200,
        PostType.TEXT: 4096
    }

    def __init__(self, channel: Channel, post_info: PostInfo):
        self.channel = channel
        self.post_info = post_info

    def format(self) -> Post:
        """
        Format a json_object into text representation.
        :return: Post
        """
        return self.__make_post()

    def __make_post(self):
        post_type = self.__get_type()
        first_link = self.__extract_first_link()
        text = self.__extract_text()

        if post_type == PostType.TEXT:
            result = first_link + self.__generate_header() + text
            file_id = None
        else:
            result = self.__generate_caption() + text
            file_id = first_link

        return Post(
            text=self.__shorten_text(result, post_type),
            type=post_type,
            mode=ParseMode.HTML,
            preview_enabled=first_link != "",
            file_id=file_id
        )

    def __generate_header(self) -> str:
        return f"<b>new in</b> <a href=\"https://t.me/{self.channel.url}/{self.post_info.raw['id_']}\">{html.escape(self.channel.name)}</a>"

    def __generate_caption(self) -> str:
        return f"via {self.channel.name}(@{self.channel.url})"

    def __extract_text(self) -> str:
        text = None
        raw = self.post_info.raw

        if 'text_' in raw['content_']:
            text = raw['content_']['text_']
        elif 'caption_' in raw['content_']:
            text = raw['content_']['caption_']

        return "\n\n" + html.escape(text) if text is not None and text is not False else ""

    def __extract_first_link(self) -> str:
        raw = self.post_info.raw

        if 'photo_' in raw['content_']:
            photos = raw['content_']['photo_']['sizes_']
            for k in sorted(photos, reverse=True):
                return photos[k]['photo_']['persistent_id_']
        elif 'entities_' in raw['content_']:
            utf16text = raw['content_']['text_'].encode('utf-16-le')
            entities = raw['content_']['entities_']
            for entity in entities.values():
                if entity['ID'] == 'MessageEntityUrl':
                    offset = entity['offset_']
                    length = entity['length_']
                    link = utf16text[offset * 2:(length + offset) * 2].decode('utf-16-le')
                    return f"<a href=\"{html.escape(link)}\">\xad</a>" if link is not None else ""

        return ""

    def __get_type(self) -> str:
        raw = self.post_info.raw

        if 'photo_' in raw['content_']:
            return PostType.PHOTO

        return PostType.TEXT

    def __shorten_text(self, text: str, post_type: str) -> str:
        max_length = self.MAX_MESSAGE_LENGTH[post_type]

        if len(text) <= max_length:
            return text

        return text[:max_length - 3].strip() + '...'
