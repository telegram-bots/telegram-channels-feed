package com.github.telegram_bots.channels_feed.tg.service.processor

import com.github.telegram_bots.channels_feed.tg.domain.*
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost.Mode.AS_IS
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup.Type.FULL
import org.springframework.stereotype.Component

@Component
class FullPostProcessor : PostProcessor {
    override val type = FULL

    override fun process(data: RawPostData) = ProcessedPost(mode = AS_IS)
}
