import json
import logging

import pprint
from datetime import datetime
from retry import retry
from telegram.error import NetworkError
from src.config import encoding


class UpdatesNotifier:
    def __init__(self, notifications, queue_consumer):
        self.notifications = notifications
        self.queue_consumer = queue_consumer

    def instance(self, bot):
        self.bot = bot
        self.queue_consumer.run(on_message_callback=self.on_message)

        return self

    def on_message(self, channel, basic_deliver, properties, body):
        logging.debug(f"Received message # {basic_deliver.delivery_tag} from {properties.app_id}: {body}")

        data = json.loads(body.decode(encoding))
        channel_telegram_id = data['chat_id_']
        timestamp = datetime.fromtimestamp(data['date_'])

        for notify in self.notifications.list_not_notified(channel_telegram_id, timestamp):
            try:
                logging.debug(f"Sending channel {notify.channel.id} content to user {notify.user.id}")
                self.__send_message(chat_id=notify.user.telegram_id, data=data)

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

        logging.debug(f"Acknowledging message {basic_deliver.delivery_tag}")
        channel.basic_ack(basic_deliver.delivery_tag)

    @retry(NetworkError, tries=5, delay=10)
    def __send_message(self, chat_id, data):
        self.bot.send_message(chat_id=chat_id, text=pprint.pformat(data, indent=4))
