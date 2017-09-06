package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.telegram_bots.channels_feed.tg.config.properties.ProcessingProperties
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.job.*
import com.github.telegram_bots.channels_feed.tg.service.processor.PostProcessor
import com.github.telegram_bots.channels_feed.tg.util.toExtended
import io.reactivex.Observable
import io.reactivex.Single
import io.reactivex.disposables.Disposable
import mu.KLogging
import org.springframework.cloud.stream.annotation.EnableBinding
import org.springframework.cloud.stream.messaging.Source
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
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

    private var disposable: Disposable? = null

    @PreDestroy
    fun onDestroy() {
        disposable?.dispose()
        client.close()
    }

    @Scheduled(fixedDelay = 1000)
    fun run() {
        iterateChannels()
                .flatMap { resolve(it) }
                .flatMap { download(it) }
                .flatMap { prepare(it) }
                .flatMap { process(it) }
                .flatMap { sendToQueue(it) }
                .flatMap { markDownloaded(it) }
                .doOnSubscribe { disposable = it }
                .doOnError(this::onError)
                .blockingSubscribe()
    }

    private fun onError(throwable: Throwable) = logger.error("[ERROR]", throwable)

    private fun iterateChannels(): Observable<Channel> {
        return Observable.fromCallable(IterateChannelsJob(repository, props.channelsBatchSize))
                .flatMap { it }
                .concatMap {
                    Observable.just(it).toExtended().randomDelay(
                            props.postsIntervalMin,
                            props.postsIntervalMax,
                            props.postsIntervalTimeUnit
                    )
                }
                .doOnNext { logger.info { "[PROCESS CHANNEL] $it" } }
    }

    private fun resolve(channel: Channel): Observable<Channel> {
        return Observable.just(channel)
                .filter { it.isEmpty() }
                .flatMap {
                    Single.fromCallable(ResolveChannelJob(client, repository, it))
                            .flatMap { it }
                            .toObservable()
                            .concatMap {
                                Observable.just(it).toExtended().randomDelay(
                                        props.postsIntervalMin,
                                        props.postsIntervalMax,
                                        props.postsIntervalTimeUnit
                                )
                            }
                            .doOnNext { logger.info { "[RESOLVE CHANNEL] $it" } }
                }
                .defaultIfEmpty(channel)
    }

    private fun download(channel: Channel): Observable<Pair<Channel, List<TLMessage>>> {
        return Observable.fromCallable(DownloadPostJob(client, channel, props.postsBatchSize))
                .flatMap { it }
                .toList()
                .toObservable()
                .skipWhile { it.isEmpty() }
                .doOnNext { logger.info { "[DOWNLOAD POSTS] ${it.size}x $channel" } }
                .map { channel to it }
    }

    private fun prepare(pair: Pair<Channel, List<TLMessage>>): Observable<RawPostData> {
        return Observable.fromIterable(pair.second)
                .map { RawPostData(it, pair.first) }
                .doOnSubscribe { logger.info { "[PREPARE POSTS] ${pair.second.size}x ${pair.first}" } }
    }

    private fun process(data: RawPostData): Observable<Pair<RawPostData, ProcessedPostGroup>> {
        return Single.fromCallable(ProcessPostJob(processors, data))
                .flatMap { it }
                .map { data to it }
                .toObservable()
                .doOnNext { logger.trace { "[PROCESS POST] $data" } }
    }

    private fun sendToQueue(pair: Pair<RawPostData, ProcessedPostGroup>): Observable<RawPostData> {
        return Single.fromCallable(SendPostToQueueJob(source, pair.second))
                .flatMap { it }
                .map { pair.first }
                .toObservable()
                .doOnNext { logger.trace { "[SEND TO QUEUE] ${pair.second}" } }
    }

    private fun markDownloaded(data: RawPostData): Observable<Channel> {
        return Single.fromCallable(UpdateChannelLastPostIDJob(repository, data.channel, data.raw.id))
                .flatMap { it }
                .toObservable()
                .doOnNext { logger.trace { "[MARK DOWNLOADED] $data" } }
    }
}

