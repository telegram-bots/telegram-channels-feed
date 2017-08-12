package com.github.telegram_bots.channels_feed.domain.deserializer

import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.core.TreeNode
import com.fasterxml.jackson.databind.DeserializationContext
import com.fasterxml.jackson.databind.JsonDeserializer
import com.github.telegram_bots.channels_feed.domain.FileID

class PhotoIDDeserializer : JsonDeserializer<FileID>() {
    override fun deserialize(p: JsonParser, ctxt: DeserializationContext): FileID {
        val node: TreeNode = p.readValueAsTree()
        val sizes = node.get("sizes_")
        val maxSize = sizes?.fieldNames()?.asSequence()?.sorted()?.last()

        return sizes?.get(maxSize)
                ?.get("photo_")
                ?.get("persistent_id_")
                ?.toString()
                ?: throw IllegalStateException("Image ID doesn't exists!")
    }
}
