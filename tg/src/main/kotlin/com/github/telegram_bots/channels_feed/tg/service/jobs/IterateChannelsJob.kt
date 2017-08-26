package com.github.telegram_bots.channels_feed.tg.service.jobs

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Observable
import java.util.concurrent.Callable

class IterateChannelsJob(private val repository: ChannelRepository) : Callable<Observable<Channel>> {
    override fun call(): Observable<Channel> {
        return Observable.range(0, Int.MAX_VALUE)
                .buffer(10)
                .map { it.last() }
                .map { repository.list(10, it) }
                .takeUntil { it.isNotEmpty() }
                .flatMap { Observable.fromIterable(it) }
    }
}
