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
    private val authKeyFile = "auth.key".toPath()
    private val nearestDcFile = "dc.save".toPath()
    private val sessionFile = "session".toPath()

    override fun saveAuthKey(authKey: AuthKey) = authKeyFile.write(authKey.key)

    override fun loadAuthKey() = authKeyFile.load { AuthKey(it) }

    override fun deleteAuthKey() = authKeyFile.delete()

    override fun saveDc(dataCenter: DataCenter) = nearestDcFile.write(dataCenter.toString().toByteArray())

    override fun loadDc(): DataCenter? {
        return nearestDcFile.load { bytes ->
            bytes.let { String(it) }
                .split(":")
                .let { DataCenter(it[0], it[1].toInt()) }
        }
    }

    override fun deleteDc() = nearestDcFile.delete()

    override fun saveSession(session: MTSession?) {
        if (session == null) return deleteSession()

        val content = with(session) {
            val id = id.toList().joinToString(",")
            val tag = tag.split(":").first()
            listOf(dataCenter, id, salt, contentRelatedCount, lastMessageId, tag)
        }.joinToString(System.lineSeparator()).toByteArray()

        sessionFile.write(content)
    }

    override fun loadSession(): MTSession? {
        return sessionFile.load {
            val params = String(it).split(System.lineSeparator())
            val dc = params[0].split(":")

            MTSession(
                    dataCenter = DataCenter(dc[0], dc[1].toInt()),
                    id = params[1].split(",").map { it.toByte() }.toByteArray(),
                    salt = params[2].toLong(),
                    contentRelatedCount = params[3].toInt(),
                    lastMessageId = params[4].toLong(),
                    tag = params[5]
            )
        }
    }

    fun deleteSession() = sessionFile.delete()

    private final fun String.toPath() = props.storagePath.resolve(this)

    private fun Path.delete() {
        Files.deleteIfExists(this)
    }

    private fun Path.write(content: ByteArray) {
        Files.createDirectories(parent)
        Files.write(this, content, CREATE, WRITE, TRUNCATE_EXISTING)
    }

    private fun <T> Path.load(mapper: (ByteArray) -> T) =
            if (!Files.exists(this)) null
            else Files.readAllBytes(this).let(mapper)
}
