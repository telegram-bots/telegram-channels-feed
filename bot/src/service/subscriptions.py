from src.config import db, tg_cli, user_repository, channel_repository, subscription_repository


class Subscriptions:
    """
    Subscriptions management
    """
    def __init__(self):
        pass

    def subscribe(self, command):
        if command.channel_url is None:
            raise NameError('Invalid channel url!')

        channel = channel_repository.get(url=command.channel_url)
        if channel is None:
            channel_tg_id, channel_name = tg_cli.lookup_channel(command.channel_url)
            tg_cli.subscribe_to_channel(channel_tg_id)
            channel = channel_repository.create_or_update(
                tg_id=channel_tg_id,
                url=command.channel_url,
                name=channel_name
            )

        user = user_repository.get_or_create(telegram_id=command.chat_id)

        subscription_repository.create(user_id=user['id'], channel_id=channel['id'])

        return channel

    def unsubscribe(self, command):
        if command.channel_url is None:
            raise NameError('Invalid channel url!')

        user = user_repository.get(telegram_id=command.chat_id)
        if user is None:
            raise IndexError("No such user!")

        channel = channel_repository.get(command.channel_url)
        if channel is None:
            raise IndexError("No such channel!")

        subs_left = subscription_repository.remove(user_id=user['id'], channel_id=channel['id'])
        if subs_left == 0:
            tg_cli.unsubscribe_from_channel(channel['telegram_id'])
            channel_repository.remove(channel['id'])

        return channel

    def list(self, command):
        return subscription_repository.list(user_telegram_id=command.chat_id)

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
