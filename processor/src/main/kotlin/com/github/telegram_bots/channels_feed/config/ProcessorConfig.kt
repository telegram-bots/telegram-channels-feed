package com.github.telegram_bots.channels_feed.config

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.module.SimpleModule
import com.github.telegram_bots.channels_feed.domain.RawPost
import com.github.telegram_bots.channels_feed.util.RawPostDeserializer
import org.springframework.boot.autoconfigure.amqp.RabbitProperties
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Primary
import org.springframework.core.env.Environment
import org.springframework.jdbc.core.JdbcTemplate
import java.net.URI
import javax.sql.DataSource

@Configuration
class ProcessorConfig {
    @Bean
    fun objectMapper() = ObjectMapper()
            .findAndRegisterModules()
            .registerModule(SimpleModule().apply { addDeserializer(RawPost::class.java, RawPostDeserializer) })

    @Bean
    fun jdbcTemplate(ds: DataSource) = JdbcTemplate(ds)

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

    @Bean
    @Primary
    fun dataSourceProperties(env: Environment): DataSourceProperties {
        val uri = env.getProperty("CF_DB_URL").let { URI(it) }
        val (user, pass) = uri.userInfoParts()

        return DataSourceProperties().apply {
            username = user
            password = pass
            url = "jdbc:" + uri.toString().replace("//${uri.userInfo}@", "//")
        }
    }

   private fun URI.userInfoParts() = userInfo?.split(":")
           .let { it?.getOrNull(0) to it?.getOrNull(1) }
}
