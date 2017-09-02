package com.github.telegram_bots.channels_feed.tg.rest

import com.github.badoualy.telegram.api.TelegramClient
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import com.github.telegram_bots.channels_feed.tg.service.job.SubscribeChannelJob
import com.github.telegram_bots.channels_feed.tg.service.job.UnsubscribeChannelJob
import io.reactivex.Single
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1")
class APIController(
        private val client: TelegramClient,
        private val repository: ChannelRepository
) {
    @RequestMapping("channel/sub/{url}")
    fun subscribe(@PathVariable channelUrl: String): ResponseEntity<Channel> {
        return Single.fromCallable(SubscribeChannelJob(client, repository, channelUrl))
                .flatMap { it }
                .map { ResponseEntity.ok(it) }
                .blockingGet()
    }

    @RequestMapping("channel/unsub/{url}")
    fun unsubsribe(@PathVariable channelUrl: String): ResponseEntity<Boolean> {
        return Single.fromCallable(UnsubscribeChannelJob(repository, channelUrl))
                .flatMap { it }
                .map { ResponseEntity.ok(it) }
                .blockingGet()
    }
}
