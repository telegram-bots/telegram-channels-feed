package com.github.telegram_bots.channels_feed.tg.service

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Repository
import java.sql.ResultSet

@Repository
class ChannelRepository(private val jdbc: JdbcTemplate) {
    fun update(channel: Channel): Channel {
        jdbc.update(
                """
                | UPDATE Channels
                | SET telegram_id = ?, hash = ?, url = ?, name = ?, last_post_id = ?
                | WHERE id = ?
                """.trimMargin(),
                channel.telegramId,
                channel.hash,
                channel.url,
                channel.name,
                channel.lastPostId,
                channel.id
        )

        return channel
    }

    fun list(limit: Int, offset: Int): List<Channel> {
        return jdbc.query("SELECT * FROM Channels LIMIT ? OFFSET ?", arrayOf(limit, offset), Mapper)
    }

    private object Mapper : RowMapper<Channel> {
        override fun mapRow(rs: ResultSet, rowNum: Int) = Channel(
                id = rs.getInt("id"),
                telegramId = rs.getObject("telegram_id")?.let { it as? Int } ?: Channel.EMPTY_TG_ID,
                hash = rs.getObject("hash")?.let { it as? Long } ?: Channel.EMPTY_HASH,
                url = rs.getString("url"),
                name = rs.getString("name"),
                lastPostId = rs.getObject("last_post_id")?.let { it as? Int } ?: Channel.EMPTY_LAST_POST_ID,
                lastSentId = rs.getObject("last_sent_id")?.let { it as? Int }
        )
    }
}
