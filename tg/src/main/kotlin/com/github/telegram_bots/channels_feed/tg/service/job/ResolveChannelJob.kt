package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLChannel
import com.github.badoualy.telegram.tl.api.TLInputPeerChannel
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Single
import io.reactivex.rxkotlin.toSingle
import java.util.concurrent.Callable

class ResolveChannelJob(
        private val client: TelegramClient,
        private val repository: ChannelRepository,
        private val channel: Channel
) : Callable<Single<Channel>> {
    override fun call(): Single<Channel> {
        return try {
            resolveChannel(channel)
                    .let(this::resolveLastPostId)
                    .let(this::update)
                    .toSingle()
        } catch (e: Exception) {
            Single.error(e)
        }
    }

    private fun resolveChannel(channel: Channel): Channel {
        return client.contactsResolveUsername(channel.url)
                .chats
                ?.mapNotNull { it as? TLChannel }
                ?.find { channel.url.equals(it.username, true) }
                ?.let {
                    Channel(
                            id = channel.id,
                            telegramId = it.id,
                            hash = it.accessHash,
                            url = it.username.toLowerCase(),
                            name = it.title,
                            lastPostId = -1,
                            lastSentId = null
                    )
                }
                ?: throw NoSuchChannelException(channel)
    }

    private fun resolveLastPostId(channel: Channel): Channel {
        val lastPostId = client
                .messagesGetHistory(
                        TLInputPeerChannel(channel.telegramId, channel.hash),
                        0,
                        0,
                        0,
                        1,
                        -1,
                        1
                )
                .messages
                ?.firstOrNull()
                ?.id
                ?: throw FailedToResolveLastPostIdException(channel)

        return channel.copy(lastPostId = lastPostId)
    }

    private fun update(channel: Channel) = repository.update(channel)

    class FailedToResolveLastPostIdException(channel: Channel) : RuntimeException("Failed to resolve lastPostId $channel")

    class NoSuchChannelException(channel: Channel) : RuntimeException("No such channel $channel")
}
