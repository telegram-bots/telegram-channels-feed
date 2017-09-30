package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.api.utils.date
import com.github.badoualy.telegram.tl.api.TLAbsMessage
import com.github.badoualy.telegram.tl.api.TLInputPeerChannel
import com.github.badoualy.telegram.tl.api.messages.TLAbsMessages
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Single
import io.reactivex.functions.Function
import java.time.Instant

class ResolveChannelCreationDateJob(private val client: TelegramClient) : Function<Channel, Single<Channel>> {
    override fun apply(channel: Channel): Single<Channel> {
        return Single.just(channel)
                .map { TLInputPeerChannel(channel.telegramId, channel.hash) }
                .map { client.messagesGetHistory(it, 2, 0, 0, 1, 2, 0) }
                .flattenAsObservable(TLAbsMessages::getMessages)
                .map(TLAbsMessage::date)
                .map(Int::toLong)
                .map(Instant::ofEpochSecond)
                .map { channel.copy(createdAt = it) }
                .singleOrError()
                .onErrorReturn { throw FailedToResolveCreationDateException(channel) }
    }

    class FailedToResolveCreationDateException(channel: Channel) : RuntimeException(
            "Failed to resolve creation date $channel", null, false, false
    )
}
