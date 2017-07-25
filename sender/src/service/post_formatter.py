import html

from telegram.parsemode import ParseMode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

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
            keyboard=self.__generate_keyboard(),
            file_id=file_id
        )

    def __generate_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(
                'Mark as read',
                callback_data='mark'
            )
        ]])

    def __generate_header(self) -> str:
        return f"<a href=\"https://t.me/{self.channel.url}\">{html.escape(self.channel.name)}</a>:"

    def __generate_caption(self) -> str:
        return f"via {self.channel.name}(@{self.channel.url})"

    def __extract_text(self) -> str:
        text = ""
        content = self.post_info.content

        if 'text_' in content:
            text = content['text_']
            if text is not None:
                text = self.__convert_entities_to_html(self.__replace_html_tags(text))
            else:
                text = ""
        elif 'caption_' in content:
            text = content['caption_']
            if text is False:
                text = ""

        return "\n\n" + text

    def __extract_first_link(self) -> str:
        content = self.post_info.content

        if 'photo_' in content:
            photos = content['photo_']['sizes_']
            for k in sorted(photos, reverse=True):
                return photos[k]['photo_']['persistent_id_']
        elif 'entities_' in content:
            utf16text = content['text_'].encode('utf-16-le')
            entities = content['entities_']
            for entity in entities.values():
                if entity['ID'] == 'MessageEntityUrl':
                    offset = entity['offset_']
                    length = entity['length_']
                    link = utf16text[offset * 2:(length + offset) * 2].decode('utf-16-le')
                    return f"<a href=\"{html.escape(link)}\">\xad</a>" if link is not None else ""

        return ""

    def __replace_html_tags(self, text: str) -> str:
        return text.replace('<', '&lt;') \
            .replace('>', '&gt;') \
            .replace('&', '&amp;')

    def __is_nested_tag_bound(self, text: str, offset: int, length: int):
        tags = [
            ('<a', '</a>'),
            ('<code>', '</code>'),
            ('<pre>', '<pre>'),
            ('<b>', '</b>'),
            ('<i>', '</i>'),
        ]

        for start_tag, end_tag in tags:
            start_tag_pos = text.find(start_tag, offset)
            end_tag_pos = text.find(end_tag, offset + length)

            if start_tag_pos != -1 and end_tag_pos != -1:
                return True

        return False

    def __convert_entities_to_html(self, text: str) -> str:
        content = self.post_info.content

        if 'entities_' not in content:
            return text

        utf16text = content['text_'].encode('utf-16-le')
        entities = content['entities_']

        for entity in entities.values():
            offset = entity['offset_']
            length = entity['length_']
            extracted = utf16text[offset * 2:(length + offset) * 2].decode('utf-16-le')

            if self.__is_nested_tag_bound(text, offset, length):
                continue

            if entity['ID'] == 'MessageEntityTextUrl':
                url = entity['url_']
                text = text.replace(extracted, f"<a href=\"{url}\">{extracted}</a>", 1)
            elif entity['ID'] == 'MessageEntityBold':
                text = text.replace(extracted, f"<b>{extracted}</b>", 1)
            elif entity['ID'] == 'MessageEntityItalic':
                text = text.replace(extracted, f"<i>{extracted}</i>", 1)
            elif entity['ID'] == 'MessageEntityCode':
                text = text.replace(extracted, f"<code>{extracted}</code>", 1)
            elif entity['ID'] == 'MessageEntityPre':
                text = text.replace(extracted, f"<pre>{extracted}</pre>", 1)

        return text

    def __get_type(self) -> str:
        if 'photo_' in self.post_info.content:
            return PostType.PHOTO

        return PostType.TEXT

    def __shorten_text(self, text: str, post_type: str) -> str:
        max_length = self.MAX_MESSAGE_LENGTH[post_type]

        if len(text) <= max_length:
            return text

        return text[:max_length - 3].strip() + '...'
