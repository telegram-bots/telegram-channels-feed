import logging
import json
from threading import Thread

from retry.api import retry_call
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.config import encoding
from src.domain.entities import User
from src.domain.post import Post, PostGroup


class UpdatesNotifier:
    def __init__(self, notifications, queue_consumer):
        self.notifications = notifications
        self.queue_consumer = queue_consumer
        self.bot = None

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

        def get_args(group: PostGroup, post: Post, user: User):
            chat_id = user.telegram_id if user.redirect_url is None else user.redirect_url

            if post.mode == "AS_IS":
                args = {
                    'chat_id': chat_id,
                    'from_chat_id': '@' + group.channel_url,
                    'message_id': group.post_id
                }
            else:
                args = {
                    'chat_id': chat_id,
                    'text': post.text,
                    'parse_mode': post.mode,
                    'reply_markup': make_keyboard(),
                    'disable_web_page_preview': not post.preview_enabled,
                }

            return args

        def get_callback(post: Post):
            if post.mode == "AS_IS":
                return self.bot.forward_message
            else:
                return self.bot.send_message

        def send_post(group: PostGroup, post: Post, user: User):
            logging.info(f"Sending channel {group.channel_id} content to user {user.id}")
            retry_call(
                get_callback(post),
                fkwargs=get_args(group, post, user),
                tries=5,
                delay=10
            )

        def mark_sub(group: PostGroup, user: User):
            logging.info(f"Setting subscription {user.id}:{group.channel_id} last_sent_id to {group.post_id})")
            self.notifications.mark_subscription(user.id, group.channel_id, group.post_id)

        def mark_channel(group: PostGroup):
            logging.info(f"Setting channel {group.channel_id} last_sent_id to {group.post_id})")
            self.notifications.mark_channel(group.channel_id, group.post_id)

        def ack_message():
            logging.info(f"Acknowledging message #{basic_deliver.delivery_tag}")
            mq_channel.basic_ack(basic_deliver.delivery_tag)

        logging.info(f"Received message #{basic_deliver.delivery_tag}")
        logging.debug(f"From app {properties.app_id}: {body}")

        has_errors = False
        group = PostGroup(json.loads(body, encoding=encoding))

        for notify in self.notifications.list_not_notified(group.channel_id, group.post_id, False):
            try:
                user = notify.user
                post = group.posts['FULL']  # User settings
                send_post(group, post, user)
                mark_sub(group, user)
            except:
                has_errors = True
                logging.exception("Failed to deliver message")
                continue

        if has_errors:
            return

        mark_channel(group)
        ack_message()
