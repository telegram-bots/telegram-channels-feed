package com.github.telegram_bots.channels_feed.service

import io.reactivex.Observable
import io.reactivex.disposables.Disposable
import mu.KotlinLogging
import org.springframework.cloud.stream.annotation.EnableBinding
import org.springframework.cloud.stream.annotation.StreamListener
import org.springframework.cloud.stream.messaging.Sink
import org.springframework.cloud.stream.messaging.Source
import org.springframework.messaging.support.MessageBuilder
import org.springframework.stereotype.Service

import javax.annotation.PreDestroy

@Service
@EnableBinding(Sink::class)
class PostProcessor(private val source: Source) {
    private val log = KotlinLogging.logger {}
    private var disposable: Disposable? = null

    @PreDestroy
    fun onDestroy() {
        disposable?.dispose()
    }

    @StreamListener(Sink.INPUT)
    fun process(payload: String) {
        Observable.just(payload)
                .doOnSubscribe { d -> disposable = d }
                .subscribe(this::send, this::onError)
    }

    private fun send(payload: String) {
        source.output().send(MessageBuilder.withPayload(payload).build())
    }

    private fun onError(throwable: Throwable) {
        log.error("Ошибка записи", throwable)
    }
}
