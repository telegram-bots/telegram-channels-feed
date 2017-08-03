package com.github.telegram_bots.channels_feed.domain.deserializer

import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.core.JsonToken
import com.fasterxml.jackson.core.TreeNode
import com.fasterxml.jackson.databind.DeserializationContext
import com.fasterxml.jackson.databind.JsonDeserializer
import com.fasterxml.jackson.databind.ObjectMapper
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity

class EntityListDeserializer : JsonDeserializer<List<Entity>>() {
    override fun deserialize(p: JsonParser, ctxt: DeserializationContext): List<Entity> {
        if (p.currentToken != JsonToken.START_OBJECT) {
            return emptyList()
        }

        val node: TreeNode = p.readValueAsTree()
        val mapper = ObjectMapper()

        return node.fieldNames()
                .asSequence()
                .map { mapper.readValue(node.get(it).toString(), Entity::class.java) }
                .toList()
    }
}
