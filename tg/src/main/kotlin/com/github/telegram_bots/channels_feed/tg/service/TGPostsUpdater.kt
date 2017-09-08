package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.badoualy.telegram.tl.exception.RpcErrorException
import com.github.telegram_bots.channels_feed.tg.config.properties.ProcessingProperties
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.job.DownloadPostJob
import com.github.telegram_bots.channels_feed.tg.service.job.ProcessPostJob
import com.github.telegram_bots.channels_feed.tg.service.job.ResolveChannelJob
import com.github.telegram_bots.channels_feed.tg.service.job.SendPostToQueueJob
import com.github.telegram_bots.channels_feed.tg.service.processor.PostProcessor
import com.github.telegram_bots.channels_feed.tg.util.randomDelay
import io.reactivex.Completable
import io.reactivex.Flowable
import io.reactivex.Maybe
import io.reactivex.Single
import io.reactivex.disposables.Disposable
import io.reactivex.rxkotlin.zipWith
import io.reactivex.schedulers.Schedulers
import mu.KLogging
import org.springframework.cloud.stream.annotation.EnableBinding
import org.springframework.cloud.stream.messaging.Source
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong
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

    private val counter = AtomicLong(0)
    private val executor = Executors.newSingleThreadExecutor({ Thread(it, "tg-post-updater")})
    private var disposable: Disposable? = null

    @PreDestroy
    fun onDestroy() {
        disposable?.dispose()
        client.close()
    }

    @Scheduled(fixedDelay = 1000)
    fun run() {
        iterateChannels()
                .flatMapSingle(this::resolve)
                .flatMapMaybe(this::download)
                .flatMapSingle(this::prepare)
                .flatMap(this::process)
                .flatMapSingle(this::sendToQueue)
                .flatMapCompletable(this::markAsDownloaded)
                .doOnSubscribe(this::onSubscribe)
                .doOnError(this::onError)
                .doOnComplete(this::onComplete)
                .blockingAwait()
    }

    private fun iterateChannels(): Flowable<Channel> {
        return repository.list()
                .concatMap {
                    Single.just(it)
                            .randomDelay(
                                    delayMin = props.postsIntervalMin,
                                    delayMax = props.postsIntervalMax,
                                    unit = props.postsIntervalTimeUnit,
                                    scheduler = Schedulers.from(executor)
                            )
                            .toFlowable()
                }
                .doOnNext { logger.info { "[PROCESS CHANNEL] $it" } }
    }

    private fun resolve(channel: Channel): Single<Channel> {
        return Single.just(channel)
                .filter(Channel::isEmpty)
                .concatMap { ch ->
                    Single.fromCallable(ResolveChannelJob(client, repository, ch))
                            .flatMap { it }
                            .randomDelay(
                                    delayMin = props.channelsIntervalMin,
                                    delayMax = props.channelsIntervalMax,
                                    unit = props.channelsIntervalTimeUnit,
                                    scheduler = Schedulers.from(executor)
                            )
                            .retry(this::retry)
                            .doOnSuccess { logger.info { "[RESOLVE CHANNEL] $ch" } }
                            .toMaybe()
                }
                .toSingle(channel)
    }

    private fun download(channel: Channel): Maybe<Pair<Channel, List<TLMessage>>> {
        return Single.fromCallable(DownloadPostJob(client, channel, props.postsBatchSize))
                .subscribeOn(Schedulers.from(executor))
                .retry(this::retry)
                .flatMapPublisher { it }
                .toList()
                .filter(List<TLMessage>::isNotEmpty)
                .zipWith(Maybe.just(channel), { msgs, ch -> ch to msgs })
                .doOnSuccess { (ch, msgs) -> logger.info { "[DOWNLOAD POSTS] ${msgs.size}x $ch" } }
    }

    private fun prepare(pair: Pair<Channel, List<TLMessage>>): Single<List<RawPostData>> {
        val (channel, msgs) = pair

        return Flowable.fromIterable(msgs)
                .subscribeOn(Schedulers.from(executor))
                .zipWith(Single.just(channel).repeat())
                .map { (msg, ch) -> RawPostData(ch, msg) }
                .toList()
                .doOnSubscribe { logger.info { "[PREPARE POSTS] ${msgs.size}x $channel" } }
    }

    private fun process(list: List<RawPostData>): Flowable<Pair<RawPostData, ProcessedPostGroup>> {
        return Flowable.fromIterable(list)
                .flatMapSingle { raw ->
                    Single.fromCallable(ProcessPostJob(processors, raw))
                        .subscribeOn(Schedulers.computation())
                        .flatMap { it }
                        .zipWith(Single.just(raw), { p, r -> r to p })
                }
                .sorted { (_, group1), (_, group2) -> group1.postId.compareTo(group2.postId) }
                .doOnSubscribe { logger.info { "[PROCESS POSTS] ${list.size}x ${list.firstOrNull()?.channel}" } }
    }

    private fun sendToQueue(pair: Pair<RawPostData, ProcessedPostGroup>): Single<RawPostData> {
        val (raw, processed) = pair

        return Single.fromCallable(SendPostToQueueJob(source, processed))
                .subscribeOn(Schedulers.single())
                .flatMapCompletable { it }
                .doOnSubscribe { logger.debug { "[SEND TO QUEUE] $processed" } }
                .andThen(Single.just(raw))
    }

    private fun markAsDownloaded(raw: RawPostData): Completable {
        return Single.just(raw)
                .subscribeOn(Schedulers.io())
                .map { (channel, msg) -> channel.copy(lastPostId = msg.id) }
                .doOnSuccess{ logger.debug { "[MARK DOWNLOADED] $it" } }
                .flatMapCompletable(repository::update)
    }

    private fun onSubscribe(disposable: Disposable) {
        this.disposable = disposable
        logger.info { "[START PROCESSING] #${counter.incrementAndGet()}" }
    }

    private fun onError(throwable: Throwable) = logger.error("[ERROR]", throwable)

    private fun onComplete() = logger.info { "[END PROCESSING] #${counter.get()}" }

    private fun retry(count: Int, throwable: Throwable): Boolean {
        return when {
            count < 10 && throwable is RpcErrorException && throwable.code == 420 -> {
                TimeUnit.SECONDS.sleep(throwable.tagInteger.toLong())
                return true
            }
            else -> false
        }
    }
}

