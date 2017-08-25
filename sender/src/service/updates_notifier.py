import logging
import json
from threading import Thread
from urllib.parse import urlparse

from retry.api import retry_call
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.config import config, encoding
from src.domain.entities import User
from src.domain.post import Post, PostGroup


class UpdatesNotifier:
    def __init__(self, notifications, queue_consumer):
        self.notifications = notifications
        self.queue_consumer = queue_consumer
        self.tg_cli_user = urlparse(config['tg-cli']['url']).username

    def instance(self, bot):
        def run():
            self.bot = bot
            self.queue_consumer.run(on_message_callback=self.on_message)

        thread = Thread(target=run)
        thread.start()

        return self

    def on_message(self, mq_channel, basic_deliver, properties, body):
        def make_keyboard() -> InlineKeyboardMarkup:
            return InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    'Mark as read',
                    callback_data='mark'
                )
            ]])

        def get_args(post: Post, user: User):
            args = {
                'chat_id': user.telegram_id if user.redirect_url is None else user.redirect_url,
                'text': post.text,
                'caption': post.text,
                'parse_mode': post.mode,
                'reply_markup': make_keyboard(),
                'disable_web_page_preview': not post.preview_enabled,
                'photo': post.file_id
            }

            return args

        def get_callback(post: Post):
            if post.file_id is not None:
                return self.bot.send_photo
            else:
                return self.bot.send_message

        def send_post(channel_id: int, user: User, post: Post):
            logging.info(f"Sending channel {channel_id} content to user {user.id}")
            retry_call(
                get_callback(post),
                fkwargs=get_args(post, user),
                tries=5,
                delay=10
            )

        def mark_subscription(channel_id: int, message_id: int, user: User):
            logging.info(f"Setting subscription {user.id}:{channel_id} last_message_id to {message_id})")
            self.notifications.mark_subscription(user.id, channel_id, message_id)

        def mark_channel(channel_id: int, message_id: int):
            logging.info(f"Setting channel {channel_id} last_message_id to {message_id})")
            self.notifications.mark_channel(channel_id, message_id)

        def acknowledge_message():
            logging.info(f"Acknowledging message #{basic_deliver.delivery_tag}")
            mq_channel.basic_ack(basic_deliver.delivery_tag)

        logging.info(f"Received message #{basic_deliver.delivery_tag}")
        logging.debug(f"From app {properties.app_id}: {body}")

        has_errors = False
        post_group = PostGroup(json.loads(body, encoding=encoding))

        for notify in self.notifications.list_not_notified(post_group.channel_id, post_group.message_id, False):
            try:
                user = notify.user
                posts = post_group.posts['FULL']  # User settings
                for post in posts:
                    send_post(post_group.channel_id, user, post)
                if not has_errors:
                    mark_subscription(post_group.channel_id, post_group.message_id, user)
            except:
                has_errors = True
                logging.exception("Failed to deliver message")
                continue

        if has_errors:
            return

        mark_channel(post_group.channel_id, post_group.message_id)
        acknowledge_message()
