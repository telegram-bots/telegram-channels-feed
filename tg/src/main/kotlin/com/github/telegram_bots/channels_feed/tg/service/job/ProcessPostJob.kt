package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.processor.PostProcessor
import io.reactivex.Observable
import io.reactivex.Single
import io.reactivex.functions.Function

class ProcessPostJob(private val processors: Collection<PostProcessor>)
    : Function<RawPostData, Single<ProcessedPostGroup>>
{
    override fun apply(data: RawPostData): Single<ProcessedPostGroup> {
        return Observable.fromIterable(processors)
                .toMap(PostProcessor::type, { it.process(data) })
                .map {
                    ProcessedPostGroup(
                            channelId = data.channel.id,
                            channelUrl = data.channel.url,
                            postId = data.message.id,
                            posts = it
                    )
                }
    }
}
