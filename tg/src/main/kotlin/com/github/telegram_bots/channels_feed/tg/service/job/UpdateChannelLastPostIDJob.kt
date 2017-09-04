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
    override fun call() = repository.update(channel.copy(lastPostId = lastPostId)).toSingle()
}
