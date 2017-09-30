package com.github.telegram_bots.channels_feed.tg.service.updater

import io.reactivex.Completable
import io.reactivex.disposables.Disposable
import io.reactivex.schedulers.Schedulers
import mu.KLogging
import java.util.concurrent.Executors
import javax.annotation.PostConstruct
import javax.annotation.PreDestroy

abstract class AbstractUpdater(private val name: String) {
    companion object : KLogging()

    private val executor = Executors.newSingleThreadExecutor({ Thread(it, name) })
    protected val scheduler = Schedulers.from(executor)
    private var disposable: Disposable? = null

    @PreDestroy
    open fun onDestroy() = disposable?.dispose()

    @PostConstruct
    fun init() {
        run()
                .doOnSubscribe(this::onSubscribe)
                .doOnError(this::onError)
                .observeOn(scheduler)
                .subscribe()
    }

    abstract fun run(): Completable

    private fun onSubscribe(disposable: Disposable) {
        this.disposable = disposable
    }

    private fun onError(throwable: Throwable) = logger.error("[ERROR]", throwable)
}
