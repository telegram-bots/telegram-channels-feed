package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*

interface PostProcessor {
    fun process(postInfo: PostInfo): List<ProcessedPost>
    fun type(): ProcessType
}
