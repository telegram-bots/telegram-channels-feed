package com.github.telegram_bots.channels_feed.service

import com.github.telegram_bots.channels_feed.domain.Channel
import com.github.telegram_bots.channels_feed.domain.PostInfo
import com.github.telegram_bots.channels_feed.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.domain.RawPost
import com.github.telegram_bots.channels_feed.service.processor.PostProcessor
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
class PostProcessorService(
//        private val source: Source,
        private val channelRepository: ChannelRepository,
        private val postProcessors: Collection<PostProcessor>
) {
    private val log = KotlinLogging.logger {}
    private var disposable: Disposable? = null

    @PreDestroy
    fun onDestroy() {
        disposable?.dispose()
    }

    @StreamListener(Sink.INPUT)
    fun process(raw: RawPost) {
        Observable.just(raw)
                .map(this::postInfo)
                .map(this::processPostData)
                .doOnSubscribe { d -> disposable = d }
                .subscribe(this::send, this::onError)
    }

    private fun postInfo(raw: RawPost) = raw to (channelRepository.find(raw.channelId) ?: Channel.empty(raw.channelId))

    private fun processPostData(info: PostInfo)= postProcessors
            .map { p -> p.type() to p.process(info) }
            .toMap()

    private fun send(postGroup: ProcessedPostGroup) {
        println(postGroup)
//        source.output().send(MessageBuilder.withPayload(postGroup).build())
    }

    private fun onError(throwable: Throwable) = log.error("Send to queue error", throwable)
}
