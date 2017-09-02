package com.github.telegram_bots.channels_feed.tg.util

import java.net.URI
import java.nio.charset.Charset

val UTF_16LE = Charset.forName("UTF-16LE")!!

fun URI.userInfoParts() = userInfo?.split(":")
        .let { it?.getOrNull(0) to it?.getOrNull(1) }
