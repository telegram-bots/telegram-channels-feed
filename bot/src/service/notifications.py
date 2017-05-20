from typing import Generator
from datetime import datetime
from src.config import db, channel_repository, subscription_repository
from src.domain.entities import Subscription


class Notifications:
    def list_not_notified(self, channel_telegram_id: int, timestamp: datetime) -> Generator[Subscription, None, None]:
        return subscription_repository.all(channel_telegram_id, timestamp)

    def mark_subscription(self, user_id: int, channel_id: int, timestamp: datetime):
        subscription_repository.set_timestamp(user_id, channel_id, timestamp)
        db.session.commit()

    def mark_channel(self, channel_telegram_id: int, timestamp: datetime):
        channel_repository.set_timestamp(channel_telegram_id, timestamp)
        db.session.commit()
