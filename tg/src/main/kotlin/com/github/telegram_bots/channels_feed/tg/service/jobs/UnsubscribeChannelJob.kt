package com.github.telegram_bots.channels_feed.tg.service.jobs

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLChannel
import com.github.badoualy.telegram.tl.api.TLInputChannel
import com.github.badoualy.telegram.tl.api.TLUpdates
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Observable
import java.util.concurrent.Callable

class UnsubscribeChannelJob(private val client: TelegramClient, private val channel: Channel) : Callable<Observable<Channel>> {
    override fun call(): Observable<Channel> {
        return client.channelsLeaveChannel(TLInputChannel(channel.id, channel.hash))
                .let { it as? TLUpdates }
                ?.chats
                ?.mapNotNull { it as? TLChannel }
                ?.find { it.id == channel.telegramId && it.left == true }
                .let { Observable.just(channel) }
                ?: Observable.error { FailedToLeaveChannelException(channel) }
    }

    class FailedToLeaveChannelException(channel: Channel) : RuntimeException("Failed to leave channel $channel")
}
