package com.github.telegram_bots.channels_feed.tg.service.processor

import com.github.telegram_bots.channels_feed.tg.domain.*
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup.Type.TITLE_ONLY
import org.springframework.stereotype.Component

@Component
class TitleOnlyPostProcessor : PostProcessor {
    override val type = TITLE_ONLY

    override fun process(data: RawPostData) = ProcessedPost(makeHeader(data), previewEnabled = false, mode = HTML)

    private fun makeHeader(data: RawPostData) =
        """<b>new in</b> <a href="https://t.me/${data.channel.url}/${data.raw.id}">${data.channel.name}</a>"""
}
