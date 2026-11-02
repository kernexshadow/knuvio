# knuvio changes

Everything knuvio adds on top of [NuvioMedia/NuvioTV](https://github.com/NuvioMedia/NuvioTV). Each entry says why the change
exists, which files it touches, and how to remove it. Read this first when an upstream merge conflicts.

Files under `app/src/full/res`, `app/src/fullDebug/res`, `knuvio-branding/` and the knuvio workflow are knuvio-only and cannot
conflict. **Upstream files that knuvio edits** are the ones to watch:

| Upstream file | Changed by |
|---|---|
| `app/build.gradle.kts` | [K-02](#k-02-application-ids-and-updater-source), [K-06](#k-06-audio-based-subtitle-sync-upstream-pr-4150), [K-07](#k-07-built-in-usenet-streaming-upstream-pr-3511) |
| `app/src/main/java/com/nuvio/tv/updater/VersionUtils.kt` | [K-05](#k-05-knuvio-revisions-in-the-updater) |
| `app/proguard-rules.pro`, player and settings files listed in K-06 | [K-06](#k-06-audio-based-subtitle-sync-upstream-pr-4150) |
| `gradle/libs.versions.toml`, addon manager, stream, player and settings files listed in K-07 | [K-07](#k-07-built-in-usenet-streaming-upstream-pr-3511) |
| Player files and Portuguese strings listed in K-08 | [K-08](#k-08-blu-ray-clips-and-discs-in-exoplayer-upstream-pr-696) |
| `DirectDebridStreamPreparer.kt`, `PlayerRuntimeControllerStreams.kt`, `StreamScreenViewModel.kt` | [K-10](#k-10-debrid-link-preparation-off-the-main-thread-upstream-pr-4400) |
| `StreamComponents.kt`, `StreamSourcesSidePanel.kt`, `EpisodesSidePanel.kt`, `StreamScreen.kt` | [K-11](#k-11-addon-tab-focus-on-the-selected-chip-upstream-pr-4424) |

Upstream status: **knuvio only** = not meant for upstream; **upstream PR #N** = proposed; **in upstream since X** = the change
can be dropped from knuvio after merging X.

---

## K-01 Branding: icons, banner, app name, wordmarks

- **Why:** knuvio must be recognisable next to the official app on the same TV.
- **What:**
  - K launcher icon (all densities), splash mark (`app_logo_mark`), TV banner.
  - App name "knuvio" in every locale; debug builds show "knuvio Debug".
  - In-app wordmark (`app_logo_wordmark` plus the five themed variants) with the K mark.
  - The five alternative launcher icons and banners (arctic blue, emerald, rose gold, copper, graphite), recoloured K.
- **Files:** `app/src/full/res/**` (`mipmap-*`, `drawable/`, `drawable-nodpi/`, `values*/strings_knuvio.xml`),
  `app/src/fullDebug/res/values/strings_knuvio.xml`, `knuvio-branding/**` (source artwork and generator scripts).
- **Commits:** `a8d06b712`, `dce6f721c`, `f7e032b73`, `17e90709f`, `45174c883`.
- **Remove:** delete the files; the upstream resources in `app/src/main/res` take over.
- **Upstream status:** knuvio only.
- **Watch:** a new upstream locale with `app_name` needs its own `strings_knuvio.xml`; a new theme or icon option needs a
  regenerated variant (see `knuvio-branding/`). An overlay only replaces an upstream resource with the same qualifiers: if
  upstream moves an image to another folder (as 1.1.0-beta.9 moved the logos to `drawable-nodpi`), move the overlay and the
  script paths with it, or upstream's image wins on some screen densities.

## K-02 Application IDs and updater source

- **Why:** knuvio installs next to the official app, is signed with its own key, and must update from knuvio releases.
- **What:** `com.knuvio.tv` (full), `com.knuvio.app` (playstore), debug `com.knuviodebug.com` / `com.knuvio.appdebug`;
  `GITHUB_OWNER`/`GITHUB_REPO` = `kernexshadow`/`knuvio`.
- **Files:** `app/build.gradle.kts` (5 lines: two `applicationId`, the debug `variant.applicationId`, `GITHUB_OWNER`, `GITHUB_REPO`).
- **Commits:** `b3a8f4708`.
- **Remove:** revert the commit. Installed knuvio apps would then be replaced by, or conflict with, the official app.
- **Upstream status:** knuvio only. A configurable owner/repo (Gradle property with NuvioMedia as default) could be proposed
  upstream to shrink this diff.

## K-03 Upstream sync and release workflow

- **Why:** follow upstream releases without manual work, and publish signed APKs.
- **What:** `.github/workflows/knuvio-sync-release.yml`: scheduled merge of upstream release tags, manual `+k.N` revision builds,
  versionName stamping, disabling inherited workflows, signed release build and GitHub release. Details in `.claude/CLAUDE.md`.
- **Files:** `.github/workflows/knuvio-sync-release.yml`.
- **Commits:** `08f38f567`, `2ce5024ec`, `d89acd56a`, `720c09f89`.
- **Remove:** delete the workflow; releases then have to be built by hand.
- **Upstream status:** knuvio only.

## K-04 Project notes

- **Why:** keep how knuvio works, and why each change exists, next to the code.
- **Files:** `.claude/CLAUDE.md` (force-added: upstream's `.gitignore` ignores `CLAUDE.md`), `KNUVIO_CHANGES.md`.
- **Upstream status:** knuvio only.

## K-05 knuvio revisions in the updater

- **Why:** manual knuvio builds of the same upstream version (`+k.1`, `+k.2`, …) must be offered as updates, for betas and
  stable versions alike, while any newer upstream version still wins.
- **What:** `SemanticVersion` gets `knuvioRevision`, parsed from `+k` / `+k.N` build metadata and compared only when everything
  else is equal. Other build metadata stays ignored, so upstream's tests still pass.
- **Files:** `app/src/main/java/com/nuvio/tv/updater/VersionUtils.kt` (upstream file),
  `app/src/test/java/com/nuvio/tv/updater/KnuvioRevisionTest.kt` (knuvio-only tests).
- **Commits:** `42314d583`.
- **Remove:** revert the commit and stop publishing `+k.N` builds (the workflow's manual mode depends on it).
- **Upstream status:** knuvio only.
- **Watch:** upstream edits to `VersionUtils.kt` will conflict. Keep the `knuvioRevision` comparison as the last tie-breaker
  and run `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.updater.*'`.

## K-06 Audio-based subtitle sync (upstream PR #4150)

- **Why:** try upstream's proposed audio sync fallback before it is merged: when a subtitle cannot be synced from embedded
  subtitles, it is aligned against the speech in the audio track.
- **What:** the four commits of [NuvioMedia/NuvioTV#4150](https://github.com/NuvioMedia/NuvioTV/pull/4150) by DavidVamaiotu
  (head `9d72c7046`), cherry-picked unchanged. The build downloads the sherpa-onnx AAR from GitHub (pinned version and
  SHA-256). On first use the app downloads the speech model, about 74 MB, from the PR author's GitHub release (ORT
  conversion), or from Hugging Face (k2-fsa ONNX files) if that fails; every file is pinned by size and SHA-256.
- **Files:** new `app/src/main/java/com/nuvio/tv/ui/screens/player/audiosync/**`, its tests,
  `res/raw/silero_vad_v5_16k.bin`, `res/values/audio_sync_strings.xml`, `assets/licenses/audio_sync_NOTICE.md`.
  Upstream files edited: `app/build.gradle.kts`, `app/proguard-rules.pro`, `PlayerRuntimeController{AutomaticSubtitleSync,
  Initialization,Lifecycle,Observers}.kt`, `settings/LicensesAttributionsScreen.kt`, `settings/PlaybackSubtitleSettings.kt`.
- **Commits:** `3fa527098`, `1bcbfff6c`, `5c3f82d69`, `bf3ab8e3f`, cherry-picks of `4fd4ffff6`, `50b433bca`, `d73467d79`,
  `9d72c7046` (each message ends with "cherry picked from commit …").
- **Remove:** revert the four cherry-picks, newest first.
- **Upstream status:** upstream PR #4150 (open).
- **Watch:** if the PR gets more commits, cherry-pick them too. When an upstream release contains the PR, merging it may
  conflict in the files above: take upstream's version and delete this entry. If the PR is closed without merging, revert.
  Check with `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.ui.screens.player.audiosync.*'`.

## K-07 Built-in Usenet streaming (upstream PR #3511)

- **Why:** try upstream's proposed on-device Usenet engine before it is merged: Usenet (NZB) sources play directly on the
  TV, without an external bridge.
- **What:** [NuvioMedia/NuvioTV#3511](https://github.com/NuvioMedia/NuvioTV/pull/3511) by haaihond, complete at head
  `b42ba6f1e`. A Go engine (`libnuvio_usenet.so`) runs in-process and streams over loopback; its settings are under
  Settings → Integrations → Usenet. The build uses the PR's prebuilt engine for the four ABIs (about 11 MB each, no Go
  needed); `python native/usenet/scripts/check_prebuilts.py` checks them against the vendored source. The head includes
  follow-ups by kernexshadow, merged into the PR branch (`nntp`) through haaihond/NuvioTV pull requests:
  - [#58](https://github.com/haaihond/NuvioTV/pull/58): once a provider and an indexer are set up, the addon list gets a
    "Built-in Usenet" row (toggle and move buttons, no Remove). Its place orders the results on the stream screen and in the
    player (next-episode auto-play, stream fallback), so *Auto-play first source* can reach Usenet before the addons below it.
    The place is stored per profile with the device-local Usenet sources, never in the synced addon order. Built-in Usenet
    always comes before plugins.
  - [#59](https://github.com/haaihond/NuvioTV/pull/59) and [#60](https://github.com/haaihond/NuvioTV/pull/60): the engine
    opens RAR sets stored inside a RAR set; the prebuilt binaries are rebuilt with it.
  - [#62](https://github.com/haaihond/NuvioTV/pull/62) and [#63](https://github.com/haaihond/NuvioTV/pull/63): the engine
    returns its memory to the OS after the last session closes (binaries rebuilt); stale Usenet notes are fixed.

  How it got here: the PR branch is not merged, because it carries upstream `dev` commits that are in no release. Its diff
  against the `dev` commit it last merged (`7596edc76`) was imported onto 1.1.0-beta.8 as one commit, leaving out the parts
  that relied on later `dev`; the later follow-ups were cherry-picked (#58 `927023efd`, #59 `e9c3d3d08`, #60 `666cc76e6`, #62 `0456c4ebe` and
  `5f274e426`, #63 `f10125281`). 1.1.0-beta.9
  contains `7596edc76`, so its merge restored the parts left out, and knuvio now matches the PR head exactly.
- **Files:** new `native/usenet/**`, `app/src/main/java/com/nuvio/tv/core/usenet/**`, new files in `core/di`,
  `core/player`, `core/server`, `core/streams`, `ui/screens/player` and `ui/screens/settings` (stream fallback, ranking,
  Usenet screens), their tests, three `res/values/*usenet*` files,
  `BUILT_IN_USENET.md`, `STREAM_FALLBACK.md`, `docs/USENET_SORTING.md`, `.github/workflows/usenet-tests.yml`. Upstream files
  edited: `app/build.gradle.kts`, `gradle/libs.versions.toml`, `NuvioApplication.kt`, `core/player/{FrameRateUtils,
  StreamAutoPlaySelector,SubtitleFileCache}.kt`, `core/streams/PlaybackAvailability.kt`,
  `data/local/StreamLinkCacheDataStore.kt`, `data/mapper/StreamMapper.kt`, `data/remote/api/TmdbApi.kt`,
  `data/remote/dto/StreamResponseDto.kt`, `data/repository/StreamRepositoryImpl.kt`, `domain/model/Stream.kt`,
  `ui/components/{PlaybackAvailabilityProvider,StreamBadgeChips}.kt`,
  `ui/screens/addon/{AddonManagerScreen,AddonManagerUiState,AddonManagerViewModel}.kt`,
  `ui/screens/player/{MpvStartupWatchdogPolicy,NuvioMpvSurfaceView,PlayerMediaSourceFactory,PlayerViewModel}.kt`, the
  `PlayerRuntimeController*.kt` files (base, ErrorRecovery, Initialization, Lifecycle, Mpv, MpvEvents, Observers,
  PlaybackEvents, Scrobble, Server, Startup, Streams, TrackSelection), `ui/screens/settings/{AdvancedSettingsViewModel,
  DiagnosticsCard,PlaybackSettingsViewModel,SettingsScreen}.kt`, `ui/screens/stream/{StreamScreen,StreamScreenViewModel}.kt`,
  `res/values/strings.xml`, four existing unit tests and two upstream workflows (disabled in knuvio).
- **Commits:** "knuvio: import upstream PR #3511 (built-in Usenet streaming)", "knuvio: import haaihond/NuvioTV PR #58
  (built-in Usenet among the addons)", the cherry-picks of `e9c3d3d08`, `666cc76e6`, `0456c4ebe`, `5f274e426` and
  `f10125281`, and the conflict resolution in "Merge upstream 1.1.0-beta.9".
- **Remove:** revert the cherry-picks and the two import commits, newest first (K-08 before them if both go). Where a
  revert conflicts, keep the upstream release's code.
- **Upstream status:** upstream PR #3511 (open).
- **Watch:** if the PR gets more commits, cherry-pick its new non-merge commits that are not in upstream `dev`
  (`git rev-list --reverse --no-merges b42ba6f1e..<new head> ^upstream/dev`) and update the head here. If it merges a newer
  upstream `dev`, leave out the parts that rely on `dev` after the current knuvio release and list them here until a release
  contains them. When an upstream release contains the PR, merging it conflicts in the files above: take upstream's version
  and delete this entry. If the PR is closed without merging, revert. Check with
  `python native/usenet/scripts/check_prebuilts.py` and
  `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.core.usenet.*' --tests '*Usenet*'`.

## K-08 Blu-ray clips and discs in ExoPlayer (upstream PR #696)

- **Why:** Blu-ray clips (`.m2ts`) and full disc releases fail in ExoPlayer and need an external player. With this change
  they play in the internal player, also from the built-in Usenet engine of K-07.
- **What:** [NuvioMedia/NuvioTV#696](https://github.com/NuvioMedia/NuvioTV/pull/696) by kernexshadow (head `3afa62cd0`),
  imported as one commit like K-07: the PR's diff against upstream `dev` `b700cf98e`, applied onto 1.1.0-beta.8 without
  conflicts and without changes. BDAV clips play and seek (EP map from the CLPI), TrueHD and PGS tracks are exposed, track
  languages come from the CLPI, a clip that is part of its feature plays the whole feature, and a disc titles button lists
  the extras. Disc images (`.iso`) play only through the K-07 engine, which serves the disc's files beside the clip.
- **Files:** new `ui/screens/player/{BdavM2tsDataSource,BdavPgsReader,BdavTrueHdReader,BlurayClipInfo,
  BlurayPlaylistResolver,PlayerRuntimeControllerDiscTitles}.kt` and five tests. Upstream files edited:
  `ui/screens/player/{PlayerMediaSourceFactory,PlayerScreen,PlayerUiState,PostPlayRecommendationState}.kt`, the
  `PlayerRuntimeController*.kt` files (base, EngineFailover, ErrorRecovery, Initialization, PlaybackEvents, Streams,
  TrackSelection; most are also edited by K-07), `res/values{,-pt-rPT,-pt-rBR}/strings.xml`.
- **Commits:** the commit "knuvio: import upstream PR #696 (Blu-ray clips and discs in ExoPlayer)".
- **Remove:** revert that commit (before K-07 if both go).
- **Upstream status:** upstream PR #696 (open).
- **Watch:** same as K-07: cherry-pick new non-merge commits of the PR that are not in upstream `dev`
  (`git rev-list --reverse --no-merges 3afa62cd0..<new head> ^upstream/dev`). Check with
  `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.ui.screens.player.*'`.

## K-10 Debrid link preparation off the main thread (upstream PR #4400)

- **Why:** with "Prepare links" on and a few thousand streams, every prepared link held the main thread for seconds, long
  enough for an input ANR on a SHIELD.
- **What:** [NuvioMedia/NuvioTV#4400](https://github.com/NuvioMedia/NuvioTV/pull/4400) by kernexshadow (head `062eb1e61`,
  based on 1.1.0-beta.9), cherry-picked unchanged. Link preparation runs on `Dispatchers.Default` on the stream screen and
  in the player's sources and episode panels, and `replacePreparedStream` compares the key fields instead of building a
  lowercased key for every stream.
- **Files:** `core/debrid/DirectDebridStreamPreparer.kt`, `ui/screens/player/PlayerRuntimeControllerStreams.kt` (also
  edited by K-07 and K-08), `ui/screens/stream/StreamScreenViewModel.kt` (also edited by K-07), new
  `DirectDebridStreamPreparerTest.kt`.
- **Commits:** cherry-pick of `062eb1e61` (its message ends with "cherry picked from commit …").
- **Remove:** revert the cherry-pick.
- **Upstream status:** upstream PR #4400 (open), fixes NuvioMedia/NuvioTV#4399.
- **Watch:** if the PR gets more commits, cherry-pick them too. When an upstream release contains the PR, take upstream's
  version in a conflict and delete this entry. If the PR is closed without merging, revert. Check with
  `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.core.debrid.*'`.

## K-11 Addon tab focus on the selected chip (upstream PR #4424)

- **Why:** with more addon tabs than fit on screen, switching addon from the stream results left focus on "All" or another
  tab while the results showed the selected addon, and up from the first result stayed in the list.
- **What:** [NuvioMedia/NuvioTV#4424](https://github.com/NuvioMedia/NuvioTV/pull/4424) by kernexshadow (head `c8f175cd8`,
  based on upstream `dev` after 1.1.0-beta.9; no `dev` commit since beta.9 touches its files), cherry-picked unchanged.
  `focusChip()` scrolls a tab into the row before requesting focus, and every tab focus request goes through it. While
  focus is in the results, the tab row scrolls only when the selected tab is off screen, instead of snapping back to the
  first tab. Same change in the player's sources and episodes panels.
- **Files:** `ui/screens/player/{StreamComponents,StreamSourcesSidePanel,EpisodesSidePanel}.kt`,
  `ui/screens/stream/StreamScreen.kt` (also edited by K-07, not in the tab row).
- **Commits:** cherry-pick of `c8f175cd8` (its message ends with "cherry picked from commit …").
- **Remove:** revert the cherry-pick.
- **Upstream status:** upstream PR #4424 (open), fixes NuvioMedia/NuvioTV#4423.
- **Watch:** if the PR gets more commits, cherry-pick them too. When an upstream release contains the PR, take upstream's
  version in a conflict and delete this entry. If the PR is closed without merging, revert. A new tab focus request in
  knuvio code must go through `focusChip()`.
