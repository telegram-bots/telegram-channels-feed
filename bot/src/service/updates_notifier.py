import json
import logging
from datetime import datetime

from retry.api import retry_call
from telegram.ext.dispatcher import run_async

from src.config import encoding
from src.domain.post import PostInfo
from src.service.post_formatter import PostFormatter


class UpdatesNotifier:
    def __init__(self, notifications, queue_consumer):
        self.notifications = notifications
        self.queue_consumer = queue_consumer

    @run_async
    def instance(self, bot):
        self.bot = bot
        self.queue_consumer.run(on_message_callback=self.on_message)

        return self

    def on_message(self, mq_channel, basic_deliver, properties, body):
        logging.info(f"Received message #{basic_deliver.delivery_tag}")
        logging.debug(f"From app {properties.app_id}: {body}")

        json_obj = json.loads(body.decode(encoding))
        info = PostInfo(
            channel_telegram_id=json_obj['chat_id_'],
            message_id=json_obj['id_'],
            date=datetime.fromtimestamp(json_obj['date_']),
            raw=json_obj
        )
        channel = self.notifications.get_channel_info(info.channel_telegram_id)
        post = PostFormatter(channel, info).format()
        has_errors = False

        logging.debug(f"Formatted post: {post}")

        for notify in self.notifications.list_not_notified(info.channel_telegram_id, info.message_id):
            try:
                user = notify.user

                logging.info(f"Sending channel {channel.id} content to user {user.id}")
                retry_call(
                    self.bot.send_message,
                    fkwargs={
                        'chat_id': user.telegram_id,
                        'text': post.text,
                        'parse_mode': post.type,
                        'reply_markup': post.keyboard,
                        'disable_web_page_preview': not post.preview_enabled
                    },
                    tries=5,
                    delay=10
                )

                logging.info(f"Setting subscription {user.id}:{channel.id} last_message_id to {info.message_id} ({info.date})")
                self.notifications.mark_subscription(
                    user_id=user.id,
                    channel_id=channel.id,
                    message_id=info.message_id
                )
            except Exception as e:
                has_errors = True
                logging.error(f"Failed to deliver message: {e}")
                continue

        if has_errors:
            return

        logging.info(f"Setting channel {channel.id} last_message_id to {info.message_id} ({info.date})")
        self.notifications.mark_channel(
            info.channel_telegram_id,
            info.message_id
        )

        logging.info(f"Acknowledging message #{basic_deliver.delivery_tag}")
        mq_channel.basic_ack(basic_deliver.delivery_tag)
