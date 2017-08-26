package com.github.telegram_bots.channels_feed.tg.service.jobs

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLInputChannel
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.badoualy.telegram.tl.core.TLIntVector
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Observable
import java.util.concurrent.Callable

class DownloadPostJob(private val client: TelegramClient, private val channel: Channel) : Callable<Observable<TLMessage>> {
    override fun call(): Observable<TLMessage> {
        if (channel.lastPostId == null) return Observable.empty()

        return Observable.range(channel.lastPostId, Int.MAX_VALUE)
                .buffer(50)
                .map { TLInputChannel(channel.id, channel.hash) to TLIntVector().apply { addAll(it) } }
                .map { client.channelsGetMessages(it.first, it.second) }
                .takeUntil { it.messages.count { it is TLMessage } > 0 }
                .flatMap { Observable.fromIterable(it.messages) }
                .filter { it is TLMessage }
                .map { it as TLMessage }
    }
}
