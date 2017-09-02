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
class TelegramConfigStorage(private val props: TGProperties) : TelegramApiStorage {
    companion object {
        const val AUTH_KEY_FILE = "auth.key"
        const val NEAREST_DC_FILE = "dc.save"
        const val SESSION_FILE = "session"
    }

    override fun saveAuthKey(authKey: AuthKey) {
        overwrite(props.storagePath.resolve(AUTH_KEY_FILE), authKey.key)
    }

    override fun loadAuthKey() = load(props.storagePath.resolve(AUTH_KEY_FILE)) { AuthKey(it) }

    override fun deleteAuthKey() {
        Files.deleteIfExists(props.storagePath.resolve(AUTH_KEY_FILE))
    }

    override fun saveDc(dataCenter: DataCenter) {
        overwrite(props.storagePath.resolve(NEAREST_DC_FILE), dataCenter.toString().toByteArray())
    }

    override fun loadDc(): DataCenter? {
        return load(props.storagePath.resolve(NEAREST_DC_FILE)) { bytes ->
            bytes.let { String(it) }
                .split(":")
                .let { DataCenter(it[0], it[1].toInt()) }
        }
    }

    override fun deleteDc() {
        Files.deleteIfExists(props.storagePath.resolve(NEAREST_DC_FILE))
    }

    override fun saveSession(session: MTSession?) {
        if (session == null) return deleteSession()

        val content = with(session) {
            val id = id.toList().joinToString(",")
            val tag = tag.split(":").first()
            listOf(dataCenter, id, salt, contentRelatedCount, lastMessageId, tag)
        }.joinToString(System.lineSeparator()).toByteArray()

        overwrite(props.storagePath.resolve(SESSION_FILE), content)
    }

    override fun loadSession(): MTSession? {
        return load(props.storagePath.resolve(SESSION_FILE)) {
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

    private fun deleteSession() {
        Files.deleteIfExists(props.storagePath.resolve(SESSION_FILE))
    }

    private fun overwrite(file: Path, content: ByteArray) {
        Files.createDirectories(file.parent)
        Files.write(file, content, CREATE, WRITE, TRUNCATE_EXISTING)
    }

    private fun <T> load(file: Path, mapper: (ByteArray) -> T): T? {
        return if (!Files.exists(file)) null else Files.readAllBytes(file).let(mapper)
    }
}
