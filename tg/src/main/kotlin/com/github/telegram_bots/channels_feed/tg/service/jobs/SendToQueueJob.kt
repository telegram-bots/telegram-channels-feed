package com.github.telegram_bots.channels_feed.tg.service.jobs

import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import io.reactivex.Observable
import org.springframework.cloud.stream.messaging.Source
import org.springframework.messaging.support.MessageBuilder
import java.util.concurrent.Callable

class SendToQueueJob(private val source: Source, private val group: ProcessedPostGroup) : Callable<Observable<ProcessedPostGroup>> {
    override fun call(): Observable<ProcessedPostGroup> {
        return Observable.just(group)
                .map { MessageBuilder.withPayload(it).build() }
                .map { source.output().send(it) }
                .map { if (it) throw FailedToSendToQueueException(group) else group }
    }

    class FailedToSendToQueueException(group: ProcessedPostGroup) : RuntimeException("Failed to send to queue $group")
}
