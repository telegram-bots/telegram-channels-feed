package com.github.telegram_bots.channels_feed.service

import com.github.telegram_bots.channels_feed.domain.Channel
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Repository
import java.sql.ResultSet

@Repository
class ChannelRepository(private val jdbc: JdbcTemplate) {
    fun find(telegramId: Long): Channel {
        return jdbc
                .query(
                        "SELECT * FROM Channels WHERE telegram_id = ?",
                        arrayOf(telegramId),
                        Mapper
                )
                .first()
                ?: Channel.empty(telegramId)
    }

    private object Mapper : RowMapper<Channel> {
        override fun mapRow(rs: ResultSet, rowNum: Int) = Channel(
                id = rs.getLong("id"),
                telegramId = rs.getLong("telegram_id"),
                url = rs.getString("url"),
                name = rs.getString("name"),
                lastMessageId = rs.getObject("last_message_id")?.let { it as? Long }
        )
    }
}
