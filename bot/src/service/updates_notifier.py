import json
import logging

from datetime import datetime
from retry import retry
from telegram.error import NetworkError
from telegram.ext.dispatcher import run_async
from src.config import encoding
from src.domain.post import Post
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
        logging.debug(f"Received message #{basic_deliver.delivery_tag} from {properties.app_id}: {body}")

        json_obj = json.loads(body.decode(encoding))
        channel_telegram_id = json_obj['chat_id_']
        timestamp = datetime.fromtimestamp(json_obj['date_'])
        channel = self.notifications.get_channel_info(channel_telegram_id)
        post = PostFormatter(channel, json_obj).format()
        has_errors = False

        for notify in self.notifications.list_not_notified(channel_telegram_id, timestamp):
            try:
                user = notify.user

                logging.debug(f"Sending channel {channel.id} content to user {user.id}")
                self.__send_message(chat_id=user.telegram_id, post=post)

                logging.debug(f"Marking subscription {user.id}:{channel.id} as updated at {timestamp}")
                self.notifications.mark_subscription(
                    user_id=user.id,
                    channel_id=channel.id,
                    timestamp=timestamp
                )
            except Exception as e:
                has_errors = True
                logging.error(f"Failed to deliver message: {e}")
                continue

        if has_errors:
            return

        logging.debug(f"Marking channel {channel.id} as updated at {timestamp}")
        self.notifications.mark_channel(
            channel_telegram_id=channel_telegram_id,
            timestamp=timestamp
        )

        logging.debug(f"Acknowledging message #{basic_deliver.delivery_tag}")
        mq_channel.basic_ack(basic_deliver.delivery_tag)

    @retry(NetworkError, tries=5, delay=10)
    def __send_message(self, chat_id: int, post: Post):
        self.bot.sendMessage(
            chat_id=chat_id,
            text=post.text,
            parse_mode=post.type,
            reply_markup=post.keyboard,
            disable_web_page_preview=not post.preview_enabled
        )
