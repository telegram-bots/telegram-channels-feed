package com.github.telegram_bots.channels_feed.sender.config.properties

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import java.util.concurrent.TimeUnit

@Configuration
@ConfigurationProperties("sender")
data class SenderProperties(
        var botToken: String,
        var rateLimit: Long,
        var rateLimitUnit: TimeUnit
)
