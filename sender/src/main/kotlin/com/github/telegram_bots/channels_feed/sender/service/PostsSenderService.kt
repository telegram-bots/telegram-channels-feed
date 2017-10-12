package com.github.telegram_bots.channels_feed.sender.service

import com.github.telegram_bots.channels_feed.sender.config.properties.SenderProperties
import com.github.telegram_bots.channels_feed.sender.domain.*
import com.github.telegram_bots.channels_feed.sender.domain.ProcessedPost.Mode.AS_IS
import com.github.telegram_bots.channels_feed.sender.domain.ProcessedPostGroup.Type
import com.github.telegram_bots.channels_feed.sender.domain.ProcessedPostGroup.Type.FULL
import com.github.telegram_bots.channels_feed.sender.exception.TelegramException
import com.github.telegram_bots.channels_feed.sender.util.RetryWithDelay
import com.pengrad.telegrambot.TelegramBot
import com.pengrad.telegrambot.model.request.InlineKeyboardButton
import com.pengrad.telegrambot.model.request.InlineKeyboardMarkup
import com.pengrad.telegrambot.model.request.ParseMode
import com.pengrad.telegrambot.request.BaseRequest
import com.pengrad.telegrambot.request.ForwardMessage
import com.pengrad.telegrambot.request.SendMessage
import io.reactivex.Flowable
import io.reactivex.Single
import io.reactivex.rxkotlin.zipWith
import io.reactivex.schedulers.Schedulers
import mu.KLogging
import org.reactivestreams.Subscription
import org.springframework.cloud.stream.annotation.EnableBinding
import org.springframework.cloud.stream.annotation.StreamListener
import org.springframework.cloud.stream.messaging.Sink
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit.*
import javax.annotation.PreDestroy

@Service
@EnableBinding(Sink::class)
class PostsSenderService(
        private val props: SenderProperties,
        private val bot: TelegramBot,
        private val notifications: NotificationsService
) {
    companion object : KLogging()

    private var subscription: Subscription? = null

    @PreDestroy
    fun onDestroy() = subscription?.cancel()

    @StreamListener(Sink.INPUT)
    fun subscribe(group: ProcessedPostGroup) {
        enableExceptionPropagate()

        Single.just(group)
                .delay(props.rateLimit, props.rateLimitUnit)
                .flatMapPublisher { getNotNotified(it) }
                .flatMapSingle { preparePost(it) }
                .flatMapSingle { sendPost(it) }
                .doOnSubscribe { subscription = it }
                .blockingSubscribe(
                        this::markSubscription,
                        this::onError,
                        { markChannel(group) }
                )
    }

    private fun getNotNotified(group: ProcessedPostGroup): Flowable<PostData> {
        return notifications
                .listNotNotified(group.channelId, group.postId)
                .zipWith(Flowable.just(group).repeat())
                .doOnSubscribe { logger.info { "[PROCESSING] $group" } }
    }

    private fun preparePost(data: PostData): Single<RequestData> {
        fun User.getChatId(): Any = redirectUrl?.let { "@$it" } ?: telegramId
        fun ProcessedPostGroup.getPost(type: Type): ProcessedPost {
            return posts.getOrElse(type, { throw IllegalStateException("Impossible to happen") })
        }
        fun ProcessedPost.buildRequest(chatId: Any): BaseRequest<*, *> {
            return SendMessage(chatId, text)
                    .disableWebPagePreview(!previewEnabled)
                    .parseMode(ParseMode.valueOf(mode.name))
                    .replyMarkup(
                            InlineKeyboardMarkup(arrayOf(
                                    InlineKeyboardButton("Mark as read")
                                            .callbackData("mark")
                            ))
                    )
        }

        return Single.just(data)
                .map { (user, group) ->
                    val post = group.getPost(FULL)
                    val chatId = user.getChatId()
                    val request = post.buildRequest(chatId)

                    (user to group) to request
                }
    }

    private fun sendPost(data: RequestData): Single<PostData> {
        return Single.just(data)
                .map { it to bot.execute(it.second) }
                .flatMap(this::handleErrors)
                .retryWhen(RetryWithDelay(
                        tries = 10,
                        delay = 5 to SECONDS,
                        backOff = 2.0,
                        maxDelay = 30 to SECONDS
                ))
                .map { (req) -> req.first }
    }

    private fun markSubscription(data: PostData) {
        val (user, group) = data

        notifications.markSubscription(user.id, group.channelId, group.postId)
                .subscribeOn(Schedulers.io())
                .doOnComplete { logger.info { "[MARK_SUB] ${user.id}:${group.channelId} to ${group.postId}" } }
                .subscribe()
    }

    private fun markChannel(group: ProcessedPostGroup) {
        notifications.markChannel(group.channelId, group.postId)
                .subscribeOn(Schedulers.io())
                .doOnComplete { logger.info { "[MARK_CHANNEL] ${group.channelId} to ${group.postId}" } }
                .subscribe()
    }

    private fun onError(throwable: Throwable) {
        logger.error("[PROCESSING ERROR]", throwable)
        throw throwable
    }

    private fun handleErrors(data: ExchangeData): Single<ExchangeData> {
        val (req, res) = data
        if (res.isOk) return Single.just(data)
        val error = TelegramException(req.second, res)

        logger.warn { "[SEND ERROR] ${error.message}" }

        return when (error.code) {
            403 -> Single.just(data)
            400 -> when (error.description) {
                "Bad Request: message to forward not found" -> Single.just(data)
                "Bad Request: chat not found" -> Single.just(data)
                else -> Single.error(error)
            }
            429 -> Single.timer(error.value / 2, SECONDS).flatMap { Single.error<ExchangeData>(error) }
            else -> Single.error(error)
        }
    }

    private fun enableExceptionPropagate() = Thread.currentThread().setUncaughtExceptionHandler { _, e -> throw e }
}
