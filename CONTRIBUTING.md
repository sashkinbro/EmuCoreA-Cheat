# Contributing PSP cheats

Only PPSSPP/PSP cheat material belongs in this repository. PlayStation 1
GameShark files and PNACH patches for other cores do not belong here.

Every catalog entry must:

1. identify one or more exact PSP serials (`ULUS-12345`, `ULES-12345`,
   `NPJH-12345`, and similar);
2. retain a stable HTTPS source URL and a 40-character source commit where
   possible;
3. include non-empty author attribution and a useful description;
4. point at a UTF-8 text file whose active lines are parseable address/value
   pairs and whose block count matches the catalog;
5. avoid duplicate packs that only rename an existing entry; and
6. record exclusions or conversions in the build report when upstream data is
   malformed or uses a code type the importer cannot represent.

Do not copy data from a source that forbids redistribution. If the source has
no clear license, keep it link-only in `sources.json` and do not add its pack
to the manifest or release archive. The active libretro batch requires the
pinned repository revision and its CC-BY-SA-4.0 license to be retained.

Run all checks before a pull request:

```bash
python scripts/build_libretro_batch.py --source path/to/libretro-database
python scripts/validate_catalog.py
python scripts/validate_libretro_source.py --source path/to/libretro-database
```

The catalog is an input to the app and is not a guarantee that a code works
with every game revision. Test codes against the exact serial and PPSSPP
version before recommending them as enabled by default.
