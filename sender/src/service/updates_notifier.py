import json
import logging
import os
import os.path
from threading import Thread
from datetime import datetime
from urllib.parse import urlparse

from retry.api import retry_call

from src.config import config, encoding
from src.domain.post import PostType, PostInfo, Post
from src.domain.entities import Channel, User
from src.service.post_formatter import PostFormatter


class UpdatesNotifier:
    def __init__(self, notifications, queue_consumer):
        self.notifications = notifications
        self.queue_consumer = queue_consumer
        self.tg_cli_user = urlparse(config['tg-cli']['url']).username

    def instance(self, bot):
        def run():
            self.bot = bot
            self.message_route = {
                PostType.TEXT: self.bot.send_message,
                PostType.PHOTO: self.bot.send_photo
            }
            self.queue_consumer.run(on_message_callback=self.on_message)

        thread = Thread(target=run)
        thread.start()

        return self

    def on_message(self, mq_channel, basic_deliver, properties, body):
        def get_post_info(body):
            json_data = json.loads(body.decode(encoding))
            if json_data['ID'] == 'Message':
                return PostInfo(
                    channel_telegram_id=json_data['chat_id_'],
                    message_id=int(json_data['id_']),
                    date=datetime.fromtimestamp(json_data['date_']),
                    content=json_data['content_'],
                    update=False
                )
            elif json_data['ID'] == 'UpdateMessageContent':
                return PostInfo(
                    channel_telegram_id=json_data['chat_id_'],
                    message_id=int(json_data['message_id_']),
                    date=datetime.now(),
                    content=json_data['new_content_'],
                    update=True
                )

        def get_channel_info(channel_tg_id):
            channel = self.notifications.get_channel_info(channel_tg_id)
            if channel is None:
                channel = Channel()
                channel.id = -1
                channel.url = ""
                channel.name = "removed"

            return channel

        def format_post(channel: Channel, info: PostInfo):
            post = PostFormatter(channel, info).format()
            logging.debug(f"Formatted post: {post}")
            return post

        def get_callback(post: Post):
            if post.file_id is not False:
                return self.message_route[post.type]
            return self.bot.send_message

        def get_args(post: Post, user: User):
            args = {
                'text': post.text,
                'caption': post.text,
                'parse_mode': post.mode,
                'reply_markup': post.keyboard,
                'disable_web_page_preview': not post.preview_enabled,
                'chat_id': user.telegram_id if user.redirect_url is None else user.redirect_url
            }

            if post.file_id is not False:
                args[post.type] = post.file_id

            return args

        def upload_file(post: Post):
            def get_file_path(file_id: str):
                return os.path.join(os.sep, 'data', 'files', file_id)

            def remove_file(file_id: str):
                try:
                    os.remove(path)
                except OSError:
                    pass

            def download_file(file_id: str, to_path: str):
                file = self.bot.get_file(file_id=file_id)
                retry_call(
                    file.download,
                    fkwargs={'custom_path': to_path},
                    tries=5,
                    delay=5
                )

            def cache_file(path: str, post_type: str):
                result = retry_call(
                    self.message_route[post_type],
                    fkwargs={
                        'chat_id': self.tg_cli_user,
                        post_type: open(path, 'rb')
                    },
                    tries=5,
                    delay=5
                )
                return result[post_type][-1]['file_id']

            if post.type == PostType.TEXT or post.file_id is None:
                return False

            logging.info(f"Uploading file: {post.file_id}")
            path = get_file_path(post.file_id)

            try:
                download_file(post.file_id, path)
                file_id = cache_file(path, post.type)
                remove_file(path)

                return file_id
            except Exception as e:
                logging.warning(f"Failed to upload file: {e}")
                return False

        def send_post(channel: Channel, user: User, post: Post):
            logging.info(f"Sending channel {channel.id} content to user {user.id}")
            retry_call(
                callback,
                fkwargs=get_args(post, user),
                tries=5,
                delay=10
            )

        def mark_subscription(channel: Channel, user: User, info: PostInfo):
            logging.info(f"Setting subscription {user.id}:{channel.id} last_message_id to {info.message_id} ({info.date})")
            self.notifications.mark_subscription(
                user_id=user.id,
                channel_id=channel.id,
                message_id=info.message_id
            )

        def mark_channel(channel: Channel, info: PostInfo):
            logging.info(f"Setting channel {channel.id} last_message_id to {info.message_id} ({info.date})")
            self.notifications.mark_channel(
                info.channel_telegram_id,
                info.message_id
            )

        def acknowledge_message():
            logging.info(f"Acknowledging message #{basic_deliver.delivery_tag}")
            mq_channel.basic_ack(basic_deliver.delivery_tag)

        logging.info(f"Received message #{basic_deliver.delivery_tag}")
        logging.debug(f"From app {properties.app_id}: {body}")

        info = get_post_info(body)
        channel = get_channel_info(info.channel_telegram_id)
        post = format_post(channel, info)
        post.file_id = upload_file(post)
        callback = get_callback(post)
        has_errors = False

        for notify in self.notifications.list_not_notified(info.channel_telegram_id, info.message_id, info.update):
            try:
                send_post(channel, notify.user, post)
                mark_subscription(channel, notify.user, info)
            except:
                has_errors = True
                logging.exception("Failed to deliver message")
                continue

        if has_errors and not info.update:
            return

        mark_channel(channel, info)
        acknowledge_message()
