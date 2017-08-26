package com.github.telegram_bots.channels_feed.tg.service.jobs

import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.processor.PostProcessor
import io.reactivex.Observable
import java.util.concurrent.Callable

class ProcessPostJob(private val processors: Collection<PostProcessor>, private val data: RawPostData) : Callable<Observable<ProcessedPostGroup>> {
    override fun call(): Observable<ProcessedPostGroup> {
        val posts = processors
                .map { p -> p.type to p.process(data) }
                .toMap()

        return ProcessedPostGroup(
                channelId = data.channel.id,
                channelUrl = data.channel.url,
                postId = data.raw.id,
                posts = posts
        ).let { Observable.just(it) }
    }
}
