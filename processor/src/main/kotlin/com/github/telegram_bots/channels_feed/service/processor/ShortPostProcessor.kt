package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent
import com.github.telegram_bots.channels_feed.service.processor.PostProcessor.ProcessType.SHORT
import org.springframework.stereotype.Component

@Component
class ShortPostProcessor : AbstractPostProcessor() {
    override fun process(postInfo: PostInfo): List<ProcessedPost> {
        val fileId = extractFileId(postInfo)
        val firstLink = extractFirstLink(postInfo, hasFile = fileId != null)
        val header = makeHeader(postInfo)
        val text = processText(firstLink, header, postInfo)

        return listOf(ProcessedPost(text, fileId, previewEnabled = firstLink != null, mode = HTML))
    }

    override fun type() = SHORT

    private fun processText(link: Link, header: Header, info: PostInfo): String {
        return ((link ?: "") + header + info.first.content.text.replaceHTMLTags()).shorten(MAX_CAPTION_LENGTH)
    }

    private fun makeHeader(info: PostInfo) = when (info.first.content) {
        is TextContent -> """<a href="https://t.me/${info.second.url}">${info.second.name}</a>:$SEPARATOR"""
        else -> """via ${info.second.name}(@${info.second.url})$SEPARATOR"""
    }

    private fun extractFirstLink(info: PostInfo, hasFile: Boolean) = if (hasFile) null else extractFirstLink(info)

    private fun String.shorten(limit: Int, placeholder: String = "...") =
            if (length <= limit) this
            else substring(0, limit - placeholder.length) + placeholder
}
