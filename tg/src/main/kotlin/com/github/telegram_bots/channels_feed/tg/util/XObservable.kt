package com.github.telegram_bots.channels_feed.tg.util

import io.reactivex.Observable
import io.reactivex.ObservableSource
import java.util.concurrent.ThreadLocalRandom
import java.util.concurrent.TimeUnit


class XObservable<T>(private val observable: Observable<T>) : ObservableSource<T> by observable {
    private val random = ThreadLocalRandom.current()

    companion object {
        fun stepRange(start: Int, step: Int, count: Int = Int.MAX_VALUE): Observable<Int> {
            return Observable.create { sub ->
                for (n in start until count - step step step) {
                    if (sub.isDisposed) break
                    sub.onNext(n)
                }
                sub.onComplete()
            }
        }
    }

    fun randomDelay(delayMin: Long, delayMax: Long, unit: TimeUnit): Observable<T> {
        return observable.delay(random.nextLong(delayMin, delayMax), unit)
    }
}

fun <T> Observable<T>.toExtended() = XObservable(this)
