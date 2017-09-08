package com.github.telegram_bots.channels_feed.tg.util

import io.reactivex.Scheduler
import io.reactivex.Single
import io.reactivex.schedulers.Schedulers
import java.util.concurrent.ThreadLocalRandom
import java.util.concurrent.TimeUnit

fun <T> Single<T>.randomDelay(
        delayMin: Long,
        delayMax: Long,
        unit: TimeUnit,
        scheduler: Scheduler = Schedulers.computation()
): Single<T> {
    val random = ThreadLocalRandom.current()
    return delay(random.nextLong(delayMin, delayMax), unit, scheduler)
}
