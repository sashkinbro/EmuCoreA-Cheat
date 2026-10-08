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
- `files/author-psp/` - additional exact-serial patches from pinned,
  explicitly licensed author repositories. Each downloadable pack embeds
  its complete upstream license; original copies are in `LICENSES/`.
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
allows at most 1000 assets per release, the catalog is served from five stable
release tags: `cheat-catalog` (first 798 packs), `cheat-catalog-2` (next 1000)
and `cheat-catalog-3` (final 715 libretro packs plus the custom camera pack
only), with the eleven additional author packs on `cheat-catalog-4` and two
final additional packs on `cheat-catalog-5`.
Every catalog entry keeps a direct HTTPS `.pnach` URL on the release that holds
its asset.

The catalog also publishes author-provided packs through `files/custom-psp/`.
`custom-psp-ules-00277` is a Tenchu camera patch for `ULES-00277`, a serial that
already has a libretro gameplay pack, so a serial may appear in more than one
entry; the Android client lists every matching pack for the selected game and
the entries must never repeat the same pack bytes.

On 2026-10-08, eleven author packs containing 32 unique blocks were added,
bringing the catalog to 2525 packs, 2516 unique serials, and 75,852 blocks.
Three of the additions cover previously absent serials. They are additional
editions of games represented in other regions, with distinct code content:

| Exact serial | Game edition | Optional patch blocks |
| --- | --- | --- |
| `ULKS-46086` | Naruto: Ultimate Ninja Heroes 2 [KR] | Five aerial-dogfight and CPU substitution disable/restore options |
| `ULJM-05904` | Midnight Club: L.A. Remix (Rockstar Classics) [JP] | Unlock prototype-only in-game cheat passwords |
| `NPUG-80329` | Daxter (PlayStation Store) [US] | Fix analog controls |

The other eight packs add new features for existing serials: four regional
Naruto packs (`ULES-00865`, `ULUS-10299`, `ULES-01088`, `ULUS-10349`), one
shared US/EU Battlefront II ticket-rebalance pack (`ULUS-10053`, `ULES-00183`),
one shared US/EU Midnight Club prototype-cheat pack (`ULUS-10383`, `ULES-01144`),
and separate US/EU Tag Force Japanese-voice packs (`ULUS-10136`, `ULES-00600`).
Each shared-region pack is published once with both verified serials; its
code sequences match both pinned source files. Existing catalog entries and
packs are unchanged.

The final partial batch on 2026-10-08 adds two packs with 13 new blocks for
existing games, bringing the catalog to 2527 packs, 2516 unique serials, and
75,865 blocks. LocoRoco Midnight Carnival (`NPEG-00024`) gains 11 acceleration,
screen-rotation, and jump-height options from an alternate pinned libretro file.
Choose one acceleration value and one jump value at a time. Its version-ambiguous
demo-limit patch is excluded. GTA: Chinatown Wars (`ULUS-10490`) gains two
guarded object-cell radius settings from TAbdiukov: minimum and default. Choose
one setting and immediately restart the game after changing it; the higher
radius is excluded because the author says it exceeds PSP-1000 memory limits.
Both packs retain their complete source license. Runtime was not tested locally.

The final source sweep found no additional entirely new game title with both
clear redistribution terms and verified code/build applicability. In particular,
the Syphon Filter demo's author uses a homebrew-style hash identifier, so a title
match to an official demo serial was insufficient to publish that candidate.
The audit also confirmed an existing conversion-fidelity issue: the legacy
converter drops a required zero operand from `All Items Rare-1` in
`NPJB-40001`. It is recorded in `build-report.json`; existing packs and scripts
are unchanged under the add-only scope. New additions preserve complete ordered
code sequences, including zero operands and repeated lines where required.

Naruto and Daxter come from
[TAbdiukov/PPSSPP-patches](https://github.com/TAbdiukov/PPSSPP-patches/tree/a38b2aba3e0e24935392d2617b14b35d73ab0f27)
under Apache-2.0; the Daxter source credits `theboy181` in its filename.
Midnight Club comes from
[CookiePLMonster/Console-Cheat-Codes](https://github.com/CookiePLMonster/Console-Cheat-Codes/tree/f55aa8db8e6c79a2af6a9dd216b46635fc7324b5)
under MIT, credited to Adrian Zdanowicz (Silent). For Midnight Club, apply
the patch and enter the prototype passwords through the game's cheat menu;
the [author's research](https://silentsblog.com/2023/12/27/midnight-club-la-remix-cheat-codes/)
lists the passwords and explains the serial check.

The Tag Force voice-only patches come from
[DeaTh-G/tagforce-essentials](https://github.com/DeaTh-G/tagforce-essentials/tree/0e47a5f37a268e4a516893ac5f69588b0c424acd)
under MIT. Matheus Abreu's original voice-enabler research remains credited.
These blocks enable audio already in the game and require no extracted mod
files. Reload the shop if enabling the patch there; upstream reports that
cheat-engine timing can miss title-screen voices. Visual/card mods requiring
external assets are excluded.

All 32 new blocks were compared by numeric address/value sequences against
every existing block and each other, ignoring titles, attribution, and
comments. No repeated code block or duplicate pack was introduced. Dummy menu
separators and experimental Naruto human-substitution patches were excluded;
source hashes, exclusions, and conversion details are in `build-report.json`.
Existing packs remain unchanged, including legacy baseline duplicates reported
by `check_duplicates.py`. The pinned libretro PSP subtree was also compared
with upstream commit `fbeefcb46c2e1b20a7e2945f34a694a41b2d6f90` and had no changes.

These checks validate provenance, format, and uniqueness; the new patches
have not been tested locally in the games. For Naruto, enable only one
aerial-dogfight option at a time, and do not enable a CPU substitution disable
option together with its restore option. The app and catalog schema are
unchanged; all new entries retain direct `.pnach` release URLs.
The new release also includes an aggregate archive of the complete catalog;
previous releases and their assets are preserved.

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
python scripts/make_release.py --version cheat-catalog-4
python scripts/make_game_assets.py --version cheat-catalog-4 --pnach-only
python scripts/validate_game_assets.py --version cheat-catalog
python scripts/validate_game_assets.py --version cheat-catalog-2
python scripts/validate_game_assets.py --version cheat-catalog-3
python scripts/validate_game_assets.py --version cheat-catalog-4
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
