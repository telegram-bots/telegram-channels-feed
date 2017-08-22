package com.github.telegram_bots.channels_feed.domain

import java.time.Instant

data class RawPost(
        val channelId: Long,
        val messageId: Long,
        val date: Instant,
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

    data class TextContent(override val type: Content.Type, override val text: String, val entities: List<Entity>) : Content {
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

    data class PhotoContent(override val type: Content.Type, override val text: String, val photoId: FileID) : Content

    data class OtherContent(override val type: Content.Type, override val text: String) : Content
}
