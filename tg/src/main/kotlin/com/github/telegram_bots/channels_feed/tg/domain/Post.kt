package com.github.telegram_bots.channels_feed.tg.domain

import com.github.badoualy.telegram.tl.api.TLMessage

data class ProcessedPost(
        val text: String? = null,
        val previewEnabled: Boolean = false,
        val mode: Mode
) {
    enum class Mode { AS_IS, TEXT, HTML, MARKDOWN }
}

data class ProcessedPostGroup(
        val channelId: Int,
        val channelUrl: String,
        val postId: Int,
        val posts: Map<Type, ProcessedPost>
) {
    enum class Type { FULL, SHORT, TITLE_ONLY }
}

data class RawPostData(val raw: TLMessage, val channel: Channel)
