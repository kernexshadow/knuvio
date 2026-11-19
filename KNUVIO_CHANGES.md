# knuvio changes

Everything knuvio adds on top of [NuvioMedia/NuvioTV](https://github.com/NuvioMedia/NuvioTV). Each entry says why the change
exists, which files it touches, and how to remove it. Read this first when an upstream merge conflicts.

Files under `app/src/full/res`, `app/src/fullDebug/res`, `knuvio-branding/` and the knuvio workflow are knuvio-only and cannot
conflict. **Upstream files that knuvio edits** are the ones to watch:

| Upstream file | Changed by |
|---|---|
| `app/build.gradle.kts` | [K-02](#k-02-application-ids-and-updater-source), [K-06](#k-06-audio-based-subtitle-sync-upstream-pr-4150), [K-07](#k-07-built-in-usenet-streaming-upstream-pr-4679), [K-12](#k-12-embedded-art-profile-and-compilation-status) |
| `app/src/main/java/com/nuvio/tv/updater/VersionUtils.kt` | [K-05](#k-05-knuvio-revisions-in-the-updater) |
| `app/proguard-rules.pro`, player and settings files listed in K-06 | [K-06](#k-06-audio-based-subtitle-sync-upstream-pr-4150) |
| `gradle/libs.versions.toml`, addon manager, stream, player and settings files listed in K-07 | [K-07](#k-07-built-in-usenet-streaming-upstream-pr-4679) |
| Player files and Portuguese strings listed in K-08 | [K-08](#k-08-blu-ray-clips-and-discs-in-exoplayer-upstream-pr-696) |
| `core/player/dvmkv/{DefaultEbmlReader,EbmlProcessor,MatroskaExtractor}.java`, `baseline-prof.txt` | [K-09](#k-09-read-mkv-cues-in-one-go-upstream-pr-4700) |
| `PlayerRuntimeController{,Initialization}.kt`, `MetaDetailsViewModel.kt`, `StreamScreenViewModel.kt` | [K-10](#k-10-prewarm-the-first-playback-upstream-pr-4701) |
| `PlayerMediaSourceFactory.kt`, `PlayerRuntimeControllerInitialization.kt` (one line) | [K-11](#k-11-autosync-on-blu-ray-clips) |
| `ui/screens/settings/UpdateChannelSettings.kt` (one line) | [K-12](#k-12-embedded-art-profile-and-compilation-status) |

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
- **What:** [NuvioMedia/NuvioTV#4150](https://github.com/NuvioMedia/NuvioTV/pull/4150) by DavidVamaiotu, complete at head
  `e9d460251`. The four original commits were cherry-picked unchanged at head `9d72c7046`; the author rebased the PR onto
  1.1.0-beta.12 as `1c523005f`, and the beta.12 merge resolves its conflict as the rebased PR does. Plus `d56f38a18`, our
  fix proposed into the PR's branch as
  [DavidVamaiotu/NuvioTV-Reshaped#70](https://github.com/DavidVamaiotu/NuvioTV-Reshaped/pull/70): when the audio sync tests
  other subtitles, regional variants stay apart, so a pt-PT subtitle is never swapped for a pt-BR one (same for es-419 and
  Traditional Chinese). It only changes `SubtitleCandidatePool.languageKey` and its test. The author then rebased the PR
  onto `dev` `5ad41476a` (contained in 1.2.0-beta.1) with that fix as `c1201940a`, and knuvio matched it exactly at that
  commit. On top, the PR's `ee6aa9008` (second review: fallback off by default, audio sampling Low by default, mpv support
  through dialogue spots and a retimed SRT copy, much faster word matching, less recognizer memory), `51aedfe85` (more
  reliable locks, steadier recognition), `465473a26` (interrupted spot sampling resumes for the next subtitle; a sync found
  through a bridged English reference is confirmed only when corroborated), `9091ccb5e` (no result toasts: a synced
  subtitle is retimed silently and keeps the "Auto synced" chip), `6308322f4` (English references download sooner and
  stay cached for the app, last 8 files; speech is recognised while they download), `127099b56` (an ambiguous
  speech-activity match is confirmed by where subtitle lines start) and `c6707a541` (when no whole-film lock passes, as
  with a subtitle made for another cut, it locks on the audio around the playhead) were cherry-picked unchanged,
  and so were the PR's next twelve commits, `9f4ed6c08` to `e9d460251`: frame-rate choice (the 0.1% stretched rate
  when overlap and line starts both favour it, the 23.976-based PAL rate unless 25/24 clearly fits better, and waiting
  for a rate that clearly beats the other families), a speech-activity lock withdrawn when minutes of audio no longer
  support it, searches skipped for a clearly unmatched subtitle until more audio arrives, results from a forgotten
  audio track or stream discarded, English references fetched only when the speech model is downloaded, a background
  priority decoder thread, aligner buffers and FFT sizes reused, shorter setting descriptions and Polish translations.
  The build downloads the sherpa-onnx AAR from GitHub (pinned version and SHA-256). The speech model, about 74 MB, is
  downloaded only from the button in Settings, from Hugging Face (k2-fsa ONNX files at a pinned commit), every file pinned
  by size and SHA-256; without it a session uses speech detection only.
- **Files:** new `app/src/main/java/com/nuvio/tv/ui/screens/player/audiosync/**`, its tests,
  `res/raw/silero_vad_v5_16k.bin`, `res/values{,-pl}/audio_sync_strings.xml`, `assets/licenses/audio_sync_NOTICE.md`.
  Upstream files edited: `app/build.gradle.kts`, `app/proguard-rules.pro`, `ui/screens/player/NuvioMpvSurfaceView.kt`,
  `PlayerRuntimeController{AutomaticSubtitleSync,Initialization,Lifecycle,Observers}.kt`,
  `settings/LicensesAttributionsScreen.kt`, `settings/PlaybackSubtitleSettings.kt`.
- **Commits:** `3fa527098`, `1bcbfff6c`, `5c3f82d69`, `bf3ab8e3f`, cherry-picks of `4fd4ffff6`, `50b433bca`, `d73467d79`,
  `9d72c7046` (each message ends with "cherry picked from commit …"), the conflict resolution in "Merge upstream
  1.1.0-beta.12", `a8752a302` (cherry-pick of `d56f38a18`, PR #70), and the cherry-picks of `ee6aa9008`, `51aedfe85`,
  `465473a26`, `9091ccb5e`, `6308322f4`, `127099b56`, `c6707a541`, and of the twelve commits `9f4ed6c08` to `e9d460251`.
- **Remove:** revert the cherry-picks of `e9d460251` back to `9f4ed6c08`, then `c6707a541`, `127099b56`, `6308322f4`, `9091ccb5e`, `465473a26`, `51aedfe85`
  and `ee6aa9008`, then `a8752a302`, then the four original cherry-picks, newest first. Where a revert conflicts, keep the upstream release's code.
- **Upstream status:** upstream PR #4150 (open). The regional-language fix is in the PR as `c1201940a`; PR #70 itself is
  still open.
- **Watch:** if the PR gets more commits, cherry-pick the ones after `e9d460251`. If it is rebased again, compare the PR
  head's files with knuvio (`git diff <head> -- $(git diff --name-only <base> <head>)`): only other knuvio changes may
  differ, and nothing in `audiosync/` or `SubtitleCandidatePool*`. When an upstream release contains the PR,
  merging it may conflict in the files above: take upstream's version and delete this entry. If the PR is closed without merging, revert.
  Check with `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.ui.screens.player.audiosync.*'`.

## K-07 Built-in Usenet streaming (upstream PR #4679)

- **Why:** try upstream's proposed on-device Usenet engine before it is merged: Usenet (NZB) sources play directly on the
  TV, without an external bridge.
- **What:** [NuvioMedia/NuvioTV#4679](https://github.com/NuvioMedia/NuvioTV/pull/4679) by haaihond (branch `usenet` on
  haaihond/NuvioTV), complete at head `cfa9f6d24`. It replaced [#4426](https://github.com/NuvioMedia/NuvioTV/pull/4426)
  (branch `full-nntp`) with the same app code and the engine in its own repository. A Go engine (`libnuvio_usenet.so`) runs
  in-process and streams over loopback; its settings are under Settings → Integrations → Usenet. The engine lives in
  [NuvioMedia/nuvio-usenet-engine](https://github.com/NuvioMedia/nuvio-usenet-engine) (revision pinned in
  `native/usenet/engine-source.json`); its binaries for the four ABIs (about 11 MB each) are not in Git: the build
  downloads them from the release pinned in `native/usenet/prebuilt/manifest.json`, checks their SHA-256 and caches them
  in `native/usenet/prebuilt/` (ignored). No Go is needed, but the first build needs network access;
  `-PbuildUsenetFromSource=true -PusenetEngineSourceDir=<engine checkout>` builds them from source instead (Go, NDK,
  CMake). The app code includes follow-ups by kernexshadow, merged into `full-nntp` through haaihond/NuvioTV pull requests
  before the move:
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
  - [#83](https://github.com/haaihond/NuvioTV/pull/83): a large obfuscated 7z set (16 or more volumes numbered in their
    subjects) is taken in NZB subject order once a spread sample of volumes confirms the predicted names, instead of
    reading every volume's first article first (481 volumes: about 355 MB and 7–23 s before playback). Each other volume
    is checked against its predicted name when first read. Engine binaries rebuilt (`usenet-native-82bc215e7261022b`).
  - [#84](https://github.com/haaihond/NuvioTV/pull/84): the engine reads the usual NZB shape straight from its bytes and
    leaves anything else to `encoding/xml`, with the same values, limits and errors (a 16 MB NZB on a 32-bit box: 1.15 s
    instead of 7.7 s; a cold open with the NZB cache 2.9 s instead of 9.6 s). Engine binaries rebuilt
    (`usenet-native-432c5c5998d2ab89`).
  - [#85](https://github.com/haaihond/NuvioTV/pull/85): a movie's ID search results are checked against its TMDB details
    (one request with alternative titles and translations), asked for alongside the indexers: results whose names give
    only years more than one off, or the title of another film, are dropped. Obfuscated names and names without a title
    pass; without the details the results are listed unchecked; when nothing is left, the movie is searched by title.
  - [#86](https://github.com/haaihond/NuvioTV/pull/86): a movie's Usenet release is its own binge group, so Reuse Binge
    Group opens the same release again (series keep one group per upload).
  - [#87](https://github.com/haaihond/NuvioTV/pull/87): when the engine gives up on a stream (410 with
    `X-Usenet-Failure`), the error screen names the reason (missing or damaged parts, refused login, used-up quota, no
    real video) instead of "link has expired".
  - [#88](https://github.com/haaihond/NuvioTV/pull/88): "Results per indexer" (Search results) chooses how many results
    each indexer search reads: Auto (default, as before: 200, or the maximum results when higher), 100, 200, 500 or 1000.
    100 keeps every search to one page, so an episode costs at most two API hits per indexer.

  On #4679: haaihond's per-indexer fetch limits when paging Newznab searches (TV and phone settings, with an explanation
  of Hydra pagination and the display limit), and kernexshadow's
  [#90](https://github.com/haaihond/NuvioTV/pull/90) (the auto-play cover stays while a Usenet stream hands off to the
  player) and [#92](https://github.com/haaihond/NuvioTV/pull/92) (a connection tuner for Usenet providers), followed by
  haaihond's tuner changes: provider refusals are confirmed before the connection allowance is lowered, a gain over the
  saved allowance must repeat, NNTP ports are compared at equal connection counts, and outstanding connections close
  before another run. The same #90 and #92 changes went into `full-nntp` as #89 and #91. Then
  [#93](https://github.com/haaihond/NuvioTV/pull/93): the tuner waits for provider slots freed late (retries after 5, 10
  and 20 s, at most a minute per run), still reports the limit after a later failure, treats sign-in replies that report a
  connection ceiling as refusals (Test provider too), and says "Nothing to apply:" when the result matches the settings.

  Engine ahead of the PR: knuvio pins `nuvio-usenet-engine` `main` at `65da4c88b` (its PR #4, release
  `usenet-native-7932d95b42f26ecb`) instead of the PR's `e4b0717ae` (`usenet-native-b6ca59925e184dce`). It adds haaihond's
  fixes for byte-range seeks around missing articles, first-read errors on secondary Blu-ray clips (reported as 410 with
  `X-Usenet-Failure`, like the feature), fetch contexts released when producers finish, and the episode order on
  incomplete Blu-ray discs. The app's HTTP contract with the engine is unchanged. Only `engine-source.json` and
  `prebuilt/manifest.json` differ from the PR head; when the PR pins this release or a newer one, take the PR's files.

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
  K-08 and the `dev` code that 1.2.0-beta.1 adds after `01759ead3`. The PR then merged `dev` up to `e0e830b60`
  (`635bc983c`, `e9e95ec98`), which contains 1.2.0-beta.1, so those beta.1 differences are gone. Both merges were left
  out of the 1.2.0-beta.1 revisions, because their conflict resolutions in `PlayerRuntimeControllerStreams.kt`,
  `StreamScreenViewModel.kt` and `AddonManagerViewModel.kt` fit the PR to `dev` code after 1.2.0-beta.1 (#4624's
  auto-play fallback for the next episode and on the stream screen, #4629, #4633). 1.2.0-beta.2 contains `e0e830b60`
  and does not change those three files after it, so its merge takes the PR head's version of all three; in
  `PlayerRuntimeControllerStreams.kt` it puts back K-08's two changes (the Blu-ray state reset in
  `applySelectedStreamState` and `bluray = currentStreamBluray` in `switchToSourceStream`). knuvio matches the PR head
  merged with 1.2.0-beta.2 again, apart from K-02, K-06 and K-08. On 2026-11-16 haaihond closed #4426 in favour of
  #4679: four new commits on `dev` `2c853c178` (1.2.0-beta.2) that carry the app code of `full-nntp` `671f1b1d7` and take
  the engine as a pinned dependency (`3063a97f8` there). Its app files matched knuvio apart from K-02, K-06 and K-08, so
  "knuvio: take the Usenet engine as #4679's pinned dependency" only matched it outside the app code (the vendored engine
  source and its two workflows deleted, the pinned release, licenses, prebuilt scripts and their test taken), and the
  #4679 commits after `3063a97f8` were cherry-picked.
- **Files:** new `native/usenet/**` (pinned engine release, licenses, build and prebuilt scripts), `app/src/main/java/com/nuvio/tv/core/usenet/**`, new files in `core/di`,
  `core/player`, `core/server`, `core/streams`, `ui/screens/player` and `ui/screens/settings` (stream fallback, ranking,
  Usenet screens), their tests, three `res/values/*usenet*` files,
  `BUILT_IN_USENET.md`, `STREAM_FALLBACK.md`, `docs/USENET_SORTING.md`, `tests/usenet_prebuilts_test.py`. Upstream files
  edited: `app/build.gradle.kts`, `gradle/libs.versions.toml`, `NuvioApplication.kt`, `core/player/{FrameRateUtils,
  StreamAutoPlaySelector,SubtitleFileCache}.kt`, `core/streams/PlaybackAvailability.kt`,
  `data/local/StreamLinkCacheDataStore.kt`, `data/mapper/StreamMapper.kt`, `data/remote/api/TmdbApi.kt`,
  `data/remote/dto/StreamResponseDto.kt`, `data/repository/StreamRepositoryImpl.kt`, `domain/model/Stream.kt`,
  `ui/components/{PlaybackAvailabilityProvider,StreamBadgeChips}.kt`,
  `ui/screens/addon/{AddonManagerScreen,AddonManagerUiState,AddonManagerViewModel}.kt`,
  `ui/screens/player/{MpvStartupWatchdogPolicy,NuvioMpvSurfaceView,PlayerMediaSourceFactory,PlayerViewModel}.kt`, the
  `PlayerRuntimeController*.kt` files (base, ErrorRecovery, Initialization, Lifecycle, Mpv, MpvEvents, Observers,
  PlaybackEvents, Scrobble, Server, Startup, Streams, TrackSelection), `ui/screens/settings/{AdvancedSettingsViewModel,
  DiagnosticsCard,NetworkSettingsScreen,PlaybackSettingsViewModel,SettingsDesignSystem,SettingsScreen}.kt`, `ui/screens/stream/{StreamScreen,StreamScreenViewModel}.kt`,
  `res/values/strings.xml`, four existing unit tests and two upstream workflows (disabled in knuvio).
- **Commits:** "knuvio: import upstream PR #3511 (built-in Usenet streaming)", "knuvio: import haaihond/NuvioTV PR #58
  (built-in Usenet among the addons)", the cherry-picks of `e9c3d3d08`, `666cc76e6`, `0456c4ebe`, `5f274e426`,
  `f10125281` (from #3511) and of `965cd752b`, `9d34682e9`, `0e4859f8d`, `4659845a2`, `c3ce4b500`, `d2bb6fc77`,
  `459578977`, `ee048bb39`, `8026aa4ff`, `45eff47d9`, `99fcc5cba`, `86f0bd10b`, `b0a3130cf`, `d1052741e`, `e61634f9a`,
  `89c510292`, `ee8117851`, `4f133e7b5`, `2db3c481f`, `dcbff8aa9`, `c2c5b3b0f`, `9d70bbe26`, `963e073fd`, `09a55f3d3`,
  `2d8aa575e`, `0fa315835`, `24fde2a74`, `da950d354`, `c3b21ab4c`, `6ffe8fef2`, `2600817af`, `30ba4e35a`, `1c8c83b42`,
  `cd37250b9`, `0b662dda0`, `78eb82f38`, `b6994ac6e`, `a6a88d7ab`, `814986a9f`, `ee21a9816`, `1c4a60c50`, `5e99c8c52`, `d13880a5f`, `05a66ef6e`,
  `9ff432986`, `2a5b19c37`, `e7b694a84`, `433cb5a1b` (from #4426; `0b662dda0` and `78eb82f38`
  rebuilt the engine on parallel branches, so their `manifest.json` conflicts were resolved with each commit's version), "knuvio: drop the committed Usenet engine binaries",
  the conflict resolutions in "Merge upstream 1.1.0-beta.9", "Merge upstream 1.1.0-beta.10", "Merge upstream
  1.2.0-beta.1" and "Merge upstream 1.2.0-beta.2", "knuvio: take the Usenet engine as #4679's pinned dependency", and the
  cherry-picks of `e0255815e`, `a97133b69`, `05cd2182b`, `bd113d27a`, `e9009ae50`, `f19852eed`, `5d9ad4e73`, `f9731ceb0`,
  `5c1ff0d52`, `5b2099d79`, `9df356b21` (from #4679), and "knuvio: pin Usenet engine release 7932d95b".
- **Remove:** revert those commits, newest first (K-08 before them if both go). Where a revert conflicts, keep the upstream
  release's code.
- **Upstream status:** upstream PR #4679 (open), which replaces #4426 (closed without merging on 2026-11-16), which
  replaced #3511 (closed without merging on 2026-11-01).
- **Watch:** if the PR gets more commits, cherry-pick its new non-merge commits that are not in upstream `dev`
  (`git rev-list --reverse --no-merges cfa9f6d24..<new head> ^upstream/dev`) and update the head here. If it merges a newer
  upstream `dev`, leave out the parts that rely on `dev` after the current knuvio release and list them here until a release
  contains them. An engine update changes `engine-source.json` and `prebuilt/manifest.json`; its pinned release must exist,
  or the build fails. `full-nntp` may still get commits, but #4679 is the one to follow. When an upstream release contains the
  PR, merging it conflicts in the files above: take upstream's version and delete this entry. If the PR is closed without
  merging, revert. Check with `python native/usenet/scripts/fetch_prebuilts.py`,
  `python native/usenet/scripts/check_prebuilts.py` and
  `:app:testFullDebugUnitTest --tests 'com.nuvio.tv.core.usenet.*' --tests '*Usenet*' --tests '*Newznab*'
  --tests '*NntpProvider*'`.
- **Watch, two source fallbacks:** 1.2.0-beta.1 adds upstream's own fallback to the next matching source
  (`PlayerRuntimeControllerSourceFallback.kt`, from NuvioMedia/NuvioTV#4581, `c3a27b5e2`), next to this PR's
  `StreamFallbackSession`. Both are off by default. With both on, in ExoPlayer's error handling a permanent Usenet
  failure goes to the PR's fallback first and any other error before the first frame to upstream's; the PR, now past
  `c3a27b5e2`, does the same. Since 1.2.0-beta.2, which brings #4624, upstream's auto-play fallback also leaves Usenet
  sources to the PR's own, as in the PR's `dev` merges above.

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

## K-09 Read MKV Cues in one go (upstream PR #4700)

- **Why:** a remux's Cues (seek index) holds 200,000 to 500,000 tiny elements, each fetched with several small reads:
  0.3-1.4 s before playback could start, on a SHIELD and a Strong Leap.
- **What:** [NuvioMedia/NuvioTV#4700](https://github.com/NuvioMedia/NuvioTV/pull/4700) by kernexshadow (head
  `a80fe6c5a`), cherry-picked unchanged: the Matroska extractor peeks the whole Cues element (up to 16 MiB) and walks it
  in memory; Cues it would not handle exactly as the reader does go back to the old element-by-element read.
- **Files:** upstream files edited: `core/player/dvmkv/{DefaultEbmlReader,EbmlProcessor,MatroskaExtractor}.java`,
  `app/src/main/baseline-prof.txt`. New tests `core/player/dvmkv/MatroskaWholeCuesTest.kt` and
  `app/src/test/java/android/util/SparseArray.java`.
- **Commits:** the cherry-pick of `a80fe6c5a`.
- **Remove:** revert that commit.
- **Upstream status:** upstream PR #4700 (open).
- **Watch:** cherry-pick new commits of the PR (`git rev-list --reverse --no-merges a80fe6c5a..<new head> ^upstream/dev`).

## K-10 Prewarm the first playback (upstream PR #4701)

- **Why:** the first playback after the app starts did one-time work before the first frame (codec and HDR caps for the
  Dolby Vision decision, native libraries, the playback HTTP client): 250-550 ms on a Strong Leap, 150 ms on a SHIELD.
- **What:** [NuvioMedia/NuvioTV#4701](https://github.com/NuvioMedia/NuvioTV/pull/4701) by kernexshadow (head
  `0ae8110fa`): that work runs once per process on a background thread when a details or stream screen opens, and the
  fixed 120 ms settle delay before building ExoPlayer is skipped when there is no previous player.
- **Files:** new `ui/screens/player/PlayerStartupPrewarm.kt`. Upstream files edited:
  `ui/screens/player/PlayerRuntimeController{,Initialization}.kt`, `ui/screens/detail/MetaDetailsViewModel.kt`,
  `ui/screens/stream/StreamScreenViewModel.kt`.
- **Commits:** the cherry-pick of `0ae8110fa`. Its conflict in `StreamScreenViewModel.init` with K-07 keeps both: the
  prewarm call first, as in the PR, then K-07's Usenet blocks.
- **Remove:** revert that commit.
- **Upstream status:** upstream PR #4701 (open).
- **Watch:** cherry-pick new commits of the PR (`git rev-list --reverse --no-merges 0ae8110fa..<new head> ^upstream/dev`).

## K-11 AutoSync on Blu-ray clips

- **Why:** K-08 plays Blu-ray clips (`.m2ts`, also from a full disc served by K-07) through its own extractors, which
  skipped the hook K-06 puts on the player's extractors. On a disc the audio fallback never heard the audio, and the
  embedded subtitles give AutoSync no usable reference, so a subtitle was never synced (seen with a full UHD disc release from Usenet, while
  remuxes of the same film synced).
- **What:** `PlayerMediaSourceFactory` takes a wrapper for the Blu-ray extractors, and the player sets it to the audio
  fallback's taps when AutoSync and the audio fallback are on. A playlist of several clips is left unwrapped, because
  each clip's timestamps start again at zero. On a disc the audio fallback now syncs the subtitle (about 20 s on a
  SHIELD with a UHD disc and its TrueHD track). AutoSync's embedded subtitle observer is not added: its live reference
  needs most of the film's subtitles, which only an index gives (Matroska Cues), and a `.m2ts` has none. The player
  reads only 12-15 s ahead, so even a sparse reference (8 lines over 30 s) would come later than the audio, and the
  observer would decode every PGS image on the loading thread.
  AutoSync also stops waiting 12 s for embedded lines on a Blu-ray clip, which never come: the audio fallback starts as
  soon as the subtitle is loaded. On the SHIELD the first lock came after 8.7 s instead of 21 s.
- **Files:** new `ui/screens/player/PlayerRuntimeControllerBdavAutoSync.kt`. Upstream files edited:
  `ui/screens/player/PlayerMediaSourceFactory.kt`, `PlayerRuntimeControllerInitialization.kt` (one line after the
  AutoSync hook). K-06 file edited: `autosync/AutomaticSubtitleSync.kt` (the live reference wait, and an import).
- **Remove:** revert its commits. Remove it together with K-06 or K-08.
- **Watch:** when the PR behind K-06 changes the live reference wait in `AutomaticSubtitleSync.kt`, keep the
  `BdavAutoSyncSources` case.
- **Upstream status:** knuvio only, while K-06 and K-08 are separate open PRs. If both are merged upstream, propose it
  there.

## K-12 Embedded ART profile and compilation status

- **Why:** an update the user installs through Android's installer screen keeps that screen up and offers "Open"
  afterwards, but it carries no dex metadata, so ART only verifies the app at install time and the first launches are
  slow until background dexopt. ART Service (Android 14+, recent ART module) also reads a profile embedded in the APK at
  `assets/art-profile/baseline.prof` when there is no .dm. On a Google TV emulator (API 36), installing through the
  installer screen gave `speed-profile` with the embedded profile and `verify` without it. This tests the same on real
  Android 14 devices.
- **What:** the task that embeds the updater's per-API .dm files also copies the newest-format profile
  (`primary.prof`/`primary.profm` of the open-ended .dm entry) to `assets/art-profile/baseline.prof`/`.profm`, about
  44 KB. Settings → About gets an "App compilation (ART)" row below "Optimize updates during install": compiler filter,
  compilation reason (`install` with `speed-profile` = embedded profile used, `install-dm` = the updater's .dm,
  `verify` = no profile), ART module version and instruction set, read from the first 64 KB of the app's odex.
  Selecting the row reads it again.
- **Files:** new `ui/screens/settings/KnuvioArtCompilationRow.kt`, `res/values/strings_knuvio_art.xml`. Upstream files
  edited: `app/build.gradle.kts` (`EmbedUpdateDexMetadataTask`), `ui/screens/settings/UpdateChannelSettings.kt` (one line).
- **Remove:** revert its commit.
- **Results:** Google TV emulator API 36, ART module 360499999: `speed-profile`, reason `install`. Strong Leap S3 Pro,
  Android 14, ART module 340090000 (no mainline ART update): `verify`, reason `install`, so that ART ignores the embedded
  profile. Support depends on the ART module version, not the Android version.
- **Upstream status:** knuvio only, for now. The embedded profile costs about 44 KB and helps only devices with a recent
  ART module; using the installer screen for manual updates would need a per-device check, not just Android 14+.
