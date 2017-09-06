package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.TelegramClient
import com.github.badoualy.telegram.tl.api.auth.TLAuthorization
import com.github.badoualy.telegram.tl.exception.RpcErrorException
import com.github.telegram_bots.channels_feed.tg.config.properties.TGProperties
import mu.KLogging
import org.springframework.stereotype.Service
import java.util.*
import javax.annotation.PostConstruct

@Service
class TGAuthorizer(private val props: TGProperties, private val client: TelegramClient) {
    companion object : KLogging()

    @PostConstruct
    fun init() = authorize()

    fun authorize() {
        try {
            if (isAuthorized()) return

            signIn(sentCode = sendAuthCode(), typedCode = getTypedAuthCode())
                    .let(this::getAuthStatus)
                    .let(logger::info)
        } catch (e: Exception) {
            onError(e)
        }
    }

    private fun isAuthorized(): Boolean {
        return try {
            client.accountGetAuthorizations()
            true
        } catch (e: RpcErrorException) {
            if (e.tag.equals("AUTH_KEY_UNREGISTERED", true)) false
            else throw e
        }
    }

    private fun signIn(sentCode: String, typedCode: String): TLAuthorization {
        return try {
            client.authSignIn(props.phoneNumber, sentCode, typedCode)
        } catch (e: RpcErrorException) {
            if (!e.tag.equals("SESSION_PASSWORD_NEEDED", true)) throw e
            client.authCheckPassword(getTypedTwoStepAuthCode())
        }
    }

    private fun sendAuthCode() = client.authSendCode(false, props.phoneNumber, true)
            .phoneCodeHash

    private fun getTypedAuthCode() = logger.info { "Enter authentication code: " }
            .run { Scanner(System.`in`).nextLine() }

    private fun getTypedTwoStepAuthCode() = logger.info { "Enter two-step auth password: " }
            .run { Scanner(System.`in`).nextLine() }

    private fun getAuthStatus(auth: TLAuthorization)= auth.user.asUser
            .run { "You are now signed in as $firstName $lastName @$username" }

    private fun onError(throwable: Throwable) = logger.error("Failed to authorize", throwable)
            .also { throw throwable }
}
