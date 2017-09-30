package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.TLInputChannel
import com.github.badoualy.telegram.tl.api.TLMessage
import com.github.badoualy.telegram.tl.api.messages.TLAbsMessages
import com.github.badoualy.telegram.tl.core.TLIntVector
import com.github.telegram_bots.channels_feed.tg.domain.Channel
import io.reactivex.Flowable
import io.reactivex.Single
import io.reactivex.functions.Function
import io.reactivex.rxkotlin.ofType
import io.reactivex.rxkotlin.zipWith

class DownloadPostsJob(private val client: TelegramClient, private val batchSize: Int)
    : Function<Channel, Flowable<TLMessage>>
{
    override fun apply(channel: Channel): Flowable<TLMessage> {
        return Flowable.range(channel.lastPostId + 1, batchSize)
                .toList()
                .map { TLIntVector().apply { addAll(it) } }
                .zipWith(Single.just(TLInputChannel(channel.telegramId, channel.hash)))
                .map { (ids, channel) -> client.channelsGetMessages(channel, ids) }
                .flattenAsFlowable(TLAbsMessages::getMessages)
                .ofType()
    }
}
