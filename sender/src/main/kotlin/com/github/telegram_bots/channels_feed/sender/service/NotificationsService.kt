package com.github.telegram_bots.channels_feed.sender.service

import com.github.telegram_bots.channels_feed.sender.domain.User
import io.reactivex.Completable
import io.reactivex.Flowable
import org.davidmoten.rx.jdbc.Database
import org.springframework.stereotype.Service

@Service
class NotificationsService(private val db: Database) {
    fun listNotNotified(channelId: Int, postId: Int): Flowable<User> {
        return db
                .select(
                    """
                    | SELECT u.*
                    | FROM subscriptions AS s
                    | JOIN users AS u ON s.user_id = u.id
                    | JOIN channels AS c ON s.channel_id = c.id
                    | WHERE s.channel_id = :channel_id
                    | AND (c.last_sent_id IS NULL OR c.last_sent_id < :post_id)
                    | AND (s.last_sent_id IS NULL OR s.last_sent_id < :post_id)
                    """.trimMargin()
                )
                .parameter("channel_id", channelId)
                .parameter("post_id", postId)
                .get(::User)
    }

    fun markSubscription(userId: Int, channelId: Int, postId: Int): Completable {
        return db
                .update(
                    """
                    | UPDATE subscriptions
                    | SET last_sent_id = :post_id
                    | WHERE user_id = :user_id
                    | AND channel_id = :channel_id
                    | AND (last_sent_id IS NULL OR last_sent_id < :post_id)
                    """.trimMargin()
                )
                .parameter("user_id", userId)
                .parameter("channel_id", channelId)
                .parameter("post_id", postId)
                .complete()
    }

    fun markChannel(channelId: Int, postId: Int): Completable {
        return db
                .update(
                    """
                    | UPDATE channels
                    | SET last_sent_id = :post_id
                    | WHERE id = :channel_id
                    | AND (last_sent_id IS NULL OR last_sent_id < :post_id)
                    """.trimMargin()
                )
                .parameter("channel_id", channelId)
                .parameter("post_id", postId)
                .complete()
    }
}
