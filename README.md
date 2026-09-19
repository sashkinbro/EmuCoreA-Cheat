# EmuCoreA PSP Cheat Catalog

Curated CWCheat packs for PSP games running in PPSSPP. The catalog is consumed
by EmuCoreA from:

`https://raw.githubusercontent.com/sashkinbro/EmuCoreA-Cheat/main/cheats.json`

Each entry is a serial-specific text pack. The pack contains the raw
address/value pairs that EmuCoreA can import and convert to its active cheat
format. Codes are kept separate by game serial and region; do not install a
pack for a different revision just because the title matches.

## Contents

- `cheats.json` - schema version 1 catalog used by EmuCoreA.
- `files/cwcheat-db-plus/` - generated per-game packs derived from the pinned
  CWCheat Database Plus snapshot.
- `files/libretro-psp/` - packs converted from the pinned PSP subset of
  libretro-database under its repository CC-BY-SA-4.0 license.
- `release/` - locally built ZIP bundles and SHA-256 sums for GitHub Releases;
  the Android client installs the individual text packs from their catalog URLs.
- `sources.json` - source attribution and the exact input revision.
- `schemas/cheat-catalog.schema.json` - public catalog contract.
- `scripts/build_catalog.py` - reproducible extractor and pack generator.
- `scripts/build_libretro_batch.py` - reproducible converter for the licensed
  libretro PSP batch.
- `scripts/validate_catalog.py` - dependency-free offline validator.
- `scripts/validate_source.py` - checks the pinned upstream input and output
  hashes when network access is available.
- `scripts/validate_libretro_source.py` - verifies the pinned libretro commit,
  license file, and selected PSP source files.

## Source and attribution

The current packs are generated from
[Saramagrean/CWCheat-Database-Plus-](https://github.com/Saramagrean/CWCheat-Database-Plus-)
at commit `750261bccdc39569dec5eaee380902ac1442a007` (the source snapshot is
also recorded in `sources.json`). The upstream README credits the PPSSPP
forum, GameHacking, LunaMoo, TAbdiukov and the forum patch collections. The
individual cheat authors remain credited by the upstream collection.

The upstream repository does not publish a blanket open-source license for
the cheat data. This catalog therefore preserves source attribution and the
pinned provenance for every generated pack; it does not relicense the cheat
codes. Check the upstream terms before redistributing a new source or adding
third-party material. The Python tooling is intended to be reusable, while
the data remains subject to its original authors' terms.

The libretro PSP batch is kept separate because libretro-database ships an
explicit CC-BY-SA-4.0 repository license and attribution requirements. Its
README also states that cheat files are collected from web sources and user
contributions, so original author attribution is retained and the catalog does
not claim a new license over individual code authors' rights.

## Pack format

Packs are UTF-8 text files with blocks in the format understood by EmuCoreA:

```text
// Infinite health
Author = Saramagrean / original CWCheat authors
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
python scripts/build_catalog.py --source path/to/cheat.db
python scripts/validate_catalog.py
python scripts/validate_source.py --source path/to/cheat.db
python scripts/build_libretro_batch.py --source path/to/libretro-database
python scripts/validate_libretro_source.py --source path/to/libretro-database
```

To prepare a release bundle after validation:

```bash
python scripts/make_release.py --version v1.0.0
```

The resulting ZIP is an archival distribution bundle. `cheats.json` continues
to point at the individual HTTPS text packs so the Android client does not
need to unpack an archive.

`build_catalog.py` defaults to `../CWCheat-Database-Plus/cheat.db` when run
from the repository's parent directory. It writes deterministic JSON and
pack files. The build script will not fetch or execute code from an unpinned
branch.

Generated packs are not enabled automatically by EmuCoreA. The user chooses
individual blocks after installing a pack.
