#!/usr/bin/env python3
"""Validate per-game release assets against the catalog pack bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).parents[1]
DOWNLOAD_MARKER = "/releases/download/"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def release_of(entry: dict) -> str | None:
    url = str(entry.get("downloadUrl", ""))
    if DOWNLOAD_MARKER not in url:
        return None
    return url.split(DOWNLOAD_MARKER, 1)[1].split("/", 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    base = ROOT / "release" / "game-assets" / args.version
    catalog = json.loads((ROOT / "cheats.json").read_text(encoding="utf-8"))
    entries = [entry for entry in catalog["entries"] if release_of(entry) == args.version]
    index = json.loads((base / "pack-assets.json").read_text(encoding="utf-8"))
    if len(index["packs"]) != len(entries):
        raise SystemExit("asset index/catalog count mismatch")
    by_serial = {item["serial"]: item for item in index["packs"]}
    bad: list[str] = []
    for entry in entries:
        serial = entry["serials"][0]
        item = by_serial.get(serial)
        if item is None:
            bad.append(f"{serial}: missing index entry")
            continue
        source = ROOT / entry["packPath"]
        pnach = base / item["pnachAsset"]
        if pnach.read_bytes() != source.read_bytes():
            bad.append(f"{serial}: pnach bytes differ from catalog pack")
        if sha(pnach) != entry["sha256"] or sha(pnach) != item["pnachSha256"]:
            bad.append(f"{serial}: pnach SHA mismatch")
        if "zipAsset" in item:
            archive = base / item["zipAsset"]
            with zipfile.ZipFile(archive) as output:
                names = output.namelist()
                expected = f"{serial}.pnach"
                if names != [expected] or output.read(expected) != source.read_bytes():
                    bad.append(f"{serial}: ZIP payload mismatch")
            if sha(archive) != item["zipSha256"]:
                bad.append(f"{serial}: ZIP SHA mismatch")
    if bad:
        raise SystemExit("; ".join(bad[:10]))
    has_zips = any("zipAsset" in item for item in index["packs"])
    print(f"validated {len(entries)} pnach assets" + (" and ZIP assets" if has_zips else ""))
    print(f"asset directory: {base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
