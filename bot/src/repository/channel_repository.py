from sqlalchemy import or_
from sqlalchemy.sql import text
from typing import List, Optional

from src.config import db
from src.domain.entities import Channel


class ChannelRepository:
    def get(self, url: str=None, telegram_id: int=None) -> Optional[Channel]:
        """
        Find channel by it's url
        :param url: Searchable url of channel
        :param telegram_id: Searchable telegram_id of channel
        :return: Found channel or None
        """
        if url is None and telegram_id is None:
            raise AttributeError("Both url and telegram_id is None")

        query = db.session.query(Channel)

        if url is not None:
            return query.filter(Channel.url == url).first()
        elif telegram_id is not None:
            return query.filter(Channel.telegram_id == telegram_id).first()

    def create_or_update(self, telegram_id: int, url: str, name: str) -> Channel:
        """
        Creates channel or updates it's url and name if it already exists
        :param telegram_id: Telegram ID of channel
        :param url: URL of channel
        :param name: Name of channel
        :return: Existing or just updated channel
        """
        return db.session \
            .query(Channel) \
            .from_statement(text(
                """
                INSERT INTO Channels (telegram_id, url, name)
                VALUES (:telegram_id, :url, :name)
                ON CONFLICT (telegram_id)
                DO UPDATE
                SET url = :url, name = :name;
                SELECT *
                FROM channels 
                WHERE telegram_id = :telegram_id;
                """
            )) \
            .params(telegram_id=telegram_id, url=url, name=name) \
            .first()

    def remove(self, url: str):
        """
        Remove channel by it's url if exists
        :param url: URL of channel
        """
        db.session \
            .query(Channel) \
            .filter(Channel.url == url) \
            .delete()

    def list_subscribed(self, user_telegram_id: int) -> List[Channel]:
            """
            Get list of channels user subscribed to
            :param user_telegram_id: Telegram ID of user
            :rtype: List[Channel]
            :return: List of channels
            """
            return db.session \
                .query(Channel) \
                .from_statement(text(
                    """
                    SELECT ch.id, ch.telegram_id, ch.url, ch.name, ch.last_message_id
                    FROM Subscriptions AS sub
                    JOIN Users AS u ON u.id = sub.user_id
                    JOIN Channels AS ch ON ch.id = sub.channel_id
                    WHERE u.telegram_id = :user_telegram_id
                    """
                )) \
                .params(user_telegram_id=user_telegram_id) \
                .all()

    def set_message_id(self, telegram_id: int, message_id: int):
        db.session \
            .query(Channel) \
            .filter(Channel.telegram_id == telegram_id) \
            .filter(or_(Channel.last_message_id < message_id, Channel.last_message_id == None)) \
            .update({Channel.last_message_id: message_id})
