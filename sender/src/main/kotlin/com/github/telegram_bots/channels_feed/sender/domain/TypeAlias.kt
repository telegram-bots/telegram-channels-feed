package com.github.telegram_bots.channels_feed.sender.domain

import com.pengrad.telegrambot.request.BaseRequest

typealias PostData = Pair<User, ProcessedPostGroup>
typealias RequestData = Pair<PostData, BaseRequest<*, *>>
