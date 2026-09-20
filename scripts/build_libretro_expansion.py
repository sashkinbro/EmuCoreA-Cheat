#!/usr/bin/env python3
"""Publish the remaining unique licensed libretro PSP packs.

``build_libretro_batch.py`` published the first 798 serials. This script walks
the same pinned libretro-database snapshot and appends every remaining serial
that has usable codes while leaving the published packs untouched:

* serials already present in ``cheats.json`` are never rebuilt or re-added;
* a pack whose cheat content is identical to an already published or already
  planned pack is skipped, so the catalog never repeats the same pack;
* repeated blocks inside one new pack are removed;
* new packs are split over the next stable release tags because GitHub allows
  at most 1000 assets per release.

The plan is derived from the pinned source and the original 798-entry baseline
only, so running the script repeatedly with ``--limit`` appends deterministic
batches instead of shifting earlier release assignments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import build_libretro_batch as blb

ROOT = Path(__file__).resolve().parents[1]
RELEASE_REPO = blb.RELEASE_REPO
SOURCE_PAGE = blb.SOURCE_PAGE
SOURCE_NAME = blb.SOURCE_NAME
LICENSE = blb.LICENSE
AUTHOR = "libretro-database contributors and the original PSP cheat authors"
BASELINE_UPDATED_AT = "2026-09-19T00:00:00Z"
EXPANSION_UPDATED_AT = "2026-09-20T00:00:00Z"


def hash_body(content: str) -> str:
    """Hash a pack without its serial header so regional copies compare equal."""
    body = "\n".join(line for line in content.splitlines() if not line.startswith("# Serial:"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest().upper()


def parse_blocks(content: str) -> tuple[list[str], list[list[str]]]:
    header: list[str] = []
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in content.splitlines():
        if line.startswith("// "):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is None:
            if line.strip():
                header.append(line)
        else:
            current.append(line)
    if current is not None:
        blocks.append(current)
    for block in blocks:
        while block and not block[-1].strip():
            block.pop()
    return header, blocks


def rebuild(header: list[str], blocks: list[list[str]]) -> str:
    output = list(header)
    output.append("")
    for block in blocks:
        output.extend(block)
        output.append("")
    return "\n".join(output).rstrip() + "\n"


def dedupe_blocks(content: str) -> tuple[str, int, int]:
    header, blocks = parse_blocks(content)
    seen: set[tuple[str, ...]] = set()
    kept: list[list[str]] = []
    removed = 0
    for block in blocks:
        key = tuple(line for line in block if not line.startswith("Author = "))
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept.append(block)
    return rebuild(header, kept), len(kept), removed


def load_catalog(repo: Path) -> dict:
    return json.loads((repo / "cheats.json").read_text(encoding="utf-8"))


def baseline_bodies(repo: Path, catalog: dict) -> set[str]:
    bodies: set[str] = set()
    for entry in catalog["entries"]:
        if entry.get("sourceName") != SOURCE_NAME:
            continue
        if entry.get("updatedAt") != BASELINE_UPDATED_AT:
            continue
        text = (repo / entry["packPath"]).read_text(encoding="utf-8")
        bodies.add(hash_body(text))
        bodies.add(hash_body(dedupe_blocks(text)[0]))
    return bodies


def scan_source(source_root: Path) -> tuple[dict[str, Path], list[str]]:
    parsed: dict[str, list[Path]] = {}
    no_serial: list[str] = []
    for path in sorted(source_root.glob("*.cht")):
        match = blb.SERIAL_RE.search(path.name)
        if not match:
            no_serial.append(path.name)
            continue
        parsed.setdefault(match.group(1), []).append(path)
    return {serial: paths[0] for serial, paths in parsed.items()}, no_serial


def build_plan(parsed: dict[str, Path], baseline_serials: set[str], baseline: set[str]):
    plan: list[dict[str, object]] = []
    raw_stats: dict[str, dict[str, object]] = {}
    skipped_zero: list[str] = []
    skipped_duplicate: list[str] = []
    seen = set(baseline)
    for serial in sorted(parsed):
        path = parsed[serial]
        raw, raw_blocks, raw_excluded, raw_malformed = blb.convert(path, serial)
        raw_stats[serial] = {
            "sourceFile": path.name,
            "rawBlocks": raw_blocks,
            "excluded": raw_excluded,
            "malformed": raw_malformed,
            "rawSha256": sha256_text(raw),
        }
        if serial in baseline_serials:
            continue
        content, blocks, removed = dedupe_blocks(raw)
        if blocks < 1:
            skipped_zero.append(serial)
            continue
        digest = hash_body(content)
        if digest in seen:
            skipped_duplicate.append(serial)
            continue
        seen.add(digest)
        plan.append({
            "serial": serial,
            "title": path.name.rsplit(" [", 2)[0],
            "sourceFile": path.name,
            "content": content,
            "blocks": blocks,
            "removedBlocks": removed,
            "excluded": raw_excluded,
            "malformed": raw_malformed,
            "sha256": sha256_text(content),
        })
    return plan, raw_stats, skipped_zero, skipped_duplicate


def description_for(record: dict[str, object]) -> str:
    serial = record["serial"]
    blocks = record["blocks"]
    excluded = record["excluded"]
    removed = record["removedBlocks"]
    if removed:
        return (
            f"{blocks} libretro PSP cheat blocks for {serial}; {excluded} empty or malformed "
            f"and {removed} duplicate upstream blocks excluded."
        )
    return f"{blocks} libretro PSP cheat blocks for {serial}; {excluded} empty or malformed upstream blocks excluded."


def entry_for(record: dict[str, object]) -> dict[str, object]:
    serial = str(record["serial"])
    release = str(record["release"])
    asset = f"PSP-Cheat-Catalog-{release}-{serial}.pnach"
    return {
        "id": f"libretro-psp-{serial.lower()}",
        "title": record["title"],
        "serials": [serial],
        "authors": [AUTHOR],
        "description": description_for(record),
        "downloadUrl": f"{RELEASE_REPO}/{release}/{asset}",
        "packPath": f"files/libretro-psp/{serial}.pnach",
        "sourceUrl": SOURCE_PAGE,
        "sourceName": SOURCE_NAME,
        "license": LICENSE,
        "blockCount": record["blocks"],
        "updatedAt": EXPANSION_UPDATED_AT,
        "sha256": record["sha256"],
    }


def release_of(entry: dict[str, object]) -> str | None:
    marker = "/releases/download/"
    url = str(entry.get("downloadUrl", ""))
    if marker not in url:
        return None
    return url.split(marker, 1)[1].split("/", 1)[0]


def write_asset_index(assets_root: Path, catalog: dict, version: str) -> int:
    packs: list[dict[str, object]] = []
    for entry in sorted(catalog["entries"], key=lambda item: item["serials"][0]):
        if release_of(entry) != version:
            continue
        serial = entry["serials"][0]
        asset = f"PSP-Cheat-Catalog-{version}-{serial}.pnach"
        path = assets_root / version / asset
        packs.append({
            "serial": serial,
            "catalogId": entry["id"],
            "pnachAsset": asset,
            "pnachUrl": f"{RELEASE_REPO}/{version}/{asset}",
            "pnachSha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
            "pnachBytes": path.stat().st_size,
        })
    index = assets_root / version / "pack-assets.json"
    index.write_text(json.dumps({"version": version, "packs": packs}, indent=2) + "\n", encoding="utf-8", newline="\n")
    return len(packs)


def write_build_report(repo: Path, catalog: dict, raw_stats: dict, batch_id: str, skipped: dict[str, list[str]]) -> None:
    entries = []
    for entry in sorted(catalog["entries"], key=lambda item: item["serials"][0]):
        if entry.get("sourceName") != SOURCE_NAME:
            continue
        serial = entry["serials"][0]
        stats = raw_stats.get(serial, {})
        entries.append({
            "serial": serial,
            "sourceFile": stats.get("sourceFile", entry.get("packPath", "")),
            "blocks": entry["blockCount"],
            "excluded": stats.get("excluded", 0),
            "malformed": stats.get("malformed", 0),
            "sha256": entry["sha256"],
        })
    report = {
        "batch": batch_id,
        "release": "cheat-catalog",
        "libretroSource": f"https://raw.githubusercontent.com/libretro/libretro-database/{blb.SOURCE_COMMIT}/cht/Sony%20-%20PlayStation%20Portable",
        "libretroCommit": blb.SOURCE_COMMIT,
        "libretroEntries": entries,
        "skipped": skipped,
    }
    (repo / "build-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).parents[2] / "libretro-database")
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--limit", type=int, default=0, help="append at most this many pending packs; 0 is a dry run")
    parser.add_argument("--batch-id", default="batch-020")
    parser.add_argument("--first-release", default="cheat-catalog-2")
    parser.add_argument("--second-release", default="cheat-catalog-3")
    parser.add_argument("--assets-per-release", type=int, default=1000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    source_root = args.source.resolve() / "cht" / "Sony - PlayStation Portable"
    catalog = load_catalog(repo)
    baseline_serials = {
        entry["serials"][0]
        for entry in catalog["entries"]
        if entry.get("sourceName") == SOURCE_NAME and entry.get("updatedAt") == BASELINE_UPDATED_AT
    }
    known_serials = {entry["serials"][0] for entry in catalog["entries"]}
    baseline = baseline_bodies(repo, catalog)
    parsed, no_serial = scan_source(source_root)
    plan, raw_stats, skipped_zero, skipped_duplicate = build_plan(parsed, baseline_serials, baseline)
    for index, record in enumerate(plan):
        record["release"] = args.first_release if index < args.assets_per_release else args.second_release

    pending = [record for record in plan if record["serial"] not in known_serials]
    print(f"baseline serials: {len(baseline_serials)}; catalog serials: {len(known_serials)}")
    print(f"planned unique new packs: {len(plan)}; pending: {len(pending)}")
    print(f"skipped duplicate packs: {len(skipped_duplicate)}; zero-block packs: {len(skipped_zero)}; files without serial: {len(no_serial)}")
    print(f"new codes in pending: {sum(int(record['blocks']) for record in pending)}")
    for release in (args.first_release, args.second_release):
        print(f"pending for {release}: {sum(1 for record in pending if record['release'] == release)}")
    if args.dry_run or args.limit <= 0:
        return 0

    to_add = pending[: args.limit]
    output_root = repo / "files" / "libretro-psp"
    assets_root = repo / "release" / "game-assets"
    output_root.mkdir(parents=True, exist_ok=True)
    new_entries = []
    for record in to_add:
        serial = str(record["serial"])
        release = str(record["release"])
        content = str(record["content"])
        (output_root / f"{serial}.pnach").write_text(content, encoding="utf-8", newline="\n")
        asset_dir = assets_root / release
        asset_dir.mkdir(parents=True, exist_ok=True)
        asset = asset_dir / f"PSP-Cheat-Catalog-{release}-{serial}.pnach"
        asset.write_bytes(content.encode("utf-8"))
        new_entries.append(entry_for(record))

    catalog["entries"].extend(new_entries)
    catalog["entries"].sort(key=lambda entry: entry["serials"][0])
    catalog["generatedAt"] = EXPANSION_UPDATED_AT
    (repo / "cheats.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    for release in sorted({str(record["release"]) for record in to_add}):
        count = write_asset_index(assets_root, catalog, release)
        print(f"{release}: {count} indexed release assets")
    skipped = {
        "duplicatePacks": skipped_duplicate,
        "zeroBlockPacks": skipped_zero,
        "filesWithoutSerial": no_serial,
    }
    write_build_report(repo, catalog, raw_stats, args.batch_id, skipped)
    print(f"added {len(to_add)} packs; catalog now {len(catalog['entries'])} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
