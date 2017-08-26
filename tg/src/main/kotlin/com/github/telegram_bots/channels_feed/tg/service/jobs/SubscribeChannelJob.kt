package com.github.telegram_bots.channels_feed.tg.service.jobs

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLChannel
import com.github.badoualy.telegram.tl.api.TLInputChannel
import com.github.badoualy.telegram.tl.api.TLUpdates
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Observable
import java.util.concurrent.Callable

class SubscribeChannelJob(
        private val client: TelegramClient,
        private val channel: Channel,
        private val mode: Mode = Mode.EXISTING
) : Callable<Observable<Channel>> {
    override fun call(): Observable<Channel> {
        return try {
            val channel = if (mode == Mode.NEW) {
                client.contactsResolveUsername(channel.url)
                        .chats
                        ?.mapNotNull { it as? TLChannel }
                        ?.find { it.username == channel.url }
                        ?.let { Channel(
                                id = -1,
                                telegramId = it.id,
                                hash = it.accessHash,
                                url = it.username,
                                name = it.title,
                                lastPostId = null
                        ) }
                        ?: throw NoSuchChannelException(channel.url)
            } else this.channel

            client.channelsJoinChannel(TLInputChannel(channel.id, channel.hash))
                    .let { it as? TLUpdates }
                    ?.chats
                    ?.mapNotNull { it as? TLChannel }
                    ?.find { it.id == channel.telegramId }
                    ?: throw FailedToJoinChannelException(channel)

            Observable.just(channel)
        } catch (e: Exception) {
            Observable.error(e)
        }
    }

    enum class Mode { NEW, EXISTING }

    class NoSuchChannelException(channelLink: String) : RuntimeException("No such channel $channelLink")

    class FailedToJoinChannelException(channel: Channel) : RuntimeException("Failed to join channel $channel")
}
