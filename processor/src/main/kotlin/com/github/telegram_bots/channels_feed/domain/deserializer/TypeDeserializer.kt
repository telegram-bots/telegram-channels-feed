package com.github.telegram_bots.channels_feed.domain.deserializer

import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.databind.DeserializationContext
import com.fasterxml.jackson.databind.JsonDeserializer
import com.github.telegram_bots.channels_feed.domain.RawPost.TextContent.Entity.Type

class TypeDeserializer : JsonDeserializer<Type>() {
    companion object {
        private val lookup = Type.values().map { it.value to it }.toMap()
    }

    override fun deserialize(p: JsonParser?, ctxt: DeserializationContext?): Type {
        return lookup.getOrElse(p?.valueAsString ?: "", { Type.UNKNOWN })
    }
}
