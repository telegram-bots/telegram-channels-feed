from src.config import db


class ChannelRepository:
    def __init__(self):
        self.conn = db.connection()

    def get(self, url: str) -> dict:
        """
        Find channel by it's url
        :param url: Searchable url of channel
        :return: Found channel or None
        """
        return db.get_one("SELECT * FROM Channels WHERE url = '%s'" % url)

    def create_or_update(self, tg_id: int, url: str, name: str) -> dict:
        """
        Creates channel or updates it's url and name if it already exists
        :param tg_id: Telegram ID of channel
        :param url: URL of channel
        :param name: Name of channel
        :return: Existing or just updated channel
        """
        return db.execute_and_get(lambda cur: cur.execute(
            """
            INSERT INTO Channels (telegram_id, url, name)
            VALUES (%(tg_id)s, %(url)s, %(name)s)
            ON CONFLICT (telegram_id)
            DO UPDATE
            SET url = %(url)s, name = %(name)s;
            SELECT *
            FROM channels 
            WHERE telegram_id = %(tg_id)s;
            """,
            {'tg_id': tg_id, 'url': url, 'name': name}
        ))

    def remove(self, url: str):
        """
        Remove channel by it's url if exists
        :param url: URL of channel
        """
        db.execute(lambda cur: cur.execute("DELETE FROM Channels WHERE url = '%s'" % url))
