package com.github.telegram_bots.channels_feed.tg.service

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Repository
import java.sql.ResultSet

@Repository
class ChannelRepository(private val jdbc: JdbcTemplate) {
    fun find(telegramId: Int): Channel? {
        return jdbc
                .query(
                        "SELECT * FROM Channels WHERE telegram_id = ?",
                        arrayOf(telegramId),
                        Mapper
                )
                .firstOrNull()
    }

    fun list(limit: Int, offset: Int): List<Channel> {
        return jdbc
                .query(
                        "SELECT * FROM Channels LIMIT ? OFFSET ?",
                        arrayOf(limit, offset),
                        Mapper
                )
    }

    fun updateLastPostId(telegramId: Int, lastPostId: Int): Boolean {
        return jdbc.update(
                "UPDATE Channels SET last_post_id = ? WHERE telegram_id = ?",
                lastPostId, telegramId
        ) >= 1
    }

    private object Mapper : RowMapper<Channel> {
        override fun mapRow(rs: ResultSet, rowNum: Int) = Channel(
                id = rs.getInt("id"),
                telegramId = rs.getInt("telegram_id"),
                hash = rs.getLong("hash"),
                url = rs.getString("url"),
                name = rs.getString("name"),
                lastPostId = rs.getObject("last_post_id")?.let { it as? Int }
        )
    }
}
