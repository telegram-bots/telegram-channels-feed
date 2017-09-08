package com.github.telegram_bots.channels_feed.sender.config

import com.fasterxml.jackson.databind.ObjectMapper
import com.github.telegram_bots.channels_feed.sender.config.properties.SenderProperties
import com.pengrad.telegrambot.TelegramBot
import com.pengrad.telegrambot.TelegramBotAdapter
import org.davidmoten.rx.jdbc.Database
import org.springframework.boot.autoconfigure.amqp.RabbitProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Primary
import org.springframework.core.env.Environment
import java.net.URI

@Configuration
class SenderConfig {
    @Bean
    fun objectMapper(): ObjectMapper = ObjectMapper().findAndRegisterModules()

    @Bean
    fun database(env: Environment): Database = Database.from(env.getProperty("spring.datasource.url"), 10)

    @Bean
    @Primary
    fun rabbitProperties(env: Environment): RabbitProperties {
        val uri = env.getProperty("spring.rabbitmq.url").let { URI(it) }
        val (user, pass) = uri.userInfo?.split(":")
                .let { it?.getOrNull(0) to it?.getOrNull(1) }

        return RabbitProperties().apply {
            host = uri.host
            port = uri.port
            username = user
            password = pass
            virtualHost = uri.path
        }
    }

    @Bean
    fun telegramBot(props: SenderProperties): TelegramBot {
        return TelegramBotAdapter.build(props.botToken)
    }
}
