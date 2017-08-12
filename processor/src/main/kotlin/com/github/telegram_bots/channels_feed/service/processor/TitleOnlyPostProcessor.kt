package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.service.processor.PostProcessor.ProcessType.TITLE_ONLY
import org.springframework.stereotype.Component

@Component
class TitleOnlyPostProcessor : AbstractPostProcessor() {
    override fun process(postInfo: PostInfo) = listOf(
            ProcessedPost(makeTitle(postInfo), previewEnabled = false, mode = HTML)
    )

    override fun type() = TITLE_ONLY

    fun makeTitle(info: PostInfo) = """<b>new in</b> <a href="https://t.me/${info.second.url}">${info.second.name}</a>"""
}
