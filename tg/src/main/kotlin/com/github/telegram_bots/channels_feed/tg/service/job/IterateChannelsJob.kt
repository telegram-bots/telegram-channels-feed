package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import com.github.telegram_bots.channels_feed.tg.util.XObservable
import io.reactivex.Observable
import java.util.concurrent.Callable

class IterateChannelsJob(
        private val repository: ChannelRepository,
        private val batchSize: Int
) : Callable<Observable<Channel>> {
    override fun call(): Observable<Channel> {
        return XObservable.stepRange(0, step = batchSize)
                .map { repository.list(limit = batchSize, offset = it) }
                .takeWhile { it.isNotEmpty() }
                .flatMap { Observable.fromIterable(it) }
    }
}
