package com.nuvio.tv.core.usenet

import com.nuvio.tv.core.debrid.DebridStreamFormatter
import com.nuvio.tv.core.debrid.DebridStreamFormatterDefaults
import com.nuvio.tv.core.debrid.DebridStreamTemplateEngine
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class StreamFormatterPreviewTest {
    private val formatter = DebridStreamFormatter(DebridStreamTemplateEngine())

    @Test fun `the detailed preset shows each example's fields line by line`() {
        val samples = StreamFormatterPreview.render(formatter, DebridStreamFormatterDefaults.DETAILED_NAME_TEMPLATE,
            DebridStreamFormatterDefaults.DETAILED_DESCRIPTION_TEMPLATE).associateBy { it.kind }
        assertEquals(setOf(StreamFormatterPreview.USENET_MOVIE, StreamFormatterPreview.USENET_EPISODE,
            StreamFormatterPreview.DEBRID_MOVIE), samples.keys)
        val movie = samples.getValue(StreamFormatterPreview.USENET_MOVIE)
        assertTrue(movie.name, movie.name.startsWith("▶ 4K") && "DV" in movie.name && movie.name.endsWith("T1"))
        val lines = movie.description.lines()
        assertTrue(movie.description, lines.any { it.startsWith("🔊 TrueHD Atmos 7.1") })
        assertTrue(movie.description, lines.any { it.startsWith("📦 ") && "72 Mbps" in it && "⏳ 3d" in it })
        assertTrue(movie.description, lines.any { it.startsWith("⚡ Usenet") && "🔎 Indexer" in it && "🏷️ FraMeSToR" in it })
        val episode = samples.getValue(StreamFormatterPreview.USENET_EPISODE)
        assertTrue(episode.description, episode.description.lines().any { "S01E01" in it })
        assertTrue(episode.description, episode.description.lines().any { "📺 Amazon" in it })
        val debrid = samples.getValue(StreamFormatterPreview.DEBRID_MOVIE)
        assertTrue(debrid.description, debrid.description.lines().any { it.startsWith("⚡ RD") })
    }

    @Test fun `the default templates show every example`() {
        StreamFormatterPreview.render(formatter, DebridStreamFormatterDefaults.NAME_TEMPLATE,
            DebridStreamFormatterDefaults.DESCRIPTION_TEMPLATE).forEach {
            assertTrue(it.kind, it.name.isNotBlank() && it.description.isNotBlank())
        }
    }

    @Test fun `a template still being typed does not fail the preview`() {
        val samples = StreamFormatterPreview.render(formatter, "{stream.resolution::=2160p[\"4K\"||", "{stream.title::")
        assertEquals(3, samples.size)
    }
}
