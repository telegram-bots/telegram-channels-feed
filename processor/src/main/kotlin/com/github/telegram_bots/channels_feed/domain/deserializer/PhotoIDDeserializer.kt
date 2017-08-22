package com.github.telegram_bots.channels_feed.domain.deserializer

import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.core.TreeNode
import com.fasterxml.jackson.databind.DeserializationContext
import com.fasterxml.jackson.databind.JsonDeserializer
import com.fasterxml.jackson.databind.node.TextNode
import com.github.telegram_bots.channels_feed.domain.FileID

class PhotoIDDeserializer : JsonDeserializer<FileID>() {
    override fun deserialize(p: JsonParser, ctxt: DeserializationContext): FileID {
        val node: TreeNode = p.readValueAsTree()
        val sizes = node.path("sizes_")
        val maxSize = sizes?.fieldNames()?.asSequence()?.sorted()?.last()

        return sizes.path(maxSize)
                .path("photo_")
                .path("persistent_id_")
                .let { it as? TextNode }
                .let { it?.textValue() }
                ?: throw IllegalStateException("Image ID doesn't exists!")
    }
}
