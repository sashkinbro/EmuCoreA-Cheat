# EmuCoreA PSP Cheat Catalog

Curated PSP cheat packs for games running in PPSSPP. The catalog is consumed
by EmuCoreA from:

`https://raw.githubusercontent.com/sashkinbro/EmuCoreA-Cheat/main/cheats.json`

Each entry is a serial-specific text pack. The pack contains the raw
address/value pairs that EmuCoreA can import and convert to its active cheat
format. Codes are kept separate by game serial and region; do not install a
pack for a different revision just because the title matches.

## Contents

- `cheats.json` - schema version 1 catalog used by EmuCoreA.
- `files/libretro-psp/` - packs converted from the pinned PSP subset of
  libretro-database under its repository CC-BY-SA-4.0 license.
- `files/custom-psp/` - author-provided PSP packs that are not derived from
  libretro-database; each one records its own author and source in
  `cheats.json` and `sources.json`.
- `release/` - local, git-ignored build directory for per-release `.pnach`
  assets and aggregate ZIPs. The published files live on GitHub Releases and
  the Android client installs the individual `.pnach` packs from their release
  asset URLs; the generated copies are never committed. The asset names use the
  neutral `PSP-Cheat-Catalog` prefix; they do not claim authorship of the
  underlying cheat data.
- `sources.json` - source attribution and the exact input revision.
- `schemas/cheat-catalog.schema.json` - public catalog contract.
- `scripts/build_libretro_batch.py` - reproducible converter for the first 798
  licensed libretro PSP packs.
- `scripts/build_libretro_expansion.py` - appends every remaining unique serial
  from the same pinned snapshot, skipping duplicate packs and repeated blocks.
- `scripts/check_duplicates.py` - verifies the catalog has no repeated id,
  serial, or pack content and that new packs never repeat a published pack.
- `scripts/validate_catalog.py` - dependency-free offline validator.
- `scripts/validate_libretro_source.py` - verifies the pinned libretro commit,
  license file, and selected PSP source files.
- `scripts/make_game_assets.py` and `scripts/validate_game_assets.py` - create
  and verify per-release `.pnach` assets, with optional local ZIP packs.
- `.gitattributes` - keeps `*.pnach` packs on LF so catalog SHA-256 hashes stay
  byte-stable after checkout on Windows.
- `.gitignore` - excludes the generated `release/` build output and Python
  bytecode caches from the repository.

## Source and attribution

The current packs are generated from the pinned PSP subset of
[libretro-database](https://github.com/libretro/libretro-database) at commit
`740ebdf03247073658ccea45ddedfd57ea9d2974`. The repository ships an explicit
CC-BY-SA-4.0 license and its README describes the `.cht` cheat collection.
Original author attribution is retained; the catalog does not claim a new
license over individual code authors' rights.

The former CWCheat Database Plus source is retained in `sources.json` as
link-only provenance because its cheat data has no explicit redistribution
license in the pinned upstream repository. No CWCheat-derived pack is present
in the current manifest or release archives.

The whole PSP subset of the pinned revision is now imported: 2654 upstream
files resolve to 2611 unique serials, of which 2513 serials are published as
per-game packs with 75,691 cheat blocks. Two serials had no parseable blocks
and 96 serials repeated the exact cheat content of another serial (regional
variants); those are skipped so no pack is published twice. Because GitHub
allows at most 1000 assets per release, the catalog is served from three stable
release tags: `cheat-catalog` (first 798 packs), `cheat-catalog-2` (next 1000)
and `cheat-catalog-3` (final 715 libretro packs plus the custom camera pack).
Every catalog entry keeps a direct HTTPS `.pnach` URL on the release that holds
its asset.

The catalog also publishes author-provided packs through `files/custom-psp/`.
`custom-psp-ules-00277` is a Tenchu camera patch for `ULES-00277`, a serial that
already has a libretro gameplay pack, so a serial may appear in more than one
entry; the Android client lists every matching pack for the selected game and
the entries must never repeat the same pack bytes.

## Pack format

Packs are UTF-8 text files with blocks in the format understood by EmuCoreA:

```text
// Infinite health
Author = libretro-database contributors / original PSP cheat authors
20000000 00000001
```

The generated files intentionally omit CWCheat's `_L` and `0x` decoration and
keep only address/value pairs with an eight-hex-digit address and a value of
one to eight hex digits. Blocks containing malformed upstream lines are
excluded rather than silently repaired. This keeps every published block
parseable and makes the exclusion visible in the build report. Author-provided
CWCheat sources are converted the same way: `_C1`/`_C0` headers become
`// <title>` block comments and `_L 0xADDR 0xVALUE` lines become `ADDR VALUE`
pairs, while their explanatory comments are preserved.

## Rebuild and validate

Requires Python 3.10 or newer and no third-party packages:

```bash
python scripts/build_libretro_batch.py --source path/to/libretro-database
python scripts/validate_catalog.py
python scripts/validate_libretro_source.py --source path/to/libretro-database
```

`build_libretro_expansion.py` is idempotent: without `--limit` it only prints
the deterministic plan, and each run appends the next pending packs without
touching published entries. Verify duplicate-free state after every change:

```bash
python scripts/build_libretro_expansion.py --source path/to/libretro-database --dry-run
python scripts/build_libretro_expansion.py --source path/to/libretro-database --limit 1000 --batch-id batch-020
python scripts/check_duplicates.py
```

To prepare a release bundle after validation (writes to the git-ignored
`release/` directory, then upload the files to the matching GitHub release):

```bash
python scripts/make_release.py --version cheat-catalog-3
python scripts/make_game_assets.py --version cheat-catalog-3
python scripts/validate_game_assets.py --version cheat-catalog
python scripts/validate_game_assets.py --version cheat-catalog-2
python scripts/validate_game_assets.py --version cheat-catalog-3
```

The Android client reads `cheats.json` and downloads each entry's
`downloadUrl`; it does not read `pack-assets.json` or unpack per-game ZIPs. The
1,000-asset limit applies per release, so once the first release was full the
expansion continued on `cheat-catalog-2` and `cheat-catalog-3`. Keeping the
direct `.pnach` URLs stable keeps the app working without client changes; the
aggregate ZIP on the newest release remains an archival download.

A future schema may add optional shard fields (`shardUrl`, `shardSha256`, and
`entryPath`) so several packs can share one asset, but until the Android client
supports them every entry must retain a direct HTTPS `.pnach` `downloadUrl`;
shard metadata alone would be ignored by the current app.

`build_libretro_batch.py` and `build_libretro_expansion.py` read only the
pinned local checkout supplied with `--source`; they will not fetch or execute
code from an unpinned branch.

`build_libretro_batch.py` reads only the pinned local checkout supplied with
`--source`; it will not fetch or execute code from an unpinned branch.

Generated packs are not enabled automatically by EmuCoreA. The user chooses
individual blocks after installing a pack.
