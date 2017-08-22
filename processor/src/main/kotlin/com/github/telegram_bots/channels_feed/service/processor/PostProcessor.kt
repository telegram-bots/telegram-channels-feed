package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*

interface PostProcessor {
    val type: ProcessType

    fun process(postInfo: PostInfo): List<ProcessedPost>

    enum class ProcessType { FULL, SHORT, TITLE_ONLY }
}
