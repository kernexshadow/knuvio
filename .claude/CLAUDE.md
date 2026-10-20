# knuvio

knuvio is a personal build of [NuvioMedia/NuvioTV](https://github.com/NuvioMedia/NuvioTV), the Android TV app, published at
[kernexshadow/knuvio](https://github.com/kernexshadow/knuvio). It follows upstream releases automatically. It differs from
upstream only in branding, application IDs, the in-app updater source, and an extra revision number for its own builds.
Everything knuvio adds is listed in [KNUVIO_CHANGES.md](../KNUVIO_CHANGES.md).

NuvioTV is GPLv3, so the repository stays public: every published APK must have its source available.

## Repositories and branches

| Remote | Repository | Role |
|---|---|---|
| `origin` | `kernexshadow/knuvio` | This repo. `main` is the only branch and the release branch. |
| `upstream` | `NuvioMedia/NuvioTV` | Source of truth. Releases are tags on its `dev` branch. |

- `main` = an upstream **release tag** + the knuvio commits on top. Only release tags are merged, never upstream `dev` HEAD,
  so every knuvio release matches an exact upstream version.
- Contributions to Nuvio itself are made from the separate NuvioTV checkout and the `kernexshadow/NuvioTV` fork, on branches
  created from `upstream/dev`. Never open PRs from this repo, and never let knuvio commits reach an upstream PR branch.
- A knuvio feature that should also go upstream: develop it in NuvioTV, open the upstream PR there, then merge or cherry-pick
  it into knuvio `main` and record it in KNUVIO_CHANGES.md with the PR number.

## Versions and releases

| Build | Release tag | APK `versionName` | GitHub release |
|---|---|---|---|
| Automatic, upstream `1.1.0-beta.8` | `1.1.0-beta.8+k` | `1.1.0-beta.8+k` | prerelease if upstream's is |
| Manual, revision 1 of that version | `1.1.0-beta.8+k.1` | `1.1.0-beta.8+k.1` | same |
| Upstream stable `1.1.0` | `1.1.0+k`, then `+k.1`, `+k.2` | same as tag | latest |

- `+k` is semver build metadata. The knuvio updater (`app/src/main/java/com/nuvio/tv/updater/VersionUtils.kt`) reads `+k.N`
  as a tie-breaker between builds of the same upstream version, so the order is
  `1.1.0-beta.7+k < 1.1.0-beta.7+k.1 < 1.1.0-beta.8+k < 1.1.0+k < 1.1.0+k.1`. Any other build metadata is still ignored, as upstream.
- `versionName` in the repo stays upstream's value. The workflow stamps the full release tag into it at build time and never
  commits it, because the updater compares the installed `versionName` with release tags.
- `versionCode` stays upstream's value. Revisions reuse it, which Android allows for updates.

## Sync and release workflow

`.github/workflows/knuvio-sync-release.yml`:

- **Automatic**, every 6 hours (cron `17 */6 * * *`, UTC): finds the newest non-draft upstream release, prereleases included.
  If `<tag>+k` already exists it does nothing. Otherwise it merges the upstream tag into `main`, pushes, builds, and publishes.
- **Manual**: Actions → "Sync upstream and release" → Run workflow, or
  `gh workflow run knuvio-sync-release.yml -R kernexshadow/knuvio -f manual=true`. It builds the current `main` as the next
  `+k.N` for the upstream version in `app/build.gradle.kts`, and the release notes list commits since the previous knuvio release.
  `-f tag=<upstream tag>` (without `manual`) builds a specific upstream release.
- Merge conflicts: the job fails with an error annotation and GitHub emails the owner. Resolve locally (see below).
- It disables every other workflow in the repo. Inherited upstream workflows must not run here.
- It runs the updater unit tests, then `:app:assembleFullRelease` (about 15–20 minutes), and uploads the five APKs
  (arm64-v8a, armeabi-v7a, x86, x86_64, universal).
- Every `gh` call passes `-R`/an explicit repo: with an `upstream` remote present, `gh` defaults to NuvioMedia.
- To rebuild a version that already has a release, delete that release and its tag first, then run the workflow again.

Secrets used are referenced by name in the workflow. `SYNC_PAT` (fine-grained, this repo only, Contents + Workflows
read/write) does the checkout and push, because `GITHUB_TOKEN` cannot push upstream changes to `.github/workflows`.

## Resolving an upstream merge conflict

```bash
git fetch upstream --tags
git merge <upstream-tag>           # e.g. 1.1.0-beta.8
# resolve: KNUVIO_CHANGES.md says why each knuvio change exists and which files it touches
git push origin main
gh workflow run knuvio-sync-release.yml -R kernexshadow/knuvio   # publishes <tag>+k
```

## Rules for knuvio changes

1. **Prefer overlays to edits.** Resources go in `app/src/full/res` (flavor source set, overrides `main`) or
   `app/src/fullDebug/res`. They never conflict with upstream. Edit upstream files only when there is no other way, and keep the
   diff minimal.
2. **Record every change** in KNUVIO_CHANGES.md in the same commit: what, why, files, how to remove, upstream status.
3. Commit messages start with `knuvio:`. Code, comments and docs are in English.
4. When upstream adds a locale whose `strings.xml` defines `app_name`, add a matching
   `app/src/full/res/values-<qualifier>/strings_knuvio.xml`, or that locale shows "Nuvio". (`values-hu` uses `string.xml`.)
5. When upstream adds or renames a theme or launcher icon option, regenerate the branding (below).

## Branding assets

`knuvio-branding/` holds the source artwork and the scripts that generate every knuvio image (Python 3 with Pillow, NumPy, SciPy):

```bash
python knuvio-branding/make_icons.py knuvio-branding/source/k-mark.png knuvio-branding/source/k-banner.png app/src/full/res
python knuvio-branding/make_variants.py knuvio-branding/source/k-mark.png knuvio-branding/source/k-banner.png \
    app/src/main/res app/src/full/res <preview-dir>
```

- `make_icons.py`: default launcher icon, splash mark (`app_logo_mark`), TV banner.
- `make_variants.py`: in-app wordmarks (`app_logo_wordmark*`, transparent; the "nuvio" text is taken from upstream's wordmark,
  which uses the same typeface) and the themed launcher icons and banners. Theme colours come from upstream's themed assets.
  It writes preview images to `<preview-dir>`; check them before committing.

## Local builds

- Same toolchain as NuvioTV. Needs `local.properties` and `local.dev.properties` in the repo root (gitignored).
- Debug builds are signed with the release config, so `local.properties` must have `NUVIO_RELEASE_*` entries (pointing at the
  Android debug keystore is fine).
- Debug app ID `com.knuviodebug.com`, label "knuvio Debug". Release app ID `com.knuvio.tv`, label "knuvio". Both install next
  to the official Nuvio apps.
