import logging
import re

from src.config import db, tg_cli


class Subscriptions:
    """
    Subscriptions management
    """
    def __init__(self):
        pass

    def subscribe(self, command):
        user_telegram_id = command.chat_id
        channel_url = self.__parse_channel_url(command)
        channel_telegram_id, channel_name = tg_cli.lookup_channel(channel_url)
        tg_cli.subscribe_to_channel(channel_telegram_id)

        # SQL HERE

        return channel_name

    def unsubscribe(self, command):
        user_telegram_id = command.chat_id
        channel_id = int(command.args[0])

        # SQL HERE

        if True: # TODO Если это был последний пользователь, который был подписан на этот канал
            tg_cli.unsubscribe_from_channel(channel_id)

        return "TODO. Channel name from DB"

    def list_subscriptions(self, command):
        user_telegram_id = command.chat_id

        # return [(channel_name 1, channel_id 1), (channel_name 1, channel_id 1), ... (channel_name N, channel_id N))

    def list_subscribers(self, channel_tg_id):
        conn = db.connection()
        cur = conn.cursor()

        cur.execute("""
                    SELECT * FROM Users WHERE id IN (
                      SELECT user_id FROM Subscriptions WHERE channel_id = (
                        SELECT id FROM Channels WHERE telegram_id = %s
                      )
                    )""",
                    [channel_tg_id])

        return cur.fetchall()

    def __parse_channel_url(self, command):
        try:
            url = re.search('(?:.*)(?:t.me\/|@)(.*)', command.args[0]).group(1).strip()

            if url == '':
                raise NameError()

            return url
        except IndexError:
            raise NameError()
