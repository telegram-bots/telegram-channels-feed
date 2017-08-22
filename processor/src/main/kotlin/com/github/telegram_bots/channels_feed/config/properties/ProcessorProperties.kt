package com.github.telegram_bots.channels_feed.config.properties

import com.github.telegram_bots.channels_feed.domain.URL
import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import java.net.URI


@Configuration
@ConfigurationProperties("processor")
data class ProcessorProperties(
        var botToken: String,
        var tgCliUrl: URL
) {
    val tgCliID: String
        get() = URI(tgCliUrl).userInfo
}
