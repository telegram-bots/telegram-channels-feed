from src.config import db
from src.domain.entities import Channel
from typing import List


class ChannelRepository:
    def get(self, url: str) -> Channel:
        """
        Find channel by it's url
        :param url: Searchable url of channel
        :return: Found channel or None
        """
        return db.get_one(
            lambda cur: cur.execute("SELECT * FROM Channels WHERE url = %s", [url]),
            mapper=Channel
        )

    def create_or_update(self, telegram_id: int, url: str, name: str) -> Channel:
        """
        Creates channel or updates it's url and name if it already exists
        :param telegram_id: Telegram ID of channel
        :param url: URL of channel
        :param name: Name of channel
        :return: Existing or just updated channel
        """
        return db.get_one(
            lambda cur: cur.execute(
                """
                INSERT INTO Channels (telegram_id, url, name)
                VALUES (%(telegram_id)s, %(url)s, %(name)s)
                ON CONFLICT (telegram_id)
                DO UPDATE
                SET url = %(url)s, name = %(name)s;
                SELECT *
                FROM channels 
                WHERE telegram_id = %(telegram_id)s;
                """,
                {'telegram_id': telegram_id, 'url': url, 'name': name}
            ),
            mapper=Channel
        )

    def remove(self, url: str):
        """
        Remove channel by it's url if exists
        :param url: URL of channel
        """
        db.execute(lambda cur: cur.execute("DELETE FROM Channels WHERE url = %s", [url]))

    def list_subscribed(self, user_telegram_id: int) -> List[Channel]:
        """
        Get list of channels user subscribed to
        :param user_telegram_id: Telegram ID of user
        :rtype: List[Channel]
        :return: List of channels
        """
        return db.get_all(
            lambda cur: cur.execute(
                """
                SELECT ch.id, ch.telegram_id, ch.url, ch.name, ch.last_update
                FROM Subscriptions AS sub
                JOIN Users AS u ON u.id = sub.user_id
                JOIN Channels AS ch ON ch.id = sub.channel_id
                WHERE u.telegram_id = %s
                """,
                [user_telegram_id]
            ),
            mapper=Channel
        )
