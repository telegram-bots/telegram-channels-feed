package com.github.telegram_bots.channels_feed.sender.domain

import java.sql.ResultSet

data class User(val id: Int, val telegramId: Long, val redirectUrl: String?) {
    constructor(rs: ResultSet) : this(
            id = rs.getInt("id"),
            telegramId = rs.getLong("telegram_id"),
            redirectUrl = rs.getString("redirect_url")
    )
}
