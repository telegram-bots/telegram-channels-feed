package com.github.telegram_bots.channels_feed.tg.service.updater

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.badoualy.telegram.tl.exception.RpcErrorException
import com.github.telegram_bots.channels_feed.tg.config.properties.ProcessingProperties
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import com.github.telegram_bots.channels_feed.tg.service.job.*
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
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit
import javax.annotation.PreDestroy

@Service
@EnableBinding(Source::class)
class PostsUpdater(
        private val props: ProcessingProperties,
        private val client: TelegramClient,
        private val source: Source,
        private val repository: ChannelRepository,
        private val processors: Collection<PostProcessor>
) : AbstractUpdater("posts-updater") {
    companion object : KLogging()

    @PreDestroy
    override fun onDestroy() {
        super.onDestroy()
        client.close()
    }

    override fun run(): Completable {
        return iterateChannels()
                .flatMapSingle(this::resolve)
                .flatMapMaybe(this::download)
                .flatMapSingle(this::prepare)
                .flatMap(this::process)
                .flatMapSingle(this::sendToQueue)
                .flatMapCompletable(this::markAsDownloaded)
                .doOnSubscribe(this::onSubscribe)
                .doOnTerminate(this::onTerminate)
    }

    private fun iterateChannels(): Flowable<Channel> {
        return repository.list()
                .repeatWhen { it.delay(1, TimeUnit.SECONDS) }
                .concatMap {
                    Single.just(it)
                            .randomDelay(
                                    delayMin = props.postsIntervalMin,
                                    delayMax = props.postsIntervalMax,
                                    unit = props.postsIntervalTimeUnit,
                                    scheduler = scheduler
                            )
                            .toFlowable()
                }
                .doOnNext { logger.info { "[PROCESS CHANNEL] $it" } }
    }

    private fun resolve(channel: Channel): Single<Channel> {
        return Maybe.just(channel)
                .filter(Channel::isEmpty)
                .concatMap { ch ->
                    Single.just(ch)
                            .randomDelay(
                                    delayMin = props.channelsIntervalMin,
                                    delayMax = props.channelsIntervalMax,
                                    unit = props.channelsIntervalTimeUnit,
                                    scheduler = scheduler
                            )
                            .flatMap(ResolveChannelInfoJob(client))
                            .flatMap(ResolveChannelCreationDateJob(client))
                            .flatMap(ResolveChannelLastPostIdJob(client))
                            .flatMap { repository.update(it).andThen(Single.just(it)) }
                            .retry(this::retry)
                            .doOnSuccess { logger.info { "[RESOLVE CHANNEL] $ch" } }
                            .doOnSubscribe { client.accountUpdateStatus(false) }
                            .doOnSuccess { client.accountUpdateStatus(true) }
                            .toMaybe()
                }
                .toSingle(channel)
    }

    private fun download(channel: Channel): Maybe<Pair<Channel, List<TLMessage>>> {
        return Single.just(channel)
                .retry(this::retry)
                .flatMapPublisher(DownloadPostsJob(client, props.postsBatchSize))
                .toList()
                .filter(List<TLMessage>::isNotEmpty)
                .zipWith(Maybe.just(channel), { msgs, ch -> ch to msgs })
                .doOnSuccess { (ch, msgs) -> logger.info { "[DOWNLOAD POSTS] ${msgs.size}x $ch" } }
                .doOnSubscribe { client.accountUpdateStatus(false) }
                .doOnComplete { client.accountUpdateStatus(true) }
    }

    private fun prepare(pair: Pair<Channel, List<TLMessage>>): Single<List<RawPostData>> {
        val (channel, msgs) = pair

        return Flowable.fromIterable(msgs)
                .zipWith(Single.just(channel).repeat())
                .map { (msg, ch) -> RawPostData(ch, msg) }
                .toList()
                .doOnSubscribe { logger.info { "[PREPARE POSTS] ${msgs.size}x $channel" } }
    }

    private fun process(list: List<RawPostData>): Flowable<Pair<RawPostData, ProcessedPostGroup>> {
        return Flowable.fromIterable(list)
                .flatMapSingle { raw ->
                    Single.just(raw)
                            .subscribeOn(Schedulers.computation())
                            .flatMap(ProcessPostJob(processors))
                            .zipWith(Single.just(raw), { p, r -> r to p })
                }
                .sorted { (_, group1), (_, group2) -> group1.postId.compareTo(group2.postId) }
                .doOnSubscribe { logger.info { "[PROCESS POSTS] ${list.size}x ${list.firstOrNull()?.channel}" } }
    }

    private fun sendToQueue(pair: Pair<RawPostData, ProcessedPostGroup>): Single<RawPostData> {
        val (raw, processed) = pair

        return Single.just(processed)
                .subscribeOn(Schedulers.single())
                .flatMapCompletable(SendPostToQueueJob(source))
                .doOnSubscribe { logger.debug { "[SEND TO QUEUE] $processed" } }
                .andThen(Single.just(raw))
    }

    private fun markAsDownloaded(raw: RawPostData): Completable {
        return Single.just(raw)
                .subscribeOn(Schedulers.io())
                .map { (channel, msg) -> channel.copy(lastPostId = msg.id) }
                .doOnSuccess { logger.debug { "[MARK DOWNLOADED] $it" } }
                .flatMapCompletable(repository::update)
    }

    private fun onSubscribe(disposable: Disposable) = logger.info { "[START PROCESSING]" }

    private fun onTerminate() = logger.info { "[STOP PROCESSING]" }

    private fun retry(count: Int, throwable: Throwable): Boolean {
        return when {
            count < 10 && throwable is RpcErrorException && throwable.code == 420 -> {
                TimeUnit.SECONDS.sleep(throwable.tagInteger.toLong() / 2)
                return true
            }
            else -> false
        }
    }
}

