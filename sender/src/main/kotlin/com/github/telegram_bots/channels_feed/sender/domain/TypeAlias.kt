package com.github.telegram_bots.channels_feed.sender.domain

import com.pengrad.telegrambot.request.BaseRequest
import com.pengrad.telegrambot.response.BaseResponse

typealias PostData = Pair<User, ProcessedPostGroup>
typealias RequestData = Pair<PostData, BaseRequest<*, *>>
typealias ExchangeData = Pair<RequestData, BaseResponse>
