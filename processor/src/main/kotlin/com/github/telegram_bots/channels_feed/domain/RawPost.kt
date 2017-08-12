package com.github.telegram_bots.channels_feed.domain

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.databind.annotation.JsonDeserialize
import com.github.telegram_bots.channels_feed.domain.deserializer.EntityListDeserializer
import com.github.telegram_bots.channels_feed.domain.deserializer.PhotoIDDeserializer
import com.github.telegram_bots.channels_feed.domain.deserializer.TypeDeserializer
import com.github.telegram_bots.channels_feed.extension.UTF_16LE
import java.time.Instant

@JsonIgnoreProperties(ignoreUnknown = true)
data class RawPost(
        @JsonProperty("chat_id_")
        val channelId: Long,

        @JsonProperty("id_")
        val messageId: Long,

        @JsonProperty("date_")
        val date: Instant,

        @JsonProperty("content_")
        val content: Content,

        val update: Boolean = false
) {
    @JsonTypeInfo(
            use=JsonTypeInfo.Id.NAME,
            property="ID",
            include = JsonTypeInfo.As.EXISTING_PROPERTY,
            defaultImpl = OtherContent::class,
            visible = true
    )
    @JsonSubTypes(
            JsonSubTypes.Type(value = TextContent::class, name = "MessageText"),
            JsonSubTypes.Type(value = PhotoContent::class, name = "MessagePhoto")
    )
    interface Content {
        val type: String
        val text: String
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    data class TextContent(
            @JsonProperty("ID")
            override val type: String,

            @JsonProperty("text_")
            override val text: String,

            @JsonProperty("entities_")
            @JsonDeserialize(using = EntityListDeserializer::class)
            val entities: List<Entity>
    ) : Content {
        val utf16TextBytes: ByteArray by lazy { text.toByteArray(UTF_16LE) }

        @JsonIgnoreProperties(ignoreUnknown = true)
        data class Entity(
                @JsonProperty("ID")
                @JsonDeserialize(using = TypeDeserializer::class)
                val type: Type,

                @JsonProperty("offset_")
                val offset: Int,

                @JsonProperty("length_")
                val length: Int,

                @JsonProperty("url_")
                val url: String?
        ) {
            enum class Type(val value: String) {
                PLAIN_LINK("MessageEntityUrl"),
                FORMATTED_LINK("MessageEntityTextUrl"),
                BOLD("MessageEntityBold"),
                ITALIC("MessageEntityItalic"),
                CODE("MessageEntityCode"),
                PRE("MessageEntityPre"),
                UNKNOWN("Unknown");
            }
        }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    data class PhotoContent(
            @JsonProperty("ID")
            override val type: String,

            @JsonProperty("caption_")
            override val text: String = "",

            @JsonProperty("photo_")
            @JsonDeserialize(using = PhotoIDDeserializer::class)
            val photoId: FileID
    ) : Content

    @JsonIgnoreProperties(ignoreUnknown = true)
    data class OtherContent(
            @JsonProperty("ID")
            override val type: String,

            @JsonProperty("caption_")
            override val text: String = ""
    ) : Content
}
