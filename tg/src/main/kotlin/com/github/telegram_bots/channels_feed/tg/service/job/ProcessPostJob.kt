package com.github.telegram_bots.channels_feed.tg.service.job

import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.processor.PostProcessor
import io.reactivex.Observable
import io.reactivex.Single
import java.util.concurrent.Callable

class ProcessPostJob(
        private val processors: Collection<PostProcessor>,
        private val data: RawPostData
) : Callable<Single<ProcessedPostGroup>> {
    override fun call(): Single<ProcessedPostGroup> {
        return Observable.fromIterable(processors)
                .map { it.type to it.process(data) }
                .toMap({ it.first }, { it.second })
                .map {
                    ProcessedPostGroup(
                            channelId = data.channel.id,
                            channelUrl = data.channel.url,
                            postId = data.raw.id,
                            posts = it
                    )
                }
    }
}
