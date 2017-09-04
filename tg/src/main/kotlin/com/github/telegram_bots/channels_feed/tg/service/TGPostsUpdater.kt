package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.telegram_bots.channels_feed.tg.config.properties.ProcessingProperties
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.job.*
import com.github.telegram_bots.channels_feed.tg.service.processor.PostProcessor
import io.reactivex.Observable
import io.reactivex.Single
import io.reactivex.disposables.Disposable
import io.reactivex.functions.BiFunction
import mu.KLogging
import org.springframework.cloud.stream.annotation.EnableBinding
import org.springframework.cloud.stream.messaging.Source
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import java.util.concurrent.ThreadLocalRandom
import javax.annotation.PreDestroy

@Service
@EnableBinding(Source::class)
class TGPostsUpdater(
        private val props: ProcessingProperties,
        private val client: TelegramClient,
        private val source: Source,
        private val repository: ChannelRepository,
        private val processors: Collection<PostProcessor>
) {
    companion object : KLogging()

    private val random: ThreadLocalRandom = ThreadLocalRandom.current()
    private var disposable: Disposable? = null

    @PreDestroy
    fun onDestroy() {
        disposable?.dispose()
        client.close()
    }

    @Scheduled(fixedDelay = 60_000)
    fun run() {
        iterateChannels()
                .flatMap { download(it) }
                .flatMap { prepare(it) }
                .flatMap { process(it) }
                .flatMap { sendToQueue(it) }
                .flatMap { markDownloaded(it) }
                .doOnSubscribe { disposable = it }
                .doOnError(this::onError)
                .blockingSubscribe()
    }

    private fun onError(throwable: Throwable) {
        logger.error("Channels update error", throwable)
    }

    private fun iterateChannels(): Observable<Channel> {
        return Observable.fromCallable(IterateChannelsJob(repository, props.channelsBatchSize))
                .flatMap { it }
                .zipWith(
                        Observable.interval(
                                random.nextLong(props.postsIntervalMin, props.postsIntervalMax),
                                props.postsIntervalTimeUnit
                        ),
                        BiFunction<Channel, Long, Channel> { channel, _ -> channel }
                )
                .doOnNext { logger.info { "Processing channel $it" } }
    }

    private fun download(channel: Channel): Observable<Pair<Channel, List<TLMessage>>> {
        return Observable.fromCallable(DownloadPostJob(client, channel, props.postsBatchSize))
                .flatMap { it }
                .toList()
                .toObservable()
                .doOnNext { logger.info { "Downloaded channel $channel posts ${it.size}" } }
                .map { channel to it }
    }

    private fun prepare(pair: Pair<Channel, List<TLMessage>>): Observable<RawPostData> {
        return Observable.fromIterable(pair.second).map { RawPostData(it, pair.first) }
    }

    private fun process(data: RawPostData): Observable<Pair<RawPostData, ProcessedPostGroup>> {
        return Single.fromCallable(ProcessPostJob(processors, data))
                .flatMap { it }
                .map { data to it }
                .toObservable()
    }

    private fun sendToQueue(pair: Pair<RawPostData, ProcessedPostGroup>): Observable<RawPostData> {
        return Single.fromCallable(SendPostToQueueJob(source, pair.second))
                .flatMap { it }
                .map { pair.first }
                .toObservable()
    }

    private fun markDownloaded(data: RawPostData): Observable<Boolean> {
        return Single.fromCallable(UpdateChannelLastPostIDJob(repository, data.channel, data.raw.id))
                .flatMap { it }
                .toObservable()
    }
}

