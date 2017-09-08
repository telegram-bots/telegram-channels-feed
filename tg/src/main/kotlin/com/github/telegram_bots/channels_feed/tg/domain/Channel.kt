package com.github.telegram_bots.channels_feed.tg.domain

import java.sql.ResultSet

data class Channel(
        val id: Int,
        val telegramId: Int,
        val hash: Long,
        val url: String,
        val name: String,
        val lastPostId: Int,
        val lastSentId: Int?
) {
    companion object {
        const val EMPTY_TG_ID = -1
        const val EMPTY_HASH = -1L
        const val EMPTY_LAST_POST_ID = -1
    }

    constructor(rs: ResultSet) : this(
        id = rs.getInt("id"),
        telegramId = rs.getObject("telegram_id")?.let { it as? Int } ?: EMPTY_TG_ID,
        hash = rs.getObject("hash")?.let { it as? Long } ?: EMPTY_HASH,
        url = rs.getString("url"),
        name = rs.getString("name"),
        lastPostId = rs.getObject("last_post_id")?.let { it as? Int } ?: EMPTY_LAST_POST_ID,
        lastSentId = rs.getObject("last_sent_id")?.let { it as? Int }
    )

    fun isEmpty() = telegramId == EMPTY_TG_ID
            || hash == EMPTY_HASH
            || lastPostId == EMPTY_LAST_POST_ID
}
