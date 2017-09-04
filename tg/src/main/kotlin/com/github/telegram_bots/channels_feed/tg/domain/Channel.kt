package com.github.telegram_bots.channels_feed.tg.domain

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

    fun isEmpty() = telegramId == EMPTY_TG_ID
            || hash == EMPTY_HASH
            || lastPostId == EMPTY_LAST_POST_ID
}
