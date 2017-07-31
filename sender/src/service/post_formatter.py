import html

from telegram.constants import *
from telegram.parsemode import ParseMode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional

from src.domain.entities import Channel
from src.domain.post import Post, PostInfo, PostType


class PostFormatter:
    """
    Formats a telegram message into text representation.
    """
    MAX_MESSAGE_LENGTH = {
        PostType.PHOTO: MAX_CAPTION_LENGTH,
        PostType.TEXT: MAX_MESSAGE_LENGTH
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

    def __convert_entities_to_html(self, text: str) -> str:
        def convert(utf16: bytes, entity: dict, start_pos: int, end_pos: int) -> Optional[str]:
            e_type = entity['ID']
            extracted = utf16[start_pos:end_pos].decode('utf-16-le')

            if e_type == 'MessageEntityTextUrl':
                return f"<a href=\"{entity['url_']}\">{extracted}</a>"
            elif e_type == 'MessageEntityBold':
                return f"<b>{extracted}</b>"
            elif e_type == 'MessageEntityItalic':
                return f"<i>{extracted}</i>"
            elif e_type == 'MessageEntityCode':
                return f"<code>{extracted}</code>"
            elif e_type == 'MessageEntityPre':
                return f"<pre>{extracted}</pre>"

            return None

        def collect(utf16: bytes, entities: dict) -> list:
            replacements = [(e, e['offset_'] * 2, (e['length_'] + e['offset_']) * 2) for e in entities.values()]
            replacements = [(convert(utf16, *r),) + r[1:] for r in replacements]
            replacements = sorted(
                [(r[0].encode('utf-16-le'),) + r[1:] for r in replacements if r[0] is not None],
                key=lambda r: r[1]
            )

            return replacements

        def combine(utf16: bytes, replacements: list) -> str:
            byte_array = bytearray()
            cur_pos = 0

            for replacement, start_pos, end_pos in replacements:
                byte_array += utf16[cur_pos:start_pos]
                byte_array += replacement
                cur_pos = end_pos

            return (byte_array + utf16[cur_pos:]).decode('utf-16-le')

        content = self.post_info.content
        if 'entities_' not in content:
            return text

        utf16bytes = text.encode('utf-16-le')
        replacements = collect(utf16bytes, content['entities_'])
        return combine(utf16bytes, replacements)

    def __get_type(self) -> str:
        if 'photo_' in self.post_info.content:
            return PostType.PHOTO

        return PostType.TEXT

    def __shorten_text(self, text: str, post_type: str) -> str:
        max_length = self.MAX_MESSAGE_LENGTH[post_type]

        if len(text) <= max_length:
            return text

        return text[:max_length - 3].strip() + '...'
