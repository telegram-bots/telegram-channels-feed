from sqlalchemy import or_
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload
from typing import Generator

from src.component.config import db
from src.domain.entities import Subscription, Channel


class Notifications:
    def list_not_notified(self, channel_id: int, post_id: int) -> Generator[Subscription, None, None]:
        query = db.session \
            .query(Subscription) \
            .options(joinedload(Subscription.user)) \
            .join(Subscription.channel) \
            .filter(Channel.id == channel_id) \
            .filter(or_(Channel.last_sent_id == None, Channel.last_sent_id < post_id)) \
            .filter(or_(Subscription.last_sent_id == None, Subscription.last_sent_id < post_id))

        return db.get_lazy(query)

    def mark_subscription(self, user_id: int, channel_id: int, post_id: int):
        db.session.execute(
            text(
                """
                UPDATE subscriptions
                SET last_sent_id = :post_id
                WHERE user_id = :user_id
                AND channel_id = :channel_id
                AND (last_sent_id IS NULL OR last_sent_id < :post_id)
                """
            ),
            {'post_id': post_id, 'user_id': user_id, 'channel_id': channel_id}
        )

        db.session.commit()

    def mark_channel(self, channel_id: int, post_id: int):
        db.session.execute(
            text(
                """
                UPDATE channels
                SET last_sent_id = :post_id
                WHERE id = :channel_id
                AND (last_sent_id IS NULL OR last_sent_id < :post_id)
                """
            ),
            {'post_id': post_id, 'channel_id': channel_id}
        )

        db.session.commit()
