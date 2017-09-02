package com.github.telegram_bots.channels_feed.tg.service.processor

import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup.Type
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData

interface PostProcessor {
    val type: Type

    fun process(data: RawPostData): ProcessedPost
}
