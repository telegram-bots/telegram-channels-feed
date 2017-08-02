package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*

class FullPostProcessor : PostProcessor {
    override fun process(postInfo: PostInfo): List<ProcessedPost> {
        TODO("not implemented")
    }

    override fun type() = ProcessType.FULL
}
