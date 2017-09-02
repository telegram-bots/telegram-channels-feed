package com.github.telegram_bots.channels_feed.tg.rest

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.TGChannelResolver
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1")
class APIController(private val resolver: TGChannelResolver) {
    @RequestMapping("channel/sub/{url}")
    fun subscribe(@PathVariable channelUrl: String): ResponseEntity<Channel> {
        return resolver.subscribe(channelUrl)
                .map { ResponseEntity.ok(it) }
                .blockingGet()
    }

    @RequestMapping("channel/unsub/{url}")
    fun unsubsribe(@PathVariable channelUrl: String): ResponseEntity<Boolean> {
        return resolver.unsubscribe(channelUrl)
                .map { ResponseEntity.ok(it) }
                .blockingGet()
    }
}
