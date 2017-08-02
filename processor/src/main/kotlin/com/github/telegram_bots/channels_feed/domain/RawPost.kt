package com.github.telegram_bots.channels_feed.domain

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
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
        @JsonIgnoreProperties(ignoreUnknown = true)
        data class Content(
                @JsonProperty("text_")
                private val _text: String?,

                @JsonProperty("caption_")
                private val _caption: String?,

                @JsonProperty("entities_")
                val entities: List<Any>
        ) {
                val text: String
                        get() = _text ?: _caption!!
        }
}
