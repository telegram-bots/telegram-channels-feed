package com.github.telegram_bots.channels_feed.tg.service.jobs

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Observable
import java.util.concurrent.Callable

class UpdateChannelLastPostIDJob(
        private val repository: ChannelRepository,
        private val channel: Channel,
        private val lastPostId: Int
) : Callable<Observable<Channel>> {
    override fun call(): Observable<Channel> {
        val result = repository.updateLastPostId(channel.telegramId, lastPostId)
        return if (!result) Observable.error { FailedToUpdatePostIdException(lastPostId, channel) }
        else Observable.just(channel)
    }

    class FailedToUpdatePostIdException(postId: Int, channel: Channel) :
            RuntimeException("Failed to update postId $postId for channel $channel")
}
