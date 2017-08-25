package com.github.telegram_bots.channels_feed.domain

data class Channel(
        val id: Long,
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
}
