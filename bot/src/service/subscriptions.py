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

    def get_subscription_data(self, channel_tg_id):
        return db.get_lazy(
            """
            SELECT
              ch.id AS channel_id,
              ch.telegram_id AS channel_tg_id,
              u.id AS user_id,
              u.telegram_id AS user_tg_id,
              sub.last_update AS sub_last_update,
              ch.last_update as ch_last_update
            FROM Channels AS ch
            JOIN Subscriptions AS sub ON sub.channel_id = ch.id
            JOIN Users AS u ON u.id = sub.user_id
            WHERE ch.telegram_id = %s
            """ % channel_tg_id
        )

    def __parse_channel_url(self, command):
        try:
            url = re.search('(?:.*)(?:t.me\/|@)(.*)', command.args[0]).group(1).strip()

            if url == '':
                raise NameError()

            return url
        except IndexError:
            raise NameError()
