package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLInputChannel
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.badoualy.telegram.tl.core.TLIntVector
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Observable
import java.util.concurrent.Callable

class DownloadPostJob(
        private val client: TelegramClient,
        private val channel: Channel,
        private val batchSize: Int
) : Callable<Observable<TLMessage>> {
    override fun call(): Observable<TLMessage> {
        return Observable.range(channel.lastPostId, batchSize)
                .toList()
                .toObservable()
                .map { TLInputChannel(channel.telegramId, channel.hash) to TLIntVector().apply { addAll(it) } }
                .map { client.channelsGetMessages(it.first, it.second) }
                .flatMap { Observable.fromIterable(it.messages) }
                .filter { it is TLMessage }
                .map { it as TLMessage }
    }
}
