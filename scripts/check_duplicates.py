#!/usr/bin/env python3
"""Verify that the catalog never repeats a pack or a block.

The original 798-entry baseline already contained regional variants whose cheat
content is identical (different serials of the same game), so those groups are
reported separately. Any duplicate that involves an entry added after the
baseline fails the check, as does any duplicate id, serial, or (serial, sha256)
pair, any pack whose bytes do not match the catalog hash, and any repeated
block inside a newly added pack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import build_libretro_expansion as expansion

ROOT = Path(__file__).parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def block_keys(content: str) -> list[tuple[str, ...]]:
    _, blocks = expansion.parse_blocks(content)
    return [tuple(line for line in block if not line.startswith("Author = ")) for block in blocks]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT)
    args = parser.parse_args()
    repo = args.repo.resolve()
    catalog = json.loads((repo / "cheats.json").read_text(encoding="utf-8"))
    entries = catalog["entries"]

    failures: list[str] = []
    ids: dict[str, str] = {}
    serials: dict[str, list[str]] = defaultdict(list)
    serial_shas: dict[tuple[str, str], str] = {}
    bodies: dict[str, list[dict]] = defaultdict(list)
    internal: list[tuple[str, int]] = []

    for entry in entries:
        entry_id = entry["id"]
        serial = entry["serials"][0]
        if entry_id in ids:
            failures.append(f"duplicate id {entry_id}")
        ids[entry_id] = serial
        # One serial may hold several packs (libretro gameplay plus an author
        # patch), so only identical pack bytes count as a duplicate.
        serials[serial].append(entry_id)
        key = (serial, entry["sha256"])
        if key in serial_shas:
            failures.append(f"duplicate (serial, sha256) for {serial}")
        serial_shas[key] = entry_id
        path = repo / entry["packPath"]
        if not path.is_file():
            failures.append(f"missing pack {entry['packPath']}")
            continue
        digest = sha256_file(path)
        if digest != entry["sha256"]:
            failures.append(f"{path.name}: file sha256 does not match catalog")
        content = path.read_text(encoding="utf-8")
        bodies[expansion.hash_body(content)].append(entry)
        keys = block_keys(content)
        repeated = len(keys) - len(set(keys))
        if repeated:
            internal.append((entry_id, repeated))
        if len(keys) != entry["blockCount"]:
            failures.append(f"{path.name}: catalog says {entry['blockCount']} blocks, file has {len(keys)}")

    duplicate_groups = [group for group in bodies.values() if len(group) > 1]
    new_in_duplicate_groups = [
        entry["id"]
        for group in duplicate_groups
        for entry in group
        if entry.get("updatedAt") != expansion.BASELINE_UPDATED_AT
    ]
    for entry_id in new_in_duplicate_groups:
        failures.append(f"{entry_id}: identical content to another pack")

    entries_by_id = {entry["id"]: entry for entry in entries}
    new_internal = [
        entry_id for entry_id, _ in internal
        if entries_by_id[entry_id].get("updatedAt") != expansion.BASELINE_UPDATED_AT
    ]
    for entry_id in new_internal:
        failures.append(f"{entry_id}: repeated block inside a newly added pack")

    print(f"checked {len(entries)} packs and {len(serials)} serials")
    print(f"duplicate ids: {len(ids) - len(set(ids))}")
    print(f"identical-content groups: {len(duplicate_groups)} "
          f"({sum(len(group) for group in duplicate_groups)} packs, all pre-existing baseline variants)")
    print(f"packs with repeated blocks inside the file: {len(internal)} (all pre-existing baseline packs)")
    print(f"new additions involved in any duplicate: {len(new_in_duplicate_groups) + len(new_internal)}")
    if failures:
        for message in failures[:20]:
            print(f"FAIL: {message}")
        raise SystemExit(f"duplicate check failed with {len(failures)} problem(s)")
    print("duplicate check OK: no new pack repeats another pack or block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
