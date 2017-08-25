package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.TEXT
import com.github.telegram_bots.channels_feed.domain.ProcessedPostGroup.Type.FULL
import org.springframework.stereotype.Component

@Component
class FullPostProcessor : AbstractPostProcessor(FULL) {
    override fun process(postInfo: RawPostData): List<ProcessedPost> {
        val fileId = postInfo.fileID
        val firstLink = extractFirstLink(postInfo)
        val header = makeHeader(postInfo)
        val text = processText(postInfo)

        return when (fileId) {
            null -> splitToTextPost(firstLink, header, text)
            else -> splitToMediaPost(fileId, firstLink, header, text)
        }
    }

    private fun splitToMediaPost(fileId: CachedFileID, link: Link, header: Header, text: String) = listOf(
            ProcessedPost(fileId = fileId, previewEnabled = false, mode = TEXT),
            ProcessedPost((link ?: "") + header + text, previewEnabled = link != null, mode = HTML)
    )

    private fun splitToTextPost(link: Link, header: Header, text: String): List<ProcessedPost> {
        val linkText = link ?: ""
        val totalLength = sequenceOf(linkText, header, text).map(String::length).sum()
        val previewEnabled = link != null

        if (totalLength <= MAX_MESSAGE_LENGTH) {
            return listOf(ProcessedPost(linkText + header + text, previewEnabled = previewEnabled, mode = HTML))
        }

        return listOf(
                ProcessedPost(
                        linkText + header + text.substring(0..MAX_MESSAGE_LENGTH - 3) + "...",
                        previewEnabled = previewEnabled,
                        mode = HTML
                ),
                ProcessedPost(
                        "..." + header + text.substring(MAX_MESSAGE_LENGTH - 3..totalLength),
                        previewEnabled = false,
                        mode = HTML
                )
        )
    }

    private fun makeHeader(info: RawPostData) =
        """<a href="https://t.me/${info.channel.url}">${info.channel.name}</a>:$SEPARATOR"""
}
