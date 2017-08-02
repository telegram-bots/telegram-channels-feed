package com.github.telegram_bots.channels_feed.domain

data class ProcessedPost(
        private val text: String,
        private val previewEnabled: Boolean,
        private val fileId: String? = null,
        private val mode: Mode = ProcessedPost.Mode.HTML
) {
    enum class Mode { HTML, MARKDOWN }
}
