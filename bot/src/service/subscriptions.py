import logging

from sqlalchemy.exc import IntegrityError
from typing import List

from src.component.config import db, channel_repository, user_repository, subscription_repository
from src.domain.command import Command
from src.domain.entities import Channel
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
            user = user_repository.get_or_create(command.chat_id)
            channel = channel_repository.get_or_create(url=command.channel_url, name=command.channel_name)
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
            user = user_repository.get(command.chat_id)
            if user is None:
                raise NotSubscribedError()

            channel = channel_repository.get(command.channel_url)
            if channel is None:
                raise NotSubscribedError()

            has_sub = subscription_repository.has(user_id=user.id, channel_id=channel.id)
            if not has_sub:
                raise NotSubscribedError()

            subs_left = subscription_repository.remove(user_id=user.id, channel_id=channel.id)
            if subs_left == 0:
                channel_repository.remove(command.channel_url)

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
            user = user_repository.get(command.chat_id)
            if user is None:
                return []

            return subscription_repository.list(user.id)
        except:
            logging.exception("Failed to list subscriptions")
            raise SubscriptionsListError()
