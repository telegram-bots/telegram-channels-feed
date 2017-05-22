from typing import Generator, Optional

from src.config import db, channel_repository, subscription_repository
from src.domain.entities import Subscription, Channel


class Notifications:
    def get_channel_info(self, channel_telegram_id) -> Optional[Channel]:
        return channel_repository.get(telegram_id=channel_telegram_id)

    def list_not_notified(self, channel_telegram_id: int, message_id: int) -> Generator[Subscription, None, None]:
        return subscription_repository.all(channel_telegram_id, message_id)

    def mark_subscription(self, user_id: int, channel_id: int, message_id: int):
        subscription_repository.set_message_id(user_id, channel_id, message_id)
        db.session.commit()

    def mark_channel(self, channel_telegram_id: int, message_id: int):
        channel_repository.set_message_id(channel_telegram_id, message_id)
        db.session.commit()
