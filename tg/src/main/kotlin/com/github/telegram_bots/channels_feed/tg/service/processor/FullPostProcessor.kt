package com.github.telegram_bots.channels_feed.tg.service.processor

import com.github.badoualy.telegram.tl.api.TLInputMediaEmpty
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup.Type.FULL
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.MessageFormatter
import org.springframework.stereotype.Component

@Component
class FullPostProcessor : PostProcessor {
    companion object {
        const val MAX_LENGTH: Int = 4096
    }

    override val type = FULL
    private val formatter = MessageFormatter

    override fun process(data: RawPostData) = when (data.message.media) {
        null, is TLInputMediaEmpty -> textPost(data)
        else -> textPost(data)
    }

    private fun textPost(data: RawPostData): ProcessedPost {
        val firstLink = formatter.extractFirstLink(data)
        val header = formatter.makeHeader(data)
        val text = formatter.processText(firstLink, header, data, MAX_LENGTH)

        return ProcessedPost(text = text, previewEnabled = firstLink != null, mode = HTML)
    }
}
