package com.github.telegram_bots.channels_feed.extension

import java.nio.charset.Charset


val UTF_16LE = Charset.forName("UTF-16LE")!!
fun String.toUTF16ByteArray() = toByteArray(UTF_16LE)
fun ByteArray.asUTF16String() = String(this, UTF_16LE)
