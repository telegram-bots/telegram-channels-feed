package com.github.telegram_bots.channels_feed.service

import com.github.telegram_bots.channels_feed.domain.CachedFileID
import com.github.telegram_bots.channels_feed.domain.FileID
import org.springframework.stereotype.Service


@Service
class TelegramCachingService {
    fun compute(fileId: FileID): CachedFileID {
        return ""
    }
}

