package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessType.SHORT
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent
import org.springframework.stereotype.Component

@Component
class ShortPostProcessor(private val textLimit: Int = 200) : AbstractPostProcessor() {
    override fun process(postInfo: PostInfo): List<ProcessedPost> {
        val fileId = extractFileId(postInfo)
        val firstLink = extractFirstLink(postInfo, fileId != null)
        val text = (firstLink ?: "") + processText(postInfo)

        return listOf(
                ProcessedPost(
                        text = text,
                        previewEnabled = firstLink != null,
                        fileId = fileId,
                        mode = HTML
                )
        )
    }

    override fun processText(info: PostInfo) = (makeHeader(info) + "\n\n" + info.first.content.text.replaceHTMLTags())
            .shorten(textLimit)

    override fun type() = SHORT

    private fun makeHeader(info: PostInfo) = when (info.first.content) {
        is TextContent -> """<a href="https://t.me/${info.second.url}">${info.second.name}</a>:"""
        else -> """via ${info.second.name}(@${info.second.url})"""
    }

    private fun extractFirstLink(info: PostInfo, hasFile: Boolean) = if (!hasFile) extractFirstLink(info) else null

    private fun String.shorten(limit: Int, placeholder: String = "...") =
            if (length <= limit) this
            else substring(0, limit - placeholder.length) + placeholder
}
