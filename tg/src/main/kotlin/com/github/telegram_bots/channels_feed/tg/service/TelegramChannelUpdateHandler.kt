package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.Kotlogram
import com.github.badoualy.telegram.api.TelegramApp
import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.jobs.*
import com.github.telegram_bots.channels_feed.tg.service.processor.PostProcessor
import io.reactivex.Observable
import io.reactivex.disposables.Disposable
import mu.KLogging
import org.springframework.cloud.stream.annotation.EnableBinding
import org.springframework.cloud.stream.messaging.Source
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import javax.annotation.PreDestroy

@Service
@EnableBinding(Source::class)
class TelegramChannelUpdateHandler(
        app: TelegramApp,
        storage: FileAPIStorage,
        private val source: Source,
        private val repository: ChannelRepository,
        private val processors: Collection<PostProcessor>
) {
    companion object : KLogging()

    private val client: TelegramClient = Kotlogram.getDefaultClient(app, storage)
    private var disposable: Disposable? = null

    @PreDestroy
    fun onDestroy() {
        disposable?.dispose()
        client.close()
    }

    @Scheduled(fixedRate = 10000)
    fun run() {
        iterateChannels()
                .flatMap { subscribeToChannel(it) }
                .flatMap { downloadPosts(it) }
                .flatMap { unsubscribeFromChannel(it) }
                .flatMap { preparePosts(it) }
                .flatMap { processPost(it) }
                .flatMap { sendPostToQueue(it) }
                .flatMap { markDownloadedPost(it) }
                .doOnSubscribe { disposable = it }
                .subscribe(this::onNext, this::onError)
    }

    private fun onNext(channel: Channel) {
        logger.debug { "Channel $channel was updated" }
    }

    private fun onError(throwable: Throwable) {
        logger.error { throwable }
    }

    private fun iterateChannels(): Observable<Channel> {
        return Observable.fromCallable(IterateChannelsJob(repository)).flatMap { it }
    }

    private fun subscribeToChannel(channel: Channel): Observable<Channel> {
        return Observable.fromCallable(SubscribeChannelJob(client, channel)).flatMap { it }
    }

    private fun downloadPosts(channel: Channel): Observable<Pair<Channel, List<TLMessage>>> {
        return Observable.fromCallable(DownloadPostJob(client, channel))
                .flatMap { it }
                .toList()
                .toObservable()
                .map { channel to it }
    }

    private fun unsubscribeFromChannel(data: Pair<Channel, List<TLMessage>>): Observable<Pair<Channel, List<TLMessage>>> {
        return Observable.fromCallable(UnsubscribeChannelJob(client, data.first))
                .flatMap { it }
                .map { it to data.second }
    }

    private fun preparePosts(pair: Pair<Channel, List<TLMessage>>): Observable<RawPostData> {
        return Observable.fromIterable(pair.second).map { RawPostData(it, pair.first) }
    }

    private fun processPost(data: RawPostData): Observable<Pair<RawPostData, ProcessedPostGroup>> {
        return Observable.fromCallable(ProcessPostJob(processors, data))
                .flatMap { it }
                .map { data to it }
    }

    private fun sendPostToQueue(pair: Pair<RawPostData, ProcessedPostGroup>): Observable<RawPostData> {
        return Observable.fromCallable(SendToQueueJob(source, pair.second))
                .flatMap { it }
                .map { pair.first }
    }

    private fun markDownloadedPost(data: RawPostData): Observable<Channel> {
        return Observable.fromCallable(UpdateChannelLastPostIDJob(repository, data.channel, data.raw.id))
                .flatMap { it }
    }
}
