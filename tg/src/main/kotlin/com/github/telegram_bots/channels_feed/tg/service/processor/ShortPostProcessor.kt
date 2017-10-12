package com.github.telegram_bots.channels_feed.tg.service.processor

import com.github.badoualy.telegram.tl.api.TLInputMediaEmpty
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup.Type.SHORT
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import com.github.telegram_bots.channels_feed.tg.service.MessageFormatter
import org.springframework.stereotype.Component
import java.nio.charset.Charset

@Component
class ShortPostProcessor : PostProcessor {
    companion object {
        const val MAX_LENGTH: Int = 200
    }

    override val type = SHORT
    private val formatter = MessageFormatter

    override fun process(data: RawPostData) = when (data.message.media) {
        null, is TLInputMediaEmpty -> textPost(data)
        else -> textPost(data)
    }

    private fun textPost(data: RawPostData): ProcessedPost {
        val firstLink = formatter.extractFirstLink(data)
        val header = formatter.makeHeader(data)
        val text = formatter.processText(firstLink, header, data).shorten(MAX_LENGTH)

        return ProcessedPost(text = text, previewEnabled = firstLink != null, mode = HTML)
    }

    private fun String.shorten(limit: Int, placeholder: String = "...") =
            if (length <= limit) this
            else substring(0, limit - placeholder.length) + placeholder
}
