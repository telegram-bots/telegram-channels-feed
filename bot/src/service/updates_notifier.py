import json
import logging

from datetime import datetime
from retry import retry
from telegram.error import NetworkError
from telegram.ext.dispatcher import run_async
from src.config import encoding


class UpdatesNotifier:
    def __init__(self, notifications, queue_consumer, post_formatter):
        self.notifications = notifications
        self.queue_consumer = queue_consumer
        self.post_formatter = post_formatter

    @run_async
    def instance(self, bot):
        self.bot = bot
        self.queue_consumer.run(on_message_callback=self.on_message)

        return self

    def on_message(self, channel, basic_deliver, properties, body):
        logging.debug(f"Received message #{basic_deliver.delivery_tag} from {properties.app_id}: {body}")

        json_obj = json.loads(body.decode(encoding))
        text_type, formatted_text = self.post_formatter.format(json_obj)
        channel_telegram_id = json_obj['chat_id_']
        timestamp = datetime.fromtimestamp(json_obj['date_'])

        for notify in self.notifications.list_not_notified(channel_telegram_id, timestamp):
            try:
                logging.debug(f"Sending channel {notify.channel.id} content to user {notify.user.id}")
                self.__send_message(
                    chat_id=notify.user.telegram_id,
                    text=formatted_text,
                    text_type=text_type
                )

                logging.debug(f"Marking subscription {notify.user.id}:{notify.channel.id} as updated at {timestamp}")
                self.notifications.mark_subscription(
                    user_id=notify.user.id,
                    channel_id=notify.channel.id,
                    timestamp=timestamp
                )
            except:
                raise

        logging.debug(f"Marking channel {channel_telegram_id} as updated at {timestamp}")
        self.notifications.mark_channel(
            channel_telegram_id=channel_telegram_id,
            timestamp=timestamp
        )

        logging.debug(f"Acknowledging message #{basic_deliver.delivery_tag}")
        channel.basic_ack(basic_deliver.delivery_tag)

    @retry(NetworkError, tries=5, delay=10)
    def __send_message(self, chat_id, text, text_type):
        self.bot.sendMessage(chat_id=chat_id, text=text, parse_mode=text_type)
