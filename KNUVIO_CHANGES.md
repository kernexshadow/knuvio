# knuvio changes

Everything knuvio adds on top of [NuvioMedia/NuvioTV](https://github.com/NuvioMedia/NuvioTV). Each entry says why the change
exists, which files it touches, and how to remove it. Read this first when an upstream merge conflicts.

Files under `app/src/full/res`, `app/src/fullDebug/res`, `knuvio-branding/` and the knuvio workflow are knuvio-only and cannot
conflict. **Upstream files that knuvio edits** are the ones to watch:

| Upstream file | Changed by |
|---|---|
| `app/build.gradle.kts` | [K-02](#k-02-application-ids-and-updater-source), [K-06](#k-06-audio-based-subtitle-sync-upstream-pr-4150), [K-07](#k-07-built-in-usenet-streaming-upstream-pr-4426) |
| `app/src/main/java/com/nuvio/tv/updater/VersionUtils.kt` | [K-05](#k-05-knuvio-revisions-in-the-updater) |
| `app/proguard-rules.pro`, player and settings files listed in K-06 | [K-06](#k-06-audio-based-subtitle-sync-upstream-pr-4150) |
| `gradle/libs.versions.toml`, addon manager, stream, player and settings files listed in K-07 | [K-07](#k-07-built-in-usenet-streaming-upstream-pr-4426) |
| Player files and Portuguese strings listed in K-08 | [K-08](#k-08-blu-ray-clips-and-discs-in-exoplayer-upstream-pr-696) |

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
  (head `1c523005f`), cherry-picked unchanged at head `9d72c7046`. The author rebased the PR onto 1.1.0-beta.12 as
  `1c523005f` (same four commits, only adapted to beta.12); the beta.12 merge resolves its conflict as the rebased PR does, so
  knuvio matches it exactly. The build downloads the sherpa-onnx AAR from GitHub (pinned version and
  SHA-256). On first use the app downloads the speech model, about 74 MB, from the PR author's GitHub release (ORT
  conversion), or from Hugging Face (k2-fsa ONNX files) if that fails; every file is pinned by size and SHA-256.
  Plus `d56f38a18`, our fix proposed into the PR's branch as
  [DavidVamaiotu/NuvioTV-Reshaped#70](https://github.com/DavidVamaiotu/NuvioTV-Reshaped/pull/70): when the audio sync tests
  other subtitles, regional variants stay apart, so a pt-PT subtitle is never swapped for a pt-BR one (same for es-419 and
  Traditional Chinese). It only changes `SubtitleCandidatePool.languageKey` and its test.
- **Files:** new `app/src/main/java/com/nuvio/tv/ui/screens/player/audiosync/**`, its tests,
  `res/raw/silero_vad_v5_16k.bin`, `res/values/audio_sync_strings.xml`, `assets/licenses/audio_sync_NOTICE.md`.
  Upstream files edited: `app/build.gradle.kts`, `app/proguard-rules.pro`, `PlayerRuntimeController{AutomaticSubtitleSync,
  Initialization,Lifecycle,Observers}.kt`, `settings/LicensesAttributionsScreen.kt`, `settings/PlaybackSubtitleSettings.kt`.
- **Commits:** `3fa527098`, `1bcbfff6c`, `5c3f82d69`, `bf3ab8e3f`, cherry-picks of `4fd4ffff6`, `50b433bca`, `d73467d79`,
  `9d72c7046` (each message ends with "cherry picked from commit …"), the conflict resolution in "Merge upstream
  1.1.0-beta.12", and `a8752a302` (cherry-pick of `d56f38a18`, PR #70).
- **Remove:** revert `a8752a302`, then the four cherry-picks, newest first. Where a revert conflicts, keep the upstream
  release's code.
- **Upstream status:** upstream PR #4150 (open). The regional-language fix is PR #70 into its branch (open).
- **Watch:** if the PR gets more commits, cherry-pick them too. If it is rebased again, compare the PR head's files with
  knuvio (`git diff <head> -- <PR files>`): only other knuvio changes may differ. Once #70 is merged, the PR head contains
  `d56f38a18` or a rebased copy, and the comparison must then show no difference in `SubtitleCandidatePool*`. If #70 is
  declined, keep `a8752a302` as a knuvio-only fix on top of the PR. When an upstream release contains the PR,
  merging it may conflict in the files above: take upstream's version and delete this entry. If the PR is closed without merging, revert.
  Check with `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.ui.screens.player.audiosync.*'`.

## K-07 Built-in Usenet streaming (upstream PR #4426)

- **Why:** try upstream's proposed on-device Usenet engine before it is merged: Usenet (NZB) sources play directly on the
  TV, without an external bridge.
- **What:** [NuvioMedia/NuvioTV#4426](https://github.com/NuvioMedia/NuvioTV/pull/4426) by haaihond (branch `full-nntp`),
  complete at head `349264aef`. A Go engine (`libnuvio_usenet.so`) runs in-process and streams over loopback; its settings
  are under Settings → Integrations → Usenet. The engine binaries for the four ABIs (about 11 MB each) are not in Git: the
  build downloads them from the GitHub release pinned in `native/usenet/prebuilt/manifest.json` (currently on
  haaihond/NuvioTV), checks their SHA-256 and caches them in `native/usenet/prebuilt/` (ignored). No Go is needed, but the
  first build needs network access; `-PbuildUsenetFromSource=true` builds them from the vendored source instead (Go, NDK,
  CMake). The head includes follow-ups by kernexshadow, merged into the PR branch through haaihond/NuvioTV pull requests:
  - [#58](https://github.com/haaihond/NuvioTV/pull/58): once a provider and an indexer are set up, the addon list gets a
    "Built-in Usenet" row (toggle and move buttons, no Remove). Its place orders the results on the stream screen and in the
    player (next-episode auto-play, stream fallback), so *Auto-play first source* can reach Usenet before the addons below it.
    The place is stored per profile with the device-local Usenet sources, never in the synced addon order. Built-in Usenet
    always comes before plugins.
  - [#59](https://github.com/haaihond/NuvioTV/pull/59) and [#60](https://github.com/haaihond/NuvioTV/pull/60): the engine
    opens RAR sets stored inside a RAR set.
  - [#62](https://github.com/haaihond/NuvioTV/pull/62) and [#63](https://github.com/haaihond/NuvioTV/pull/63): the engine
    returns its memory to the OS after the last session closes; stale Usenet notes are fixed.
  - [#64](https://github.com/haaihond/NuvioTV/pull/64): every episode is searched on its own, and multi-season packs match
    each of their seasons.
  - [#65](https://github.com/haaihond/NuvioTV/pull/65): indexer searches list up to 500 or all results and page by the
    reported total.
  - [#66](https://github.com/haaihond/NuvioTV/pull/66) and [#67](https://github.com/haaihond/NuvioTV/pull/67): each listed
    release's outcome is looked up once, and the release parser's own patterns run on `java.util.regex`.
  - [#69](https://github.com/haaihond/NuvioTV/pull/69): the first time a profile turns on built-in indexer search, a notice
    explains that searches and downloads go directly from the device with the user's own accounts and cost API hits.
  - [#70](https://github.com/haaihond/NuvioTV/pull/70): a release kept for Reuse Last Link no longer stores its indexer's
    API key (it refers to the indexer, and links kept by earlier versions are rewritten); each profile's sources are
    decrypted once and then read from memory.
  - [#72](https://github.com/haaihond/NuvioTV/pull/72) and [#73](https://github.com/haaihond/NuvioTV/pull/73): Usenet
    diagnostics show statistics per indexer (searches, API requests, response time, NZB downloads, playback outcome) and
    per provider (articles served and missing, bytes, errors, opens that failed because of it), for 7 days, 30 days or all
    time, and for movies, shows or both.
  - [#74](https://github.com/haaihond/NuvioTV/pull/74): with the NZB cache on, the engine opens NZBs beyond the in-memory
    limits (up to 2,000,000 articles and 256 MiB of XML), and plays an episode from a season of Blu-ray discs posted
    without folders.
  - [#75](https://github.com/haaihond/NuvioTV/pull/75): a Usenet source keeps its statistics when it is edited.
  - [#76](https://github.com/haaihond/NuvioTV/pull/76), [#77](https://github.com/haaihond/NuvioTV/pull/77) and
    [#78](https://github.com/haaihond/NuvioTV/pull/78): RAR sets start faster and open more often: a read near the end
    comes from the last volume instead of walking every volume, a volume whose name has a posting tool's prefix stays in
    its set, and volume names shuffled in small windows are ordered by their NZB subjects.
  - [#79](https://github.com/haaihond/NuvioTV/pull/79): the "Opening Usenet stream" message follows Show loading status,
    and the stream speed test is disabled for links served from the device.
  - [#80](https://github.com/haaihond/NuvioTV/pull/80): the next-stream fallback message says why the last Usenet source
    failed.
  - [#81](https://github.com/haaihond/NuvioTV/pull/81): a video split into numbered parts without an archive plays as one
    file, and a stored RAR entry without a video extension is recognised by its first bytes.

  haaihond's own commits on the PR branch since then: separate User-Agent settings for indexer searches and NZB downloads
  (an existing shared override is migrated to both), and a server icon in the Usenet integration settings.

  How it got here: the PR branch is not merged, because it can carry upstream `dev` commits that are in no release. knuvio
  first followed [#3511](https://github.com/NuvioMedia/NuvioTV/pull/3511), the same work with the engine binaries committed:
  its diff against `dev` `7596edc76` was imported onto 1.1.0-beta.8 as one commit, the follow-ups #58 to #63 were
  cherry-picked, and 1.1.0-beta.9 restored the parts that relied on later `dev`. haaihond closed #3511 on 2026-11-01 and
  opened #4426 from a rewritten history without binaries (`b42ba6f1e` there is `f5e7ca7f6`). knuvio then cherry-picked the
  #4426 commits after `f5e7ca7f6` (the binary download and #64 to #67) and deleted the committed binaries, which remain in
  knuvio's older history. All `dev` commits in #4426 are in 1.1.0-beta.10, and the beta.10 merge resolves its conflicts as
  #4426 resolves them, so knuvio matches the PR head exactly. The same holds after the PR's later `dev` merges up to
  `8f451a88b`, which are contained in 1.1.0-beta.13. The merges in `6ca8894c1` and `48b0a2488` (`dev` up to `01759ead3`)
  were left out of the 1.1.0 revisions and are contained in 1.2.0-beta.1. Its merge conflicted only in the imports of
  `NuvioMpvSurfaceView`, resolved as the PR resolves them, so knuvio matches the PR head again, apart from K-02, K-06,
  K-08 and the `dev` code that 1.2.0-beta.1 adds after `01759ead3`.
- **Files:** new `native/usenet/**`, `app/src/main/java/com/nuvio/tv/core/usenet/**`, new files in `core/di`,
  `core/player`, `core/server`, `core/streams`, `ui/screens/player` and `ui/screens/settings` (stream fallback, ranking,
  Usenet screens), their tests, three `res/values/*usenet*` files,
  `BUILT_IN_USENET.md`, `STREAM_FALLBACK.md`, `docs/USENET_SORTING.md`, `tests/usenet_prebuilts_test.py`,
  `.github/workflows/usenet-tests.yml`, `.github/workflows/usenet-native-assets.yml`. Upstream files
  edited: `app/build.gradle.kts`, `gradle/libs.versions.toml`, `NuvioApplication.kt`, `core/player/{FrameRateUtils,
  StreamAutoPlaySelector,SubtitleFileCache}.kt`, `core/streams/PlaybackAvailability.kt`,
  `data/local/StreamLinkCacheDataStore.kt`, `data/mapper/StreamMapper.kt`, `data/remote/api/TmdbApi.kt`,
  `data/remote/dto/StreamResponseDto.kt`, `data/repository/StreamRepositoryImpl.kt`, `domain/model/Stream.kt`,
  `ui/components/{PlaybackAvailabilityProvider,StreamBadgeChips}.kt`,
  `ui/screens/addon/{AddonManagerScreen,AddonManagerUiState,AddonManagerViewModel}.kt`,
  `ui/screens/player/{MpvStartupWatchdogPolicy,NuvioMpvSurfaceView,PlayerMediaSourceFactory,PlayerViewModel}.kt`, the
  `PlayerRuntimeController*.kt` files (base, ErrorRecovery, Initialization, Lifecycle, Mpv, MpvEvents, Observers,
  PlaybackEvents, Scrobble, Server, Startup, Streams, TrackSelection), `ui/screens/settings/{AdvancedSettingsViewModel,
  DiagnosticsCard,NetworkSettingsScreen,PlaybackSettingsViewModel,SettingsScreen}.kt`, `ui/screens/stream/{StreamScreen,StreamScreenViewModel}.kt`,
  `res/values/strings.xml`, four existing unit tests and two upstream workflows (disabled in knuvio).
- **Commits:** "knuvio: import upstream PR #3511 (built-in Usenet streaming)", "knuvio: import haaihond/NuvioTV PR #58
  (built-in Usenet among the addons)", the cherry-picks of `e9c3d3d08`, `666cc76e6`, `0456c4ebe`, `5f274e426`,
  `f10125281` (from #3511) and of `965cd752b`, `9d34682e9`, `0e4859f8d`, `4659845a2`, `c3ce4b500`, `d2bb6fc77`,
  `459578977`, `ee048bb39`, `8026aa4ff`, `45eff47d9`, `99fcc5cba`, `86f0bd10b`, `b0a3130cf`, `d1052741e`, `e61634f9a`,
  `89c510292`, `ee8117851`, `4f133e7b5`, `2db3c481f`, `dcbff8aa9`, `c2c5b3b0f`, `9d70bbe26`, `963e073fd`, `09a55f3d3`,
  `2d8aa575e`, `0fa315835`, `24fde2a74`, `da950d354`, `c3b21ab4c`, `6ffe8fef2`, `2600817af`, `30ba4e35a`, `1c8c83b42`,
  `cd37250b9`, `0b662dda0`, `78eb82f38`, `b6994ac6e`, `a6a88d7ab`, `814986a9f` (from #4426; `0b662dda0` and `78eb82f38`
  rebuilt the engine on parallel branches, so their `manifest.json` conflicts were resolved with each commit's version), "knuvio: drop the committed Usenet engine binaries",
  and the conflict resolutions in "Merge upstream 1.1.0-beta.9", "Merge upstream 1.1.0-beta.10" and "Merge upstream
  1.2.0-beta.1".
- **Remove:** revert those commits, newest first (K-08 before them if both go). Where a revert conflicts, keep the upstream
  release's code.
- **Upstream status:** upstream PR #4426 (open), which replaces #3511 (closed without merging on 2026-11-01).
- **Watch:** if the PR gets more commits, cherry-pick its new non-merge commits that are not in upstream `dev`
  (`git rev-list --reverse --no-merges 349264aef..<new head> ^upstream/dev`) and update the head here. If it merges a newer
  upstream `dev`, leave out the parts that rely on `dev` after the current knuvio release and list them here until a release
  contains them. A commit that changes the engine changes `prebuilt/manifest.json` too; its pinned release must exist, or the
  build fails. If the binaries move to a NuvioMedia release, only the manifest changes. When an upstream release contains the
  PR, merging it conflicts in the files above: take upstream's version and delete this entry. If the PR is closed without
  merging, revert. Check with `python native/usenet/scripts/fetch_prebuilts.py`,
  `python native/usenet/scripts/check_prebuilts.py` and
  `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.core.usenet.*' --tests '*Usenet*'`.
- **Watch, two source fallbacks:** 1.2.0-beta.1 adds upstream's own fallback to the next matching source
  (`PlayerRuntimeControllerSourceFallback.kt`, from NuvioMedia/NuvioTV#4581, `c3a27b5e2`), next to this PR's
  `StreamFallbackSession`. The PR has not merged that `dev` yet, so nothing reconciles the two. Both are off by default.
  With both on, in ExoPlayer's error handling a permanent Usenet failure goes to the PR's fallback first and any other
  error before the first frame to upstream's. When the PR merges `dev` past `c3a27b5e2`, take its resolution.

## K-08 Blu-ray clips and discs in ExoPlayer (upstream PR #696)

- **Why:** Blu-ray clips (`.m2ts`) and full disc releases fail in ExoPlayer and need an external player. With this change
  they play in the internal player, also from the built-in Usenet engine of K-07.
- **What:** [NuvioMedia/NuvioTV#696](https://github.com/NuvioMedia/NuvioTV/pull/696) by kernexshadow (head `98e05d4ea`),
  imported as one commit like K-07: the PR's diff against upstream `dev` `b700cf98e`, applied onto 1.1.0-beta.8 without
  conflicts and without changes. BDAV clips play and seek (EP map from the CLPI), TrueHD and PGS tracks are exposed, track
  languages come from the CLPI, a clip that is part of its feature plays the whole feature, and a disc titles button lists
  the extras. Disc images (`.iso`) play only through the K-07 engine, which serves the disc's files beside the clip.
  A disc title keeps the player's engine when it restarts playback, an extra that fails or ends returns to the feature,
  and playlist clips are read with the loopback read timeout.
- **Files:** new `ui/screens/player/{BdavM2tsDataSource,BdavPgsReader,BdavTrueHdReader,BlurayClipInfo,
  BlurayPlaylistResolver,PlayerRuntimeControllerDiscTitles}.kt` and five tests. Upstream files edited:
  `ui/screens/player/{PlayerMediaSourceFactory,PlayerScreen,PlayerUiState,PostPlayRecommendationController,
  PostPlayRecommendationState}.kt`, the `PlayerRuntimeController*.kt` files (base, EngineFailover, ErrorRecovery,
  Initialization, Metadata, Observers, PlaybackEvents, Streams, TrackSelection; most are also edited by K-07),
  `res/values{,-pt-rPT,-pt-rBR}/strings.xml`.
- **Commits:** the commit "knuvio: import upstream PR #696 (Blu-ray clips and discs in ExoPlayer)" and the
  cherry-picks of `ea3193907`, `0ae08ec0d`, `0cf406aed` and `98e05d4ea`. In Initialization and Observers, an extra that fails returns to
  the feature before K-07's Usenet failure handling and stream fallback run.
- **Remove:** revert the cherry-picks and that commit, newest first (before K-07 if both go).
- **Upstream status:** upstream PR #696 (open).
- **Watch:** same as K-07: cherry-pick new non-merge commits of the PR that are not in upstream `dev`
  (`git rev-list --reverse --no-merges 98e05d4ea..<new head> ^upstream/dev`). Check with
  `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.ui.screens.player.*'`.
