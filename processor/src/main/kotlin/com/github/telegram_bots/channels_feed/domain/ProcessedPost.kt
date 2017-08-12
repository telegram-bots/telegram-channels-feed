package com.github.telegram_bots.channels_feed.domain

data class ProcessedPost(
        val text: String? = null,
        val fileId: CachedFileID? = null,
        val previewEnabled: Boolean,
        val mode: Mode
) {
    enum class Mode { HTML, MARKDOWN }
}
