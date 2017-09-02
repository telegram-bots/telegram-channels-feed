package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Single
import io.reactivex.rxkotlin.toSingle
import java.util.concurrent.Callable

class UpdateChannelLastPostIDJob(
        private val repository: ChannelRepository,
        private val channel: Channel,
        private val lastPostId: Int
) : Callable<Single<Channel>> {
    override fun call(): Single<Channel> {
        val success = repository.updateLastPostId(channel.id, lastPostId)
        return if (success) channel.copy(lastPostId = lastPostId).toSingle()
            else Single.error(FailedToUpdatePostIdException(lastPostId, channel))
    }

    class FailedToUpdatePostIdException(postId: Int, channel: Channel) :
            RuntimeException("Failed to update postId $postId for channel $channel")
}
