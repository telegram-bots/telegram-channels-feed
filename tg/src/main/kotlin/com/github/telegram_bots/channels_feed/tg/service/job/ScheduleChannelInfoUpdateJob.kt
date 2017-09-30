package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Completable
import io.reactivex.functions.Function

class ScheduleChannelInfoUpdateJob(private val repository: ChannelRepository) : Function<Channel, Completable> {
    override fun apply(channel: Channel): Completable {
        return repository.update(channel.copy(hash = Channel.EMPTY_HASH))
    }
}
