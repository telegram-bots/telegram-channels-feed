package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLChannel
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import com.github.telegram_bots.channels_feed.tg.service.ChannelRepository
import io.reactivex.Single
import io.reactivex.rxkotlin.toSingle
import java.util.concurrent.Callable

class SubscribeChannelJob(
        private val client: TelegramClient,
        private val repository: ChannelRepository,
        private val channelUrl: String
) : Callable<Single<Channel>> {
    override fun call(): Single<Channel> {
        return try {
            (findExisting(channelUrl) ?: create(channelUrl)).toSingle()
        } catch (e: Exception) {
            Single.error(e)
        }
    }

    private fun findExisting(channelUrl: String) = repository.find(channelUrl)

    private fun create(channelUrl: String) = resolveChannel(channelUrl).let(this::resolveLastPostId).let(this::save)

    private fun resolveChannel(channelUrl: String): Channel {
        return client.contactsResolveUsername(channelUrl)
                .chats
                ?.mapNotNull { it as? TLChannel }
                ?.find { it.username == channelUrl }
                ?.let {
                    Channel(
                            id = -1,
                            telegramId = it.id,
                            hash = it.accessHash,
                            url = it.username,
                            name = it.title,
                            lastPostId = -1,
                            lastSentId = null
                    )
                }
                ?: throw NoSuchChannelException(channelUrl)
    }

    private fun resolveLastPostId(channel: Channel): Channel {
        TODO("IMPLEMENT")
    }

    private fun save(channel: Channel) = repository.save(channel)

    class NoSuchChannelException(channelLink: String) : RuntimeException("No such channel $channelLink")
}
