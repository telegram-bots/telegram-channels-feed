package com.github.telegram_bots.channels_feed.tg.config.properties

import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.context.annotation.Configuration
import java.nio.file.Path

@Configuration
@ConfigurationProperties("tg")
data class TGProperties(
        var apiId: Int,
        var apiHash: String,
        var phoneNumber: String,
        var model: String,
        var appVersion: String,
        var sysVersion: String,
        var langCode: String,
        var storagePath: Path
)
