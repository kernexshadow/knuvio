# knuvio changes

Everything knuvio adds on top of [NuvioMedia/NuvioTV](https://github.com/NuvioMedia/NuvioTV). Each entry says why the change
exists, which files it touches, and how to remove it. Read this first when an upstream merge conflicts.

Files under `app/src/full/res`, `app/src/fullDebug/res`, `knuvio-branding/` and the knuvio workflow are knuvio-only and cannot
conflict. **Upstream files that knuvio edits** are the ones to watch:

| Upstream file | Changed by |
|---|---|
| `app/build.gradle.kts` | [K-02](#k-02-application-ids-and-updater-source), [K-12](#k-12-embedded-art-profile-and-compilation-status) |
| `app/src/main/java/com/nuvio/tv/updater/VersionUtils.kt` | [K-05](#k-05-knuvio-revisions-in-the-updater) |
| `core/player/dvmkv/{DefaultEbmlReader,EbmlProcessor,MatroskaExtractor}.java`, `baseline-prof.txt` | [K-09](#k-09-read-mkv-cues-in-one-go-upstream-pr-4700) |
| `PlayerRuntimeController{,Initialization}.kt`, `MetaDetailsViewModel.kt`, `StreamScreenViewModel.kt` | [K-10](#k-10-prewarm-the-first-playback-upstream-pr-4701) |
| `ui/screens/settings/UpdateChannelSettings.kt` (one line) | [K-12](#k-12-embedded-art-profile-and-compilation-status) |
| Usenet result, stream ranking and formatter files listed in K-13 and K-14 | [K-13](#k-13-usenet-result-details-upstream-pr-4821), [K-14](#k-14-template-formatting-for-usenet-results-upstream-pr-4823) |
| Player chapter files listed in K-15 | [K-15](#k-15-keep-chapters-with-play-next-episode-upstream-pr-4824) |

Upstream status: **knuvio only** = not meant for upstream; **upstream PR #N** = proposed; **in upstream since X** = the change
can be dropped from knuvio after merging X.

Dropped because upstream now has them: K-07 built-in Usenet streaming (#4679), K-08 Blu-ray clips and discs in ExoPlayer
(#696) and K-11 AutoSync on Blu-ray clips (#4756), all in upstream since 1.2.0-beta.4. K-06 was never used.

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
  prewarm call first, as in the PR, then the Usenet blocks (in upstream since 1.2.0-beta.4). The 1.2.0-beta.3 merge's conflict in
  `MetaDetailsViewModel.init` also keeps both: the prewarm call first, then upstream's `applyTrailerHandoff()`.
- **Remove:** revert that commit.
- **Upstream status:** upstream PR #4701 (open).
- **Watch:** cherry-pick new commits of the PR (`git rev-list --reverse --no-merges 0ae8110fa..<new head> ^upstream/dev`).

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

## K-13 Usenet result details (upstream PR #4821)

- **Why:** a built-in Usenet result was named `4K • Usenet • <indexer>`, without the detail addon formatters give their
  results.
- **What:** [NuvioMedia/NuvioTV#4821](https://github.com/NuvioMedia/NuvioTV/pull/4821) by kernexshadow (head
  `27cc9a13c`), cherry-picked unchanged onto 1.2.0-beta.4: the name describes the video (resolution, service, quality,
  DV/HDR, codec, quality tier) and the details add the main audio track, up to two languages and the bitrate. With size
  badges on, a single video's size is left to its badge.
- **Files:** upstream files edited: `core/streams/StreamRanking.kt`, `core/usenet/{BuiltInUsenetService,NewznabProtocol,
  UsenetReleaseLabels}.kt`, `res/values{,-vi}/usenet_sources.xml`, and their tests.
- **Commits:** the cherry-picks of `655bccb78`, `65d80756e`, `27cc9a13c`.
- **Remove:** revert those commits (after K-14, which builds on them).
- **Upstream status:** upstream PR #4821 (open).
- **Watch:** cherry-pick new commits of the PR (`git rev-list --reverse --no-merges 27cc9a13c..<new head> ^upstream/dev`).

## K-14 Template formatting for Usenet results (upstream PR #4823)

- **Why:** let built-in Usenet results use the same name and description templates as Debrid results, and see a
  template's result while typing it.
- **What:** [NuvioMedia/NuvioTV#4823](https://github.com/NuvioMedia/NuvioTV/pull/4823) by kernexshadow (head
  `952754769`), stacked on #4821, cherry-picked unchanged: built-in Usenet results can optionally be formatted with the
  Debrid templates, and the formatter page previews templates as they are typed, with a detailed preset.
- **Files:** new `core/usenet/{StreamFormatterPreview,UsenetResultValues}.kt` and tests. Upstream files edited:
  `BUILT_IN_USENET.md`, `core/debrid/DebridStreamFormatter{,Defaults}.kt`, `core/server/DebridFormatter{ConfigServer,
  WebPage}.kt`, `core/usenet/{BuiltInUsenetService,UsenetSources}.kt`, `data/repository/StreamRepositoryImpl.kt`,
  `ui/screens/settings/{DebridSettingsScreen,DebridSettingsViewModel,UsenetSourcesCard}.kt`, `res/values/strings.xml`.
- **Commits:** the cherry-picks of `7b6202f35`, `952754769` (the PR's first three commits are K-13).
- **Remove:** revert those two commits.
- **Upstream status:** upstream PR #4823 (open).
- **Watch:** cherry-pick new commits of the PR (`git rev-list --reverse --no-merges 952754769..<new head> ^upstream/dev`);
  commits that come from #4821 belong to K-13.

## K-15 Keep chapters with Play Next Episode (upstream PR #4824)

- **Why:** when binging with Play Next Episode, chapters (the list and chapter-based skip intro) stopped showing after one
  or two episodes.
- **What:** [NuvioMedia/NuvioTV#4824](https://github.com/NuvioMedia/NuvioTV/pull/4824) by kernexshadow (head
  `3feea816d`), cherry-picked unchanged: mpv re-reads chapters on `chapter-list` changes once the new file is loaded;
  ExoPlayer's Matroska chapter probe retries transient failures; the HTTP episode switch resets the playback timeline.
- **Files:** upstream files edited: `ui/screens/player/{MatroskaChapterLoader,NuvioMpvSurfaceView}.kt` and the
  `PlayerRuntimeController*.kt` files (base, Chapters, Lifecycle, Mpv, MpvEvents, Observers, PlaybackEvents, Streams), and
  their tests.
- **Commits:** the cherry-pick of `3feea816d`.
- **Remove:** revert that commit.
- **Upstream status:** upstream PR #4824 (open).
- **Watch:** cherry-pick new commits of the PR (`git rev-list --reverse --no-merges 3feea816d..<new head> ^upstream/dev`).
