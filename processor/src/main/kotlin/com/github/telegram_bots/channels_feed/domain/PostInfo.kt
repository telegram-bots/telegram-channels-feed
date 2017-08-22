package com.github.telegram_bots.channels_feed.domain

data class PostInfo(val raw: RawPost, val channel: Channel, val fileID: CachedFileID?)
