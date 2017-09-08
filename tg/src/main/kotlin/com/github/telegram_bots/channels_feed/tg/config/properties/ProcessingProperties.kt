package com.github.telegram_bots.channels_feed.tg.config.properties

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import java.util.concurrent.TimeUnit

@Configuration
@ConfigurationProperties("processing")
data class ProcessingProperties(
        var channelsIntervalMin: Long,
        var channelsIntervalMax: Long,
        var channelsIntervalTimeUnit: TimeUnit,
        var postsBatchSize: Int,
        var postsIntervalMin: Long,
        var postsIntervalMax: Long,
        var postsIntervalTimeUnit: TimeUnit
)
