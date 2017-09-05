from typing import Optional
from sqlalchemy.sql import text
from src.component.config import db
from src.domain.entities import Channel


class ChannelRepository:
    def get(self, url: str) -> Optional[Channel]:
        return db.session \
            .query(Channel) \
            .filter(Channel.url == url) \
            .first()

    def get_or_create(self, url: str, name: str) -> Channel:
        """
        Creates channel or returns existing
        :param url: URL of channel
        :param name: Name of channel
        :return: Existing or new channel
        """
        return db.session \
            .query(Channel) \
            .from_statement(text(
                """
                INSERT INTO Channels (url, name)
                VALUES (:url, :name)
                ON CONFLICT (url)
                DO NOTHING;
                SELECT *
                FROM channels 
                WHERE url = :url;
                """
            )) \
            .params(url=url, name=name) \
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
