package com.github.telegram_bots.channels_feed.tg.service

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Completable
import io.reactivex.Flowable
import org.davidmoten.rx.jdbc.Database
import org.springframework.stereotype.Repository

@Repository
class ChannelRepository(private val db: Database) {
    fun update(channel: Channel): Completable {
        return db
                .update(
                        """
                        | UPDATE channels
                        | SET telegram_id = ?, hash = ?, url = ?, name = ?, created_at = to_timestamp(?),
                        | last_post_id = CASE WHEN ? > last_post_id OR last_post_id IS NULL THEN ? ELSE last_post_id END
                        | WHERE id = ?
                        """.trimMargin()
                )
                .parameters(
                        channel.telegramId,
                        channel.hash,
                        channel.url,
                        channel.name,
                        channel.createdAt.epochSecond,
                        channel.lastPostId,
                        channel.lastPostId,
                        channel.id
                )
                .complete()
    }

    fun list(): Flowable<Channel> {
        return db.select("""SELECT * FROM channels ORDER BY last_post_id DESC""").get(::Channel)
    }

    fun listNeedToUpdate(): Flowable<Channel> {
        return db
                .select(
                        """
                        | SELECT * FROM channels
                        | WHERE extract(DAY FROM created_at) = extract(DAY FROM now())
                        | AND extract(MONTH FROM created_at) != extract(MONTH FROM now())
                        """.trimMargin()
                )
                .get(::Channel)
    }
}
