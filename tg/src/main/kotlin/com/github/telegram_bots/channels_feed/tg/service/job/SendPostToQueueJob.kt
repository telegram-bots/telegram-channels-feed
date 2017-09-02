package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import io.reactivex.Observable
import io.reactivex.Single
import org.springframework.cloud.stream.messaging.Source
import org.springframework.messaging.support.MessageBuilder
import java.util.concurrent.Callable

class SendPostToQueueJob(
        private val source: Source,
        private val group: ProcessedPostGroup
) : Callable<Single<ProcessedPostGroup>> {
    override fun call(): Single<ProcessedPostGroup> {
        return Single.just(group)
                .map { MessageBuilder.withPayload(it).build() }
                .map { source.output().send(it) }
                .map { if (!it) throw FailedToSendToQueueException(group) else group }
    }

    class FailedToSendToQueueException(group: ProcessedPostGroup) : RuntimeException("Failed to send to queue $group")
}
