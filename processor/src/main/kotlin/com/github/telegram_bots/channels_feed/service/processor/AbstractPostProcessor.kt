package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.PostInfo
import com.github.telegram_bots.channels_feed.domain.RawPost.*
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity.Type
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity.Type.*
import com.github.telegram_bots.channels_feed.extension.asUTF16String

abstract class AbstractPostProcessor : PostProcessor {
    protected abstract fun processText(info: PostInfo): String

    protected fun extractFirstLink(info: PostInfo): String? {
        fun Type.isLink() = this == PLAIN_LINK || this == FORMATTED_LINK

        val content = info.first.content as? TextContent ?: return null

        return content
                .entities
                .find { it.type.isLink() }
                ?.let {
                    when (it.type) {
                        FORMATTED_LINK -> it.url
                        PLAIN_LINK -> it.extractValue(content.utf16TextBytes).asUTF16String()
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
