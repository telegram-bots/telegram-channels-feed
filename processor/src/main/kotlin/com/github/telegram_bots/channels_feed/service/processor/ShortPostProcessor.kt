package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent
import com.github.telegram_bots.channels_feed.domain.ProcessedPostGroup.Type.SHORT
import org.springframework.stereotype.Component

@Component
class ShortPostProcessor : AbstractPostProcessor(SHORT) {
    override fun process(postInfo: RawPostData): List<ProcessedPost> {
        val fileId = postInfo.fileID
        val firstLink = extractFirstLink(postInfo, hasFile = fileId != null)
        val header = makeHeader(postInfo)
        val text = processText(firstLink, header, postInfo)

        return listOf(ProcessedPost(text, fileId, previewEnabled = firstLink != null, mode = HTML))
    }

    private fun processText(link: Link, header: Header, info: RawPostData) =
            ((link ?: "") + header + processText(info)).shorten(MAX_CAPTION_LENGTH)

    private fun makeHeader(info: RawPostData) = when (info.raw.content) {
        is TextContent -> """<a href="https://t.me/${info.channel.url}">${info.channel.name}</a>:$SEPARATOR"""
        else -> """via ${info.channel.name}(@${info.channel.url})$SEPARATOR"""
    }

    private fun extractFirstLink(info: RawPostData, hasFile: Boolean) = if (hasFile) null else extractFirstLink(info)

    private fun String.shorten(limit: Int, placeholder: String = "...") =
            if (length <= limit) this
            else substring(0, limit - placeholder.length) + placeholder
}
