package com.github.telegram_bots.channels_feed.tg.domain

data class Channel(
        val id: Int,
        val telegramId: Int,
        val hash: Long,
        val url: String,
        val name: String,
        val lastPostId: Int?
)
