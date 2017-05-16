from datetime import datetime
from sqlalchemy.sql import text
from typing import List, Optional

from src.config import db
from src.domain.entities import Channel


class ChannelRepository:
    def get(self, url: str) -> Optional[Channel]:
        """
        Find channel by it's url
        :param url: Searchable url of channel
        :return: Found channel or None
        """
        return db.session \
            .query(Channel) \
            .filter(Channel.url == url) \
            .first()

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
                    SELECT ch.id, ch.telegram_id, ch.url, ch.name, ch.last_update
                    FROM Subscriptions AS sub
                    JOIN Users AS u ON u.id = sub.user_id
                    JOIN Channels AS ch ON ch.id = sub.channel_id
                    WHERE u.telegram_id = :user_telegram_id
                    """
                )) \
                .params(user_telegram_id=user_telegram_id) \
                .all()

    def set_timestamp(self, telegram_id: int, timestamp: datetime):
        db.session \
            .query(Channel) \
            .filter(Channel.telegram_id == telegram_id) \
            .update({Channel.last_update: timestamp})
