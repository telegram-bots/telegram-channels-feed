package com.github.telegram_bots.channels_feed.domain

import com.github.telegram_bots.channels_feed.service.processor.PostProcessor

data class ProcessedPostGroup(
        val channelId: Long,
        val messageId: Long,
        val posts: Map<PostProcessor.ProcessType, List<ProcessedPost>>
)
