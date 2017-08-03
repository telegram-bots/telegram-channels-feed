package com.github.telegram_bots.channels_feed.service.processor

import com.github.telegram_bots.channels_feed.domain.*
import org.springframework.stereotype.Component

@Component
class TitleOnlyPostProcessor : PostProcessor {
    override fun process(postInfo: PostInfo) = listOf(
            ProcessedPost(
                    text = """<b>new in</b> <a href="https://t.me/${postInfo.second.url}">${postInfo.second.name}</a>""",
                    previewEnabled = false,
                    mode = ProcessedPost.Mode.HTML
            )
    )

    override fun type() = ProcessType.TITLE_ONLY
}
