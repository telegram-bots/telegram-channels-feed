package com.github.telegram_bots.channels_feed.config

import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class ProcessorConfig {
    @Bean
    fun objectMapper() = ObjectMapper()
}
