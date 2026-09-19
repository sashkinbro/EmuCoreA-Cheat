# Contributing PSP cheats

Only PPSSPP/PSP CWCheat material belongs in this repository. PlayStation 1
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
no clear license, keep the pack provenance and attribution explicit and obtain
permission before adding material outside the already curated source.

Run all checks before a pull request:

```bash
python scripts/build_catalog.py --source path/to/cheat.db
python scripts/validate_catalog.py
python scripts/validate_source.py --source path/to/cheat.db
```

The catalog is an input to the app and is not a guarantee that a code works
with every game revision. Test codes against the exact serial and PPSSPP
version before recommending them as enabled by default.
