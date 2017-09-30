package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import io.reactivex.Completable
import io.reactivex.Single
import io.reactivex.functions.Function
import org.springframework.cloud.stream.messaging.Source
import org.springframework.messaging.support.MessageBuilder

class SendPostToQueueJob(private val source: Source) : Function<ProcessedPostGroup, Completable> {
    override fun apply(group: ProcessedPostGroup): Completable {
        return Single.just(group)
                .map { MessageBuilder.withPayload(it).build() }
                .map(source.output()::send)
                .doOnSuccess { if (!it) throw FailedToSendToQueueException(group) }
                .toCompletable()
    }

    class FailedToSendToQueueException(group: ProcessedPostGroup) : RuntimeException(
            "Failed to send to queue $group", null, false, false
    )
}
