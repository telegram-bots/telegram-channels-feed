import logging
import html
from src.domain.post import Post
from src.domain.entities import Channel
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.parsemode import ParseMode


class PostFormatter:
    """
    Formats a telegram message into text representation.
    Supported text types: MARKDOWN, HTML, None (plain text)
    """
    MAX_MESSAGE_LENGTH = 4096

    def __init__(self, channel: Channel, json_obj):
        self.channel = channel
        self.json_obj = json_obj

    def format(self) -> Post:
        """
        Format a json_object into text representation.
        :return: Text type ('html', 'markdown', None) and formatted json_object as str
        """
        has_links, text = self.__make_text()

        logging.debug(f"Formatted post: {text}")

        return Post(
            text=text,
            type=ParseMode.HTML,
            keyboard=self.__make_keyboard(),
            preview_enabled=has_links
        )

    def __make_keyboard(self):
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(
                'Source',
                url=f"https://t.me/{self.channel.url}/{self.json_obj['id_']}"
            )
        ]])

    def __make_text(self):
        first_link = self.__extract_first_link()
        header = self.__generate_header()
        text = self.__extract_text()

        return first_link != "", self.__shorten_text(first_link + header + text)

    def __generate_header(self) -> str:
        return f"<b>new in</b> <a href=\"https://t.me/{self.channel.url}\">{html.escape(self.channel.name)}</a>"

    def __extract_text(self) -> str:
        text = None

        if 'text_' in self.json_obj['content_']:
            text = self.json_obj['content_']['text_']
        elif 'caption_' in self.json_obj['content_']:
            text = self.json_obj['content_']['caption_']

        return "\n\n" + html.escape(text) if text is not None and text is not False else ""

    def __extract_first_link(self) -> str:
        link = None

        if 'photo_' in self.json_obj['content_']:
            photos = self.json_obj['content_']['photo_']['sizes_']
            for k in sorted(photos, reverse=True):
                link = photos[k]['photo_']['persistent_id_']
                break
        elif 'entities_' in self.json_obj['content_']:
            entities = self.json_obj['content_']['entities_']
            for entity in entities.values():
                if entity['ID'] == 'MessageEntityUrl':
                    offset = entity['offset_']
                    length = entity['length_']
                    link = self.json_obj['content_']['text_'][offset:length + offset]
                    break

        return f"<a href=\"{html.escape(link)}\">\xad</a>" if link is not None else ""

    def __shorten_text(self, text) -> str:
        if len(text) <= self.MAX_MESSAGE_LENGTH:
            return text

        return text[:self.MAX_MESSAGE_LENGTH - 6].strip() + ' [...]'
