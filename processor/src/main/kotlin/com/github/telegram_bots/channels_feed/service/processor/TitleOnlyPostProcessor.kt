package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.service.processor.PostProcessor.ProcessType.TITLE_ONLY
import org.springframework.stereotype.Component

@Component
class TitleOnlyPostProcessor : AbstractPostProcessor(TITLE_ONLY) {
    override fun process(postInfo: PostInfo) =
        listOf(ProcessedPost(makeHeader(postInfo), previewEnabled = false, mode = HTML))

    private fun makeHeader(info: PostInfo) =
        """<b>new in</b> <a href="https://t.me/${info.channel.url}">${info.channel.name}</a>"""
}
