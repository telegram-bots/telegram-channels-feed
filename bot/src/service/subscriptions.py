import logging

from sqlalchemy.exc import IntegrityError
from typing import Generator
from typing import List

from src.config import db, tg_cli, user_repository, channel_repository, subscription_repository
from src.domain.command import Command
from src.domain.entities import Channel, Subscription
from src.exception.subscription_exception import *


class Subscriptions:
    """
    Subscriptions management
    """
    def __init__(self):
        pass

    def subscribe(self, command: Command) -> Channel:
        """
        Handle subscription request
        :param command: Command entity
        :return Channel data
        """
        if command.channel_url is None:
            raise IllegalChannelUrlError()

        def callback():
            user = user_repository.get_or_create(telegram_id=command.chat_id)

            channel = channel_repository.get(command.channel_url)
            if channel is None:
                telegram_id, name = tg_cli.lookup_channel(command.channel_url)
                tg_cli.subscribe_to_channel(telegram_id)
                channel = channel_repository.create_or_update(
                    telegram_id=telegram_id,
                    url=command.channel_url,
                    name=name
                )

            subscription_repository.create(user_id=user.id, channel_id=channel.id)

            return channel

        try:
            return db.execute_in_transaction(callback)
        except IntegrityError:
            raise AlreadySubscribedError()
        except Exception as e:
            logging.error(f"Failed to subscribe: {e}")
            raise SubscribeError()

    def unsubscribe(self, command: Command) -> Channel:
        """
        Handle unsubscription request
        :param command: Command entity
        :return Channel data
        """
        if command.channel_url is None:
            raise IllegalChannelUrlError()

        def callback():
            user = user_repository.get(telegram_id=command.chat_id)
            if user is None:
                raise NotSubscribedError()

            channel = channel_repository.get(command.channel_url)
            if channel is None:
                raise NotSubscribedError()

            subs_left = subscription_repository.remove(user_id=user.id, channel_id=channel.id)
            if subs_left == 0:
                tg_cli.lookup_channel(channel.url)
                tg_cli.unsubscribe_from_channel(channel.telegram_id)
                channel_repository.remove(channel.url)

            return channel

        try:
            return db.execute_in_transaction(callback)
        except UnsubscribeError:
            raise
        except Exception as e:
            logging.error(f"Failed to unsubscribe: {e}")
            raise UnsubscribeError()

    def list(self, command: Command) -> List[Channel]:
        """
        Handle channels list request
        :param command: Command entity
        :return: List of channels user subscribed to
        """
        try:
            return channel_repository.list_subscribed(user_telegram_id=command.chat_id)
        except Exception as e:
            logging.error(f"Failed to list subscriptions: {e}")
            raise SubscriptionsListError()

    def all(self, channel_telegram_id: int) -> Generator[Subscription, None, None]:
        return subscription_repository.all(channel_telegram_id)
