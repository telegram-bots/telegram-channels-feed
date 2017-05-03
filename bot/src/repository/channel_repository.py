from src.config import db


class ChannelRepository:
    def __init__(self):
        self.conn = db.connection()

    def get(self, url):
        return db.get_one("SELECT * FROM Channels WHERE url = '%s'" % url)

    def create_or_update(self, tg_id, url, name):
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

    def remove(self, id_):
        db.execute("DELETE FROM Channels WHERE id = %s" % id_)
