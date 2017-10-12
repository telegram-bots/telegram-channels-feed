package com.github.telegram_bots.channels_feed.tg.service

import com.github.badoualy.telegram.api.utils.getMessageOrEmpty
import com.github.badoualy.telegram.tl.api.*
import com.github.telegram_bots.channels_feed.tg.domain.RawPostData
import java.io.ByteArrayOutputStream
import java.nio.charset.Charset

object MessageFormatter {
    private const val SEPARATOR: String = "\n\n"
    private val UTF_16LE = Charset.forName("UTF-16LE")!!

    fun processText(link: String?, header: String, data: RawPostData, maxLength: Int): String {
        val processed = data.message
                .getMessageOrEmpty()
                .replaceHTMLTags()
                .convertEntities(data.message.entities)
                .shorten(maxLength)

        return ((link ?: "") + header + processed)
    }

    fun makeHeader(data: RawPostData) =
            """<a href="https://t.me/${data.channel.url}/${data.message.id}">${data.channel.name}</a>:$SEPARATOR"""

    fun extractFirstLink(data: RawPostData): String? {
        return data.message.entities
                ?.find { it is TLMessageEntityTextUrl || it is TLMessageEntityUrl }
                ?.let {
                    when (it) {
                        is TLMessageEntityTextUrl -> it.url
                        is TLMessageEntityUrl -> it.extract(data.message.getMessageOrEmpty().toByteArray(UTF_16LE))
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

    private fun String.shorten(limit: Int, placeholder: String = "...") =
            if (length <= limit) this
            else substring(0, limit - placeholder.length) + placeholder

    private fun String.replaceHTMLTags() = replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("&", "&amp;")

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
