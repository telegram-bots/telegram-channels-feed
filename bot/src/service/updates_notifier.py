import json
import logging
import os
import os.path
from datetime import datetime

from retry.api import retry_call
from telegram.ext.dispatcher import run_async

from src.config import config, encoding
from src.domain.post import PostType, PostInfo
from src.service.post_formatter import PostFormatter


class UpdatesNotifier:
    def __init__(self, notifications, queue_consumer):
        self.notifications = notifications
        self.queue_consumer = queue_consumer
        self.tg_cli_id = config['tg-cli']['id']

    @run_async
    def instance(self, bot):
        self.bot = bot
        self.message_route = {
            PostType.TEXT: self.bot.send_message,
            PostType.PHOTO: self.bot.send_photo
        }
        self.queue_consumer.run(on_message_callback=self.on_message)

        return self

    def on_message(self, mq_channel, basic_deliver, properties, body):
        logging.info(f"Received message #{basic_deliver.delivery_tag}")
        logging.debug(f"From app {properties.app_id}: {body}")

        json_obj = json.loads(body.decode(encoding))
        info = PostInfo(
            channel_telegram_id=json_obj['chat_id_'],
            message_id=int(json_obj['id_']),
            date=datetime.fromtimestamp(json_obj['date_']),
            raw=json_obj
        )
        channel = self.notifications.get_channel_info(info.channel_telegram_id)
        post = PostFormatter(channel, info).format()
        has_errors = False

        logging.debug(f"Formatted post: {post}")

        callback = self.bot.send_message
        args = {
            'text': post.text,
            'caption': post.text,
            'parse_mode': post.mode,
            'reply_markup': post.keyboard,
            'disable_web_page_preview': not post.preview_enabled
        }

        if post.type != PostType.TEXT and post.file_id is not None:
            logging.info(f"Uploading file: {post.file_id}")
            path = os.path.join(os.sep, 'data', 'files', post.file_id)

            try:
                file = self.bot.get_file(file_id=post.file_id)
                retry_call(
                    file.download,
                    fkwargs={'custom_path': path},
                    tries=3,
                    delay=10
                )

                result = retry_call(
                    self.message_route[post.type],
                    fkwargs={
                        'chat_id': self.tg_cli_id,
                        post.type: open(path, 'rb')
                    },
                    tries=3,
                    delay=10
                )

                cached_file_id = result[post.type][-1]['file_id']
                callback = self.message_route[post.type]
                args[post.type] = cached_file_id
            except Exception as e:
                logging.warn(f"Failed to upload file: {e}")

        for notify in self.notifications.list_not_notified(info.channel_telegram_id, info.message_id):
            try:
                user = notify.user

                logging.info(f"Sending channel {channel.id} content to user {user.id}")
                args['chat_id'] = user.telegram_id
                retry_call(
                    callback,
                    fkwargs=args,
                    tries=5,
                    delay=10
                )

                logging.info(f"Setting subscription {user.id}:{channel.id} last_message_id to {info.message_id} ({info.date})")
                self.notifications.mark_subscription(
                    user_id=user.id,
                    channel_id=channel.id,
                    message_id=info.message_id
                )
            except:
                has_errors = True
                logging.exception(f"Failed to deliver message")
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
