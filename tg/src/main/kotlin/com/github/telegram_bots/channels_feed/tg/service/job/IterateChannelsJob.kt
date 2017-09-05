package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Observable
import java.util.concurrent.Callable
import java.util.concurrent.atomic.AtomicInteger

class IterateChannelsJob(
        private val repository: ChannelRepository,
        private val batchSize: Int
) : Callable<Observable<Channel>> {
    private val step = AtomicInteger(0)

    override fun call(): Observable<Channel> {
        return Observable.range(0, Int.MAX_VALUE - batchSize - 1)
                .map { step.getAndAdd(batchSize) }
                .doOnNext { println(it) }
                .map { repository.list(batchSize, it) }
                .takeWhile { it.isNotEmpty() }
                .flatMap { Observable.fromIterable(it) }
    }
}
