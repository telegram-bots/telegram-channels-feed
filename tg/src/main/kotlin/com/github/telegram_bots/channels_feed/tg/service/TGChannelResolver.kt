package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.TelegramClient
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.job.SubscribeChannelJob
import com.github.telegram_bots.channels_feed.tg.service.job.UnsubscribeChannelJob
import io.reactivex.Single
import org.springframework.stereotype.Service

@Service
class TGChannelResolver(
        private val client: TelegramClient,
        private val repository: ChannelRepository
) {
    fun subscribe(channelUrl: String): Single<Channel> {
        return Single.fromCallable(SubscribeChannelJob(client, repository, channelUrl))
                .flatMap { it }
    }

    fun unsubscribe(channelUrl: String): Single<Boolean> {
        return Single.fromCallable(UnsubscribeChannelJob(repository, channelUrl))
                .flatMap { it }
    }
}
