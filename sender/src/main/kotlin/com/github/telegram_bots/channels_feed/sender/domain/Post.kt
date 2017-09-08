package com.github.telegram_bots.channels_feed.sender.domain

data class ProcessedPost(
        val text: String? = null,
        val previewEnabled: Boolean = false,
        val mode: Mode
) {
    enum class Mode { AS_IS, TEXT, HTML, Markdown }
}

data class ProcessedPostGroup(
        val channelId: Int,
        val channelUrl: String,
        val postId: Int,
        val posts: Map<Type, ProcessedPost>
) {
    enum class Type { FULL, SHORT, TITLE_ONLY }
}
