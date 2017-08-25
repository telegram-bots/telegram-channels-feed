package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import com.github.telegram_bots.channels_feed.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.domain.ProcessedPostGroup.Type.TITLE_ONLY
import org.springframework.stereotype.Component

@Component
class TitleOnlyPostProcessor : AbstractPostProcessor(TITLE_ONLY) {
    override fun process(postInfo: RawPostData) =
        listOf(ProcessedPost(makeHeader(postInfo), previewEnabled = false, mode = HTML))

    private fun makeHeader(info: RawPostData) =
        """<b>new in</b> <a href="https://t.me/${info.channel.url}">${info.channel.name}</a>"""
}
