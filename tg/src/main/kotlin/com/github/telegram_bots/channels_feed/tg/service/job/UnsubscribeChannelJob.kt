package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Single
import io.reactivex.rxkotlin.toSingle
import java.util.concurrent.Callable

class UnsubscribeChannelJob(
        private val repository: ChannelRepository,
        private val channelUrl: String
) : Callable<Single<Boolean>> {
    override fun call() = resolve(channelUrl).let(this::delete).toSingle()

    private fun resolve(channelUrl: String) = repository.find(channelUrl)

    private fun delete(channel: Channel?) = channel?.let(repository::delete) ?: false
}
