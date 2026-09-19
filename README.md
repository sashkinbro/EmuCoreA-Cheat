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
- `release/` - locally built ZIP bundles and SHA-256 sums for GitHub Releases;
  the Android client installs the individual text packs from first-party release
  asset URLs in the catalog.
- `sources.json` - source attribution and the exact input revision.
- `schemas/cheat-catalog.schema.json` - public catalog contract.
- `scripts/build_libretro_batch.py` - reproducible converter for the licensed
  libretro PSP batch.
- `scripts/validate_catalog.py` - dependency-free offline validator.
- `scripts/validate_libretro_source.py` - verifies the pinned libretro commit,
  license file, and selected PSP source files.
- `scripts/make_game_assets.py` and `scripts/validate_game_assets.py` - create
  and verify per-game release `.pnach` assets plus ZIP packs.

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
in the current manifest or release archives. The active GitHub release line
starts at `v1.0.4`; releases `v1.0.0` through `v1.0.3` were removed because
they contained packs from that link-only source.

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
parseable and makes the exclusion visible in the build report.

## Rebuild and validate

Requires Python 3.10 or newer and no third-party packages:

```bash
python scripts/build_libretro_batch.py --source path/to/libretro-database
python scripts/validate_catalog.py
python scripts/validate_libretro_source.py --source path/to/libretro-database
```

To prepare a release bundle after validation:

```bash
python scripts/make_release.py --version v1.1.0
python scripts/make_game_assets.py --version v1.1.0
python scripts/validate_game_assets.py --version v1.1.0
```

The resulting ZIP is an archival distribution bundle. `cheats.json` continues
to point at the individual HTTPS text packs so the Android client does not
need to unpack an archive.

`build_libretro_batch.py` reads only the pinned local checkout supplied with
`--source`; it will not fetch or execute code from an unpinned branch.

Generated packs are not enabled automatically by EmuCoreA. The user chooses
individual blocks after installing a pack.
