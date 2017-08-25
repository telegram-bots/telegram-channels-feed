package com.github.telegram_bots.channels_feed.domain

import com.github.telegram_bots.channels_feed.domain.RawPost.Content.Type

data class ProcessedPost(
        val text: String? = null,
        val fileId: CachedFileID? = null,
        val previewEnabled: Boolean,
        val mode: Mode
) {
    enum class Mode { TEXT, HTML, MARKDOWN }
}

data class ProcessedPostGroup(
        val channelId: Long,
        val messageId: Long,
        val posts: Map<Type, List<ProcessedPost>>
) {
    enum class Type { FULL, SHORT, TITLE_ONLY }
}

data class RawPost(
        val channelId: Long,
        val messageId: Long,
        val content: Content,
        val update: Boolean = false
) {
    interface Content {
        val type: Type
        val text: String

        enum class Type(val value: String) {
            TEXT("MessageText"),
            PHOTO("MessagePhoto"),
            UNKNOWN("Unknown")
        }
    }

    data class TextContent(override val type: Type, override val text: String, val entities: List<Entity>) : Content {
        data class Entity(val type: Type, val value: String, val startPos: Int, val endPos: Int, val url: String?) {
            enum class Type(val value: String) {
                PLAIN_LINK("MessageEntityUrl"),
                FORMATTED_LINK("MessageEntityTextUrl"),
                BOLD("MessageEntityBold"),
                ITALIC("MessageEntityItalic"),
                CODE("MessageEntityCode"),
                PRE("MessageEntityPre"),
                UNKNOWN("Unknown");
            }
        }
    }

    data class PhotoContent(override val type: Type, override val text: String, val photoId: FileID) : Content

    data class OtherContent(override val type: Type, override val text: String) : Content
}

data class RawPostData(val raw: RawPost, val channel: Channel, val fileID: CachedFileID?)
