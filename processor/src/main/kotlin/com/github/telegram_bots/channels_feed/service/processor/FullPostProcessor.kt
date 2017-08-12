package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.service.processor.PostProcessor.ProcessType.FULL
import org.springframework.stereotype.Component

@Component
class FullPostProcessor : AbstractPostProcessor() {
    override fun process(postInfo: PostInfo): List<ProcessedPost> {
        val fileId = extractFileId(postInfo)
        val firstLink = extractFirstLink(postInfo)
        val header = makeHeader(postInfo)
        val text = processText(postInfo)

        return when (fileId) {
            null -> splitToTextPost(firstLink, header, text)
            else -> splitToMediaPost(fileId, firstLink, header, text)
        }
    }

    override fun type() = FULL

    private fun processText(info: PostInfo) = info.first.content.text.replaceHTMLTags()

    private fun splitToMediaPost(fileId: CachedFileID, link: Link, header: Header, text: String) = listOf(
            ProcessedPost(fileId = fileId, previewEnabled = false, mode = HTML),
            ProcessedPost((link ?: "") + header + text, previewEnabled = link != null, mode = HTML)
    )

    private fun splitToTextPost(link: Link, header: Header, text: String): List<ProcessedPost> {
        val totalLength = sequenceOf(link ?: "", header, text).map(String::length).sum()

        if (totalLength <= MAX_MESSAGE_LENGTH) {
            return listOf(ProcessedPost((link ?: "") + header + text, previewEnabled = link != null, mode = HTML))
        }

        return listOf(
                ProcessedPost(
                        (link ?: "") + header + text.substring(0..MAX_MESSAGE_LENGTH - 3) + "...",
                        previewEnabled = link != null,
                        mode = HTML
                ),
                ProcessedPost(
                        "..." + header + text.substring(MAX_MESSAGE_LENGTH - 3..totalLength),
                        previewEnabled = false,
                        mode = HTML
                )
        )
    }

    private fun makeHeader(info: PostInfo): Header {
        return """<a href="https://t.me/${info.second.url}">${info.second.name}</a>:$SEPARATOR"""
    }
}
