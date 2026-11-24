package com.nuvio.tv.core.usenet

import com.nuvio.tv.core.debrid.DebridStreamFormatter
import com.nuvio.tv.domain.model.DebridSettings

/**
 * Example results the formatting web editor shows its templates with, as they are typed: a built-in
 * Usenet film and episode and a cached debrid film. Their fields come from made-up release names,
 * read the way a built-in result's are; a debrid result has the same fields.
 */
object StreamFormatterPreview {
    /** [kind] names the example: [USENET_MOVIE], [USENET_EPISODE] or [DEBRID_MOVIE]. */
    data class Sample(val kind: String, val name: String, val description: String)

    const val USENET_MOVIE = "usenetMovie"
    const val USENET_EPISODE = "usenetEpisode"
    const val DEBRID_MOVIE = "debridMovie"

    /** Longer templates are cut: the editor sends what is typed, and this runs on the TV. */
    const val MAX_TEMPLATE_LENGTH = 8_000

    fun render(formatter: DebridStreamFormatter, nameTemplate: String, descriptionTemplate: String,
        now: Long = System.currentTimeMillis()): List<Sample> {
        val templates = DebridSettings(streamNameTemplate = nameTemplate.take(MAX_TEMPLATE_LENGTH),
            streamDescriptionTemplate = descriptionTemplate.take(MAX_TEMPLATE_LENGTH))
        return EXAMPLES.map { example ->
            val release = example.release.copy(publishedAt = example.ageDays?.let { now - it * DAY_MS } ?: 0)
            val values = UsenetResultValues.of(release, episodeSize = null, failed = false,
                languageEmoji = formatter::languageEmoji, now = now, bitrate = example.bitrate, tier = example.tier) +
                example.overrides
            // A template the engine cannot read shows nothing rather than failing the editor.
            val (name, description) = runCatching { formatter.render(templates, values) }.getOrDefault("" to "")
            Sample(example.kind, name, description)
        }
    }

    private class Example(val kind: String, val release: UsenetRelease, val ageDays: Long?, val bitrate: String?,
        val tier: String?, val overrides: Map<String, Any?> = emptyMap())

    private const val DAY_MS = 86_400_000L
    private const val GIB = 1L shl 30

    private val EXAMPLES = listOf(
        Example(USENET_MOVIE, UsenetRelease("Movie.Title.2024.2160p.UHD.BluRay.REMUX.DV.HDR10Plus.HEVC.TrueHD.Atmos.7.1-FraMeSToR",
            "preview:movie", size = 60 * GIB, indexerName = "Indexer"), ageDays = 3, bitrate = "72 Mbps", tier = "T1"),
        Example(USENET_EPISODE, UsenetRelease("Show.Name.S01E01.2160p.AMZN.WEB-DL.DDP5.1.Atmos.DV.HDR10.H.265-NTb",
            "preview:episode", size = 13 * GIB / 2, indexerName = "Indexer"), ageDays = 12, bitrate = "13 Mbps", tier = null),
        Example(DEBRID_MOVIE, UsenetRelease("Movie.Title.2024.1080p.BluRay.DTS-HD.MA.5.1.x264-GROUP", "preview:debrid",
            size = 14 * GIB), ageDays = null, bitrate = null, tier = null,
            overrides = mapOf("service.shortName" to "RD", "service.name" to "Real-Debrid", "service.cached" to true,
                "stream.type" to "debrid", "addon.name" to "Debrid"))
    )
}
