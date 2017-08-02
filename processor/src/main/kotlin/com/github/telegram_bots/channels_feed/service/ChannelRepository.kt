package com.github.telegram_bots.channels_feed.service

import com.github.telegram_bots.channels_feed.domain.Channel
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Repository

@Repository
class ChannelRepository(private val jdbc: JdbcTemplate) {
    fun find(telegramId: Long): Channel? = jdbc
            .query(
                    "SELECT * FROM Channels WHERE telegram_id = ?",
                    arrayOf(telegramId),
                    Channel.Mapper()
            )
            .firstOrNull()
}
