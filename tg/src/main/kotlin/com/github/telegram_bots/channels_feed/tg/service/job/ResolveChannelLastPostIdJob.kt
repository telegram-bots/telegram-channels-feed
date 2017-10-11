package com.github.telegram_bots.channels_feed.tg.service.job;

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLAbsMessage
import com.github.badoualy.telegram.tl.api.TLInputPeerChannel
import com.github.badoualy.telegram.tl.api.messages.TLAbsMessages
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Single
import io.reactivex.functions.Function

class ResolveChannelLastPostIdJob(private val client: TelegramClient) : Function<Channel, Single<Channel>> {
    override fun apply(channel: Channel): Single<Channel> {
        return Single.just(channel)
                .filter { it.lastPostId == Channel.EMPTY_LAST_POST_ID }
                .map { TLInputPeerChannel(channel.telegramId, channel.hash) }
                .map { client.messagesGetHistory(it, 0, 0, 0,1, -1, 1) }
                .flattenAsObservable(TLAbsMessages::getMessages)
                .map(TLAbsMessage::getId)
                .map { channel.copy(lastPostId = it - 1) }
                .onErrorReturn { throw FailedToResolveLastPostIdException(channel) }
                .single(channel)
    }

    class FailedToResolveLastPostIdException(channel: Channel) : RuntimeException(
            "Failed to resolve lastPostId $channel", null, false, false
    )
}
