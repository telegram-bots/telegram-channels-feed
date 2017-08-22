package com.github.telegram_bots.channels_feed.util

import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.databind.DeserializationContext
import com.fasterxml.jackson.databind.JsonDeserializer
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.TextNode
import com.github.telegram_bots.channels_feed.domain.FileID
import com.github.telegram_bots.channels_feed.domain.RawPost
import com.github.telegram_bots.channels_feed.domain.RawPost.*
import com.github.telegram_bots.channels_feed.domain.RawPost.Content.Type.PHOTO
import com.github.telegram_bots.channels_feed.domain.RawPost.Content.Type.TEXT
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity
import java.time.Instant

object RawPostDeserializer : JsonDeserializer<RawPost>() {
    private val entityTypeLookup = Entity.Type.values().map { it.value to it }.toMap()
    private val contentTypeLookup = Content.Type.values().map { it.value to it }.toMap()

    override fun deserialize(p: JsonParser, ctxt: DeserializationContext): RawPost {
        val node = p.readValueAsTree<JsonNode>()

        return RawPost(
                channelId = node.get("chat_id_").asLong(),
                messageId = node.get("id_").asLong(),
                date = node.get("date_").asLong().let { Instant.ofEpochSecond(it) },
                content = deserializeContent(node.get("content_"))
        )
    }

    private fun deserializeContent(node: JsonNode): Content {
        val type = contentTypeLookup.getOrElse(node.get("ID").textValue() ?: "", { Content.Type.UNKNOWN })
        return when (type) {
            TEXT -> {
                val text = node.get("text_").textValue()
                TextContent(
                        type = type,
                        text = text,
                        entities = deserializeEntities(text, node.get("entities_"))
                )
            }
            PHOTO -> PhotoContent(
                    type = type,
                    text = node.path("caption_").textValue(),
                    photoId = deserializePhotoID(node.get("photo_"))
            )
            else -> OtherContent(type, node.path("caption_").textValue())
        }
    }

    private fun deserializePhotoID(node: JsonNode): FileID {
        val sizes = node.path("sizes_")
        val maxSize = sizes?.fieldNames()?.asSequence()?.sorted()?.last()

        return sizes.path(maxSize)
                .path("photo_")
                .path("persistent_id_")
                .let { it as? TextNode }
                .let { it?.textValue() }
                ?: throw IllegalStateException("Image ID doesn't exists!")
    }

    private fun deserializeEntities(text: String, node: JsonNode): List<Entity> {
        val byteArray = text.toByteArray(UTF_16LE)
        return node.fieldNames()
                .asSequence()
                .map { deserializeEntity(byteArray, node.get(it)) }
                .sortedBy { it.startPos }
                .toList()
    }

    private fun deserializeEntity(byteArray: ByteArray, node: JsonNode): Entity {
        val type = entityTypeLookup.getOrElse(node.get("ID").textValue() ?: "", { Entity.Type.UNKNOWN })
        val (startPos, endPos) = (node.get("offset_").intValue() to node.get("length_").intValue())
                .let { it.first * 2 to (it.first + it.second) * 2 }
        val value = byteArray.sliceArray(startPos until endPos).let { String(it, UTF_16LE) }
        val url = node.path("url_").asText(null)

        return Entity(type, value, startPos, endPos, url)
    }
}
