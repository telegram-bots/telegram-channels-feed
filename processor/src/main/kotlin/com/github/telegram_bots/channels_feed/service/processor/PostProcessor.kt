package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*

interface PostProcessor {
    val type: ProcessedPostGroup.Type

    fun process(postInfo: RawPostData): List<ProcessedPost>
}
