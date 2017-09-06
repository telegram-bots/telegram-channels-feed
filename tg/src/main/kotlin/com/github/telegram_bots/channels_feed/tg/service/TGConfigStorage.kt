package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.TelegramApiStorage
import com.github.badoualy.telegram.mtproto.auth.AuthKey
import com.github.badoualy.telegram.mtproto.model.DataCenter
import com.github.badoualy.telegram.mtproto.model.MTSession
import com.github.telegram_bots.channels_feed.tg.config.properties.TGProperties
import org.springframework.stereotype.Component
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption.*

@Component
class TGConfigStorage(private val props: TGProperties) : TelegramApiStorage {
    private val auth = "auth".prepare()
    private val separator = "\uD83D\uDD24"

    override fun saveAuthKey(authKey: AuthKey) = write(0, authKey.key.joinToString(separator))

    override fun loadAuthKey() = read(0) { it.split(separator).map(String::toByte).toByteArray().let(::AuthKey) }

    override fun deleteAuthKey() = delete(0)

    override fun saveDc(dataCenter: DataCenter) = write(1, dataCenter.toString())

    override fun loadDc() = read(1) { it.split(":").let { DataCenter(it[0], it[1].toInt()) } }

    override fun deleteDc() = delete(1)

    override fun saveSession(session: MTSession?) {
        if (session == null) return deleteSession()

        val content = with(session) {
            val id = id.joinToString(",")
            val tag = tag.split(":").first()
            listOf(dataCenter, id, salt, contentRelatedCount, lastMessageId, tag)
        }

        write(2, content.joinToString(separator))
    }

    override fun loadSession(): MTSession? {
        return read(2) {
            val params = it.split(separator)
            val dc = params[0].split(":")

            MTSession(
                    dataCenter = DataCenter(dc[0], dc[1].toInt()),
                    id = params[1].split(",").map(String::toByte).toByteArray(),
                    salt = params[2].toLong(),
                    contentRelatedCount = params[3].toInt(),
                    lastMessageId = params[4].toLong(),
                    tag = params[5]
            )
        }
    }

    fun deleteSession() = delete(2)

    private fun write(pos: Int, content: String) {
        val lines = Files.readAllLines(auth)
        lines[pos] = content
        Files.write(auth, lines, WRITE, TRUNCATE_EXISTING)
    }

    private fun delete(pos: Int) = write(pos, "")

    private fun <T> read(pos: Int, mapper: (String) -> T) = Files.lines(auth)
            .skip(pos.toLong())
            .findFirst()
            .orElseGet { null }
            ?.let { if (it.isBlank()) null else it }
            ?.let(mapper)

    private final fun String.prepare(): Path {
        val path = props.storagePath.resolve(this)

        Files.createDirectories(path.parent)
        if (!Files.exists(path)) {
            Files.write(path, System.lineSeparator().repeat(3).toByteArray(), CREATE, WRITE)
        }

        return path
    }
}
