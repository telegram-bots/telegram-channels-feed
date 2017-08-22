package com.github.telegram_bots.channels_feed.service

import com.fasterxml.jackson.databind.ObjectMapper
import com.github.kittinunf.fuel.core.DataPart
import com.github.kittinunf.fuel.core.FuelError
import com.github.kittinunf.fuel.core.Response
import com.github.kittinunf.fuel.httpGet
import com.github.kittinunf.fuel.httpUpload
import com.github.kittinunf.fuel.rx.rx_response
import com.github.kittinunf.fuel.rx.rx_responseString
import com.github.kittinunf.result.Result
import com.github.telegram_bots.channels_feed.config.properties.ProcessorProperties
import com.github.telegram_bots.channels_feed.domain.CachedFileID
import com.github.telegram_bots.channels_feed.domain.FileID
import com.github.telegram_bots.channels_feed.domain.URL
import com.github.telegram_bots.channels_feed.util.RetryWithDelay
import io.reactivex.Single
import mu.KotlinLogging
import org.springframework.cache.annotation.Cacheable
import org.springframework.stereotype.Service
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.TimeUnit.SECONDS

@Service
class TelegramCachingService(private val props: ProcessorProperties, private val jsonMapper: ObjectMapper) {
    private val log = KotlinLogging.logger {}
    private val params by lazy { listOf("chat_id" to props.tgCliID) }

    @Cacheable("telegram")
    fun compute(fileId: FileID): CachedFileID {
        return Single.just(fileId)
                .map(this::createResolveLink)
                .flatMap(this::resolve)
                .map(this::createDownloadLink)
                .flatMap(this::download)
                .map(this::createUploadLink)
                .flatMap(this::upload)
                .retryWhen(RetryWithDelay(tries = 10, delay = 5 to SECONDS, backOff = 2.0, maxDelay = 30 to SECONDS))
                .blockingGet()
    }

    private fun createResolveLink(fileId: FileID): URL = "https://api.telegram.org/bot${props.botToken}/getFile?file_id=$fileId"

    private fun resolve(url: URL): Single<String> {
        return url.httpGet()
                .rx_responseString()
                .flatMap { it.foldResult() }
                .map(jsonMapper::readTree)
                .flatMap { it.path("result")
                        .path("file_path")
                        .textValue()
                        .singleOrError()
                }
                .doOnSuccess { log.debug { "Resolved file_path: $it" } }
                .cache()
    }

    private fun createDownloadLink(path: String): URL = "https://api.telegram.org/file/bot${props.botToken}/$path"

    private fun download(url: URL): Single<Path> {
        return url.httpGet()
                .rx_response()
                .flatMap { it.foldResult() }
                .map { content -> Files.createTempFile("temp", ".tmp") to content }
                .map { (path, content) -> Files.write(path, content) }
                .doOnSuccess { log.debug { "Downloaded to: $it" } }
                .cache()
    }

    private fun createUploadLink(path: Path): Pair<URL, Path> = "https://api.telegram.org/bot${props.botToken}/sendPhoto" to path

    private fun upload(pair: Pair<URL, Path>): Single<String> {
        val (url, path) = pair

        return url.httpUpload(parameters = params)
                .dataParts { _, _ -> listOf(DataPart(path.toFile(), name = "photo"))}
                .rx_responseString()
                .flatMap { it.foldResult() }
                .map(jsonMapper::readTree)
                .flatMap { it.path("result")
                        .path("photo")
                        .iterator()
                        .asSequence()
                        .maxBy { it.path("file_size").asLong() }
                        .singleOrError()
                }
                .flatMap { it.path("file_id").textValue().singleOrError() }
                .doOnSuccess { log.debug { "Uploaded as: $it" } }
                .doAfterSuccess {
                    try { Files.deleteIfExists(path) }
                    catch (e: Exception) { log.warn { "Failed to delete temp-file" }}
                }
    }

    private fun <T : Any> T?.singleOrError() = this?.let { Single.just(it) } ?: Single.error { CachingFailedException() }

    private fun <T : Any> Pair<Response, Result<T, FuelError>>.foldResult() = second.fold(
            { Single.just(it) },
            { Single.error { CachingFailedException() } }
    )

    private class CachingFailedException : Exception("Failed to cache")
}
