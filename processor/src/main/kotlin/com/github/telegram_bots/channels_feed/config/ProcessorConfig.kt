package com.github.telegram_bots.channels_feed.config

import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.jdbc.core.JdbcTemplate
import javax.sql.DataSource

@Configuration
class ProcessorConfig {
    @Bean
    fun objectMapper() = ObjectMapper().findAndRegisterModules()!!

    @Bean
    fun jdbcTemplate(ds: DataSource) = JdbcTemplate(ds)
}
