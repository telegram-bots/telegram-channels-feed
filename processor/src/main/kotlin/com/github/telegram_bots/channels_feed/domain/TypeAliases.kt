package com.github.telegram_bots.channels_feed.domain

import com.github.telegram_bots.channels_feed.service.processor.PostProcessor.ProcessType

typealias ProcessedPostGroup = Map<ProcessType, List<ProcessedPost>>
typealias PostInfo = Pair<RawPost, Channel>
