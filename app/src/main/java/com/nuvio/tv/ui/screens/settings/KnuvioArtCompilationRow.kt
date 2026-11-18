package com.nuvio.tv.ui.screens.settings

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import com.nuvio.tv.R
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

/**
 * knuvio K-12: shows how ART compiled the installed APK, read from its odex header. It tells whether an update installed
 * without dex metadata, through Android's installer screen, was still compiled with the profile embedded in the APK.
 * Selecting the row reads the status again.
 */
@Composable
internal fun KnuvioArtCompilationRow() {
    val context = LocalContext.current.applicationContext
    var refreshCount by remember { mutableIntStateOf(0) }
    var status by remember { mutableStateOf<ArtCompilationStatus?>(null) }
    var loaded by remember { mutableStateOf(false) }
    LaunchedEffect(refreshCount) {
        status = withContext(Dispatchers.IO) { ArtCompilationStatusReader.read(context) }
        loaded = true
    }

    val current = status
    val summary = when {
        !loaded -> ""
        current == null -> stringResource(R.string.knuvio_art_compilation_no_odex)
        current.compilerFilter == "speed-profile" && current.compilationReason == "install" ->
            stringResource(R.string.knuvio_art_compilation_embedded_profile)
        current.compilerFilter == "speed-profile" && current.compilationReason == "install-dm" ->
            stringResource(R.string.knuvio_art_compilation_dex_metadata)
        current.compilerFilter == "speed-profile" -> stringResource(R.string.knuvio_art_compilation_later_profile)
        current.compilerFilter == "verify" -> stringResource(R.string.knuvio_art_compilation_no_profile)
        else -> stringResource(R.string.knuvio_art_compilation_other)
    }
    val details = current?.let {
        stringResource(
            R.string.knuvio_art_compilation_details,
            it.compilationReason ?: "?",
            it.artVersion ?: "?",
            it.instructionSet ?: "?"
        )
    }

    SettingsActionRow(
        title = stringResource(R.string.knuvio_art_compilation_title),
        subtitle = listOfNotNull(summary.takeIf { it.isNotEmpty() }, details).joinToString("\n"),
        value = current?.compilerFilter,
        onClick = { refreshCount++ }
    )
}

internal data class ArtCompilationStatus(
    val compilerFilter: String?,
    val compilationReason: String?,
    val artVersion: String?,
    val instructionSet: String?
)

internal object ArtCompilationStatusReader {
    // The OAT header and its key-value store sit a few KB into the odex; the file itself can be tens of MB.
    private const val HEADER_BYTES = 64 * 1024
    private val artVersionRegex = Regex("art-version:(\\d+)")

    fun read(context: Context): ArtCompilationStatus? {
        val codeDir = File(context.applicationInfo.sourceDir).parentFile ?: return null
        val odex = File(codeDir, "oat").listFiles()
            ?.firstNotNullOfOrNull { isaDir -> File(isaDir, "base.odex").takeIf { it.isFile } }
            ?: return null
        val header = runCatching { readHeader(odex) }.getOrNull() ?: return null
        return ArtCompilationStatus(
            compilerFilter = header.valueOf("compiler-filter"),
            compilationReason = header.valueOf("compilation-reason"),
            artVersion = artVersionRegex.find(header)?.groupValues?.get(1),
            instructionSet = odex.parentFile?.name
        )
    }

    private fun readHeader(file: File): String = file.inputStream().use { input ->
        val buffer = ByteArray(HEADER_BYTES)
        var read = 0
        while (read < buffer.size) {
            val count = input.read(buffer, read, buffer.size - read)
            if (count <= 0) break
            read += count
        }
        String(buffer, 0, read, Charsets.ISO_8859_1)
    }

    // Keys and values are NUL-terminated strings in the OAT header's key-value store.
    private fun String.valueOf(key: String): String? {
        val keyStart = indexOf("$key\u0000").takeIf { it >= 0 } ?: return null
        val valueStart = keyStart + key.length + 1
        val valueEnd = indexOf('\u0000', valueStart).takeIf { it > valueStart } ?: return null
        return substring(valueStart, valueEnd)
    }
}
