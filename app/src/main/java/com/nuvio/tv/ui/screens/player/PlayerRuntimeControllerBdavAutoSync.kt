package com.nuvio.tv.ui.screens.player

import androidx.media3.extractor.ExtractorsFactory
import com.nuvio.tv.ui.screens.player.audiosync.AudioSyncSettings
import com.nuvio.tv.ui.screens.player.audiosync.AudioSyncTaps
import com.nuvio.tv.ui.screens.player.autosync.AutoSyncExtractorsFactory
import com.nuvio.tv.ui.screens.player.autosync.AutoSyncPreferences

/**
 * Blu-ray clips (BDAV) are read by their own extractors, not by the factory that
 * [autoSyncExtractorsFactory] wraps. Wrap them the same way, so AutoSync sees the disc's subtitle
 * timing and the audio fallback hears its audio.
 */
internal fun PlayerRuntimeController.configureBdavAutoSync() {
    mediaSourceFactory.configureBdavExtractorsWrapper { delegate, url ->
        AutoSyncPreferences.ensureLoaded(context)
        if (!AutoSyncPreferences.isEnabled(context)) {
            delegate
        } else {
            val audioDelegate = if (AudioSyncSettings.fallbackEnabled.value) {
                AudioSyncTaps.wrapExtractors(delegate, url)
            } else {
                delegate
            }
            AutoSyncExtractorsFactory(delegate = audioDelegate, sourceKey = url)
        }
    }
}
