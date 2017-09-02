package com.github.telegram_bots.channels_feed.tg.config

import com.fasterxml.jackson.databind.ObjectMapper
import com.github.badoualy.telegram.api.Kotlogram
import com.github.badoualy.telegram.api.TelegramApiStorage
import com.github.badoualy.telegram.api.TelegramApp
import com.github.badoualy.telegram.api.TelegramClient
import com.github.telegram_bots.channels_feed.tg.config.properties.TGProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class TGConfig {
    @Bean
    fun objectMapper(): ObjectMapper = ObjectMapper().findAndRegisterModules()

    @Bean
    fun telegramApp(props: TGProperties): TelegramApp {
        return TelegramApp(
                props.apiId,
                props.apiHash,
                props.model,
                props.sysVersion,
                props.appVersion,
                props.langCode
        )
    }

    @Bean
    fun telegramClient(app: TelegramApp, configStorage: TelegramApiStorage): TelegramClient {
        return Kotlogram.getDefaultClient(app, configStorage)
    }
}
