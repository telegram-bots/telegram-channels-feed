package com.github.telegram_bots.channels_feed.tg.service.updater

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import com.github.telegram_bots.channels_feed.tg.service.job.ScheduleChannelInfoUpdateJob
import io.reactivex.Completable
import io.reactivex.Flowable
import io.reactivex.Single
import mu.KLogging
import org.springframework.stereotype.Service
import java.time.Duration
import java.time.LocalDateTime
import java.time.temporal.ChronoUnit
import java.util.concurrent.TimeUnit.SECONDS

@Service
class ChannelUpdater(private val repository: ChannelRepository) : AbstractUpdater("channel-updater") {
    companion object : KLogging()

    override fun run(): Completable = iterateChannels().flatMapCompletable(this::scheduleUpdate)

    private fun iterateChannels(): Flowable<Channel> {
        return repository.listNeedToUpdate()
                .repeatWhen { it.delay(secondsUntilNextDay(), SECONDS) }
    }

    private fun scheduleUpdate(channel: Channel): Completable {
        return Single.just(channel)
                .flatMapCompletable(ScheduleChannelInfoUpdateJob(repository))
                .doOnComplete { logger.info { "[SCHEDULED CHANNEL UPDATE] $channel" } }
    }

    private fun secondsUntilNextDay(): Long {
        return Duration
                .between(
                    LocalDateTime.now(),
                    LocalDateTime.now().plusDays(1).truncatedTo(ChronoUnit.DAYS)
                )
                .seconds
    }
}
