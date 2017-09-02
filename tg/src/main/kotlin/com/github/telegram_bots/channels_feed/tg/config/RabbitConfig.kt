package com.github.telegram_bots.channels_feed.tg.config

import com.github.telegram_bots.channels_feed.tg.util.userInfoParts
import org.springframework.boot.autoconfigure.amqp.RabbitProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Primary
import org.springframework.core.env.Environment
import java.net.URI

@Configuration
class RabbitConfig {
    @Bean
    @Primary
    fun rabbitProperties(env: Environment): RabbitProperties {
        val uri = env.getProperty("CF_RABBIT_URL").let { URI(it) }
        val (user, pass) = uri.userInfoParts()

        return RabbitProperties().apply {
            host = uri.host
            port = uri.port
            username = user
            password = pass
            virtualHost = uri.path
        }
    }
}
