package com.github.telegram_bots.channels_feed.domain

data class ProcessedPost(
        val text: String,
        val previewEnabled: Boolean,
        val fileId: String? = null,
        val mode: Mode
) {
    enum class Mode { HTML, MARKDOWN }
}
