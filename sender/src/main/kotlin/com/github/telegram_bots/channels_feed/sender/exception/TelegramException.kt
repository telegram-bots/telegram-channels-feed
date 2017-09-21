package com.github.telegram_bots.channels_feed.sender.exception

import com.pengrad.telegrambot.request.BaseRequest
import com.pengrad.telegrambot.response.BaseResponse

class TelegramException(request: BaseRequest<*, *>, response: BaseResponse)
    : RuntimeException("[${response.errorCode()}] ${response.description()} $request", null, false, false) {
    val code = response.errorCode()
    val description = response.description()
    val value: Long = response.description().split(" ").lastOrNull()?.toLongOrNull() ?: 1
}
