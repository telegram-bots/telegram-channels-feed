from typing import Optional
from sqlalchemy.sql import text
from src.component.config import db
from src.domain.entities import Channel


class ChannelRepository:
    def get(self, url: str) -> Optional[Channel]:
        """
        Get user if exists
        :param url: URL of channel
        :return: Existing user or None
        """
        return db.session \
            .query(Channel) \
            .from_statement(text("""SELECT * FROM channels WHERE url = :url""")) \
            .params(url=url) \
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
                INSERT INTO channels (url, name)
                VALUES (:url, :name)
                ON CONFLICT (url) DO NOTHING;
                SELECT * FROM channels WHERE url = :url;
                """
            )) \
            .params(url=url, name=name) \
            .first()

    def remove(self, url: str) -> bool:
        """
        Remove channel by it's url if exists
        :param url: URL of channel
        :rtype: bool
        :return: Delete successful or not
        """
        return db.session \
            .execute(text("""DELETE FROM channels WHERE url = :url"""), {'url': url}) \
            .rowcount > 0
