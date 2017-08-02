package com.github.telegram_bots.channels_feed.domain

import org.springframework.jdbc.core.RowMapper
import java.sql.ResultSet

data class Channel(
        val id: Int,
        val telegramId: Long,
        val url: String,
        val name: String,
        val lastMessageId: Long?
) {
    companion object {
        fun empty(telegramId: Long) = Channel(
                id = -1,
                telegramId = telegramId,
                url = "empty",
                name = "REMOVED",
                lastMessageId = null
        )
    }

    class Mapper : RowMapper<Channel> {
        override fun mapRow(rs: ResultSet, rowNum: Int) = Channel(
            id = rs.getInt("id"),
            telegramId = rs.getLong("telegram_id"),
            url = rs.getString("url"),
            name = rs.getString("name"),
            lastMessageId = rs.getObject("last_message_id")?.let { it as? Long }
        )
    }
}
