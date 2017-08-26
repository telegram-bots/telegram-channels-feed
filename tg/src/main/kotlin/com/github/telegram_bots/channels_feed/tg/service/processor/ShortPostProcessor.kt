package com.github.telegram_bots.channels_feed.tg.service.processor

import com.github.badoualy.telegram.api.utils.getMessageOrEmpty
import com.github.badoualy.telegram.tl.api.*
import com.github.telegram_bots.channels_feed.tg.domain.*
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost.Mode.AS_IS
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPost.Mode.HTML
import com.github.telegram_bots.channels_feed.tg.domain.ProcessedPostGroup.Type.SHORT
import com.github.telegram_bots.channels_feed.tg.util.UTF_16LE
import org.springframework.stereotype.Component
import java.io.ByteArrayOutputStream

@Component
class ShortPostProcessor : PostProcessor {
    companion object {
        const val MAX_LENGTH: Int = 200
        const val SEPARATOR: String = "\n\n"
    }

    override val type = SHORT

    override fun process(data: RawPostData) = when (data.raw.media) {
        null, is TLInputMediaEmpty -> textPost(data)
        else -> ProcessedPost(mode = AS_IS)
    }

    private fun textPost(data: RawPostData): ProcessedPost {
        val firstLink = extractFirstLink(data)
        val header = makeHeader(data)
        val text = processText(firstLink, header, data)

        return ProcessedPost(text = text, previewEnabled = firstLink != null, mode = HTML)
    }

    private fun processText(link: Link, header: Header, data: RawPostData): String {
        val processed = data.raw
                .getMessageOrEmpty()
                .replaceHTMLTags()
                .convertEntities(data.raw.entities)

        return ((link ?: "") + header + processed).shorten(MAX_LENGTH)
    }

    private fun makeHeader(data: RawPostData) =
            """<a href="https://t.me/${data.channel.url}/${data.raw.id}">${data.channel.name}</a>:$SEPARATOR"""

    private fun extractFirstLink(data: RawPostData): Link {
        return data.raw.entities
                ?.find { it is TLMessageEntityTextUrl || it is TLMessageEntityUrl }
                ?.let {
                    when (it) {
                        is TLMessageEntityTextUrl -> it.url
                        is TLMessageEntityUrl -> it.extract(data.raw.getMessageOrEmpty().toByteArray(UTF_16LE))
                        else -> null
                    }
                }
                ?.let { "<a href=\"$it\">\u00AD</a>" }
    }

    private fun String.convertEntities(entities: List<TLAbsMessageEntity>?): String {
        if (entities == null) return this
        val source = toByteArray(UTF_16LE)
        return entities.asSequence()
                .map { Triple(it.format(source), it.startPos(), it.endPos()) }
                .fold(Triple(0, source, ByteArrayOutputStream()), {
                    (curPos, source, target), (replacement, startPos, endPos) ->
                            target.write(source.sliceArray(curPos until startPos))
                            target.write(replacement)
                            Triple(endPos, source, target)
                })
                .let { (endPos, source, target) ->
                    if (endPos < source.size) {
                        target.write(source.sliceArray(endPos until source.size))
                    }

                    target
                }
                .toByteArray()
                .let { String(it, UTF_16LE) }
    }

    private fun String.replaceHTMLTags() = replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("&", "&amp;")

    private fun String.shorten(limit: Int, placeholder: String = "...") =
            if (length <= limit) this
            else substring(0, limit - placeholder.length) + placeholder

    private fun TLAbsMessageEntity.format(byteArray: ByteArray): ByteArray {
        val value = extract(byteArray)
        val result = when (this) {
            is TLMessageEntityTextUrl -> """<a href="$url">$value</a>"""
            is TLMessageEntityBold -> """<b>$value</b>"""
            is TLMessageEntityItalic -> """<i>$value</i>"""
            is TLMessageEntityCode -> """<code>$value</code>"""
            is TLMessageEntityPre -> """"<pre>$value</pre>"""
            else -> value
        }

        return result.toByteArray(UTF_16LE)
    }

    private fun TLAbsMessageEntity.startPos() = offset * 2

    private fun TLAbsMessageEntity.endPos() = (offset + length) * 2

    private fun TLAbsMessageEntity.extract(byteArray: ByteArray) = byteArray.sliceArray(startPos() until endPos())
            .let { String(it, UTF_16LE) }
}
