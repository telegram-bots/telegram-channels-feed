package com.github.telegram_bots.channels_feed.tg.service

import com.github.telegram_bots.channels_feed.tg.domain.Channel
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.jdbc.core.RowMapper
import org.springframework.stereotype.Repository
import java.sql.ResultSet

@Repository
class ChannelRepository(private val jdbc: JdbcTemplate) {
    fun find(url: String): Channel? {
        return jdbc
                .query(
                        "SELECT * FROM Channels WHERE url = ?",
                        arrayOf(url),
                        Mapper
                )
                .firstOrNull()
    }

    fun save(channel: Channel): Channel {
        jdbc.update("""INSERT INTO Channels(telegram_id, hash, url, name, last_post_id, last_sent_id)
            VALUES (?, ?, ?, ?, ?, ?)""",
                channel.telegramId,
                channel.hash,
                channel.url,
                channel.name,
                channel.lastPostId,
                channel.lastSentId
        )

        return find(channel.url)!!
    }

    fun delete(channel: Channel): Boolean {
        return jdbc.update(
                "DELETE FROM Channels WHERE id = ?",
                arrayOf(channel.id)
        ) >= 1
    }

    fun list(limit: Int, offset: Int): List<Channel> {
        return jdbc
                .query(
                        "SELECT * FROM Channels LIMIT ? OFFSET ?",
                        arrayOf(limit, offset),
                        Mapper
                )
    }

    fun updateLastPostId(id: Int, lastPostId: Int): Boolean {
        return jdbc.update(
                "UPDATE Channels SET last_post_id = ? WHERE id = ?",
                lastPostId, id
        ) >= 1
    }

    private object Mapper : RowMapper<Channel> {
        override fun mapRow(rs: ResultSet, rowNum: Int) = Channel(
                id = rs.getInt("id"),
                telegramId = rs.getInt("telegram_id"),
                hash = rs.getLong("hash"),
                url = rs.getString("url"),
                name = rs.getString("name"),
                lastPostId = rs.getInt("last_post_id"),
                lastSentId = rs.getObject("last_sent_id")?.let { it as? Int }
        )
    }
}
