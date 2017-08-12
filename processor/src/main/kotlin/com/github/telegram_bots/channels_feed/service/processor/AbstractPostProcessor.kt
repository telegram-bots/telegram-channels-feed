package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.Link
import com.github.telegram_bots.channels_feed.domain.PostInfo
import com.github.telegram_bots.channels_feed.domain.RawPost.*
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity.Type
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity.Type.*
import com.github.telegram_bots.channels_feed.extension.UTF_16LE

abstract class AbstractPostProcessor : PostProcessor {
    protected val MAX_MESSAGE_LENGTH: Int = 4096
    protected val MAX_CAPTION_LENGTH: Int = 200
    protected val SEPARATOR: String = "\n\n"

    protected fun extractFirstLink(info: PostInfo): Link {
        fun Type.isLink() = this == PLAIN_LINK || this == FORMATTED_LINK

        val content = info.first.content as? TextContent ?: return null

        return content
                .entities
                .find { it.type.isLink() }
                ?.let {
                    when (it.type) {
                        FORMATTED_LINK -> it.url
                        PLAIN_LINK -> it.extractValue(content.utf16TextBytes).let { String(it, UTF_16LE) }
                        else -> null
                    }
                }
                ?.let { """<a href="$it">\xad</a>""" }
    }

    protected fun extractFileId(info: PostInfo) = when (info.first.content) {
        is PhotoContent -> (info.first.content as PhotoContent).photoId
        else -> null
    }

    protected fun String.replaceHTMLTags() = replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

    protected fun Entity.extractValue(bytes: ByteArray) = bytes.sliceArray(offset * 2..(length + offset) * 2)
}
