from typing import Optional

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
