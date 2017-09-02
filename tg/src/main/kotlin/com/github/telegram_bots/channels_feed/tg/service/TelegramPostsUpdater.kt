package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.Kotlogram
import com.github.badoualy.telegram.api.TelegramApp
import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.badoualy.telegram.tl.exception.RpcErrorException
import com.github.telegram_bots.channels_feed.tg.config.properties.TGProperties
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
import java.io.IOException
import java.util.*
import java.util.concurrent.ThreadLocalRandom
import java.util.concurrent.TimeUnit
import javax.annotation.PostConstruct
import javax.annotation.PreDestroy

@Service
@EnableBinding(Source::class)
class TelegramPostsUpdater(
        app: TelegramApp,
        storage: TelegramConfigStorage,
        private val props: TGProperties,
        private val source: Source,
        private val repository: ChannelRepository,
        private val processors: Collection<PostProcessor>
) {
    companion object : KLogging()

    private val client: TelegramClient = Kotlogram.getDefaultClient(app, storage)
    private val random: ThreadLocalRandom = ThreadLocalRandom.current()
    private var disposable: Disposable? = null

    @PostConstruct
    fun init() {
        try {
            val sentCode = client.authSendCode(false, props.number, true)
            logger.info { "Authentication code: " }
            val code = Scanner(System.`in`).nextLine()

            val authorization =
                    try {
                        client.authSignIn(props.number, sentCode.phoneCodeHash, code)
                    } catch (e: RpcErrorException) {
                        if (!e.tag.equals("SESSION_PASSWORD_NEEDED", true)) throw e

                        logger.info { "Two-step auth password: " }
                        val password = Scanner(System.`in`).nextLine()
                        client.authCheckPassword(password)
                    }

            authorization.user.asUser.apply {
                logger.info { "You are now signed in as $firstName $lastName @$username" }
            }
        } catch (e: RpcErrorException) {
            logger.error { e }
        } catch (e: IOException) {
            logger.error { e }
        }
    }

    @PreDestroy
    fun onDestroy() {
        disposable?.dispose()
        client.close()
    }

    @Scheduled(fixedDelay = 1000)
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
        return Observable.fromCallable(IterateChannelsJob(repository, 10))
                .flatMap { it }
                .zipWith(
                        Observable.interval(random.nextLong(60, 120), TimeUnit.SECONDS),
                        BiFunction<Channel, Long, Channel> { channel, _ -> channel }
                )
                .doOnNext { logger.info { "Iterating channel $it" } }
    }

    private fun download(channel: Channel): Observable<Pair<Channel, List<TLMessage>>> {
        return Observable.fromCallable(DownloadPostJob(client, channel, 50))
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

    private fun markDownloaded(data: RawPostData): Observable<Channel> {
        return Single.fromCallable(UpdateChannelLastPostIDJob(repository, data.channel, data.raw.id))
                .flatMap { it }
                .toObservable()
    }
}

