#!/usr/bin/env python3
"""Validate the EmuCoreA PSP catalog without third-party dependencies."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
CATALOG = ROOT / "cheats.json"
CODE_RE = re.compile(r"^[0-9A-Fa-f]{8}[\s:+-]+[0-9A-Fa-f]{1,8}$")
SERIAL_RE = re.compile(r"^[A-Z]{4}-[0-9]{5}$")


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def main() -> int:
    try:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    except Exception as error:
        fail(f"cannot read cheats.json: {error}")
    if catalog.get("schemaVersion") != 1 or not isinstance(catalog.get("entries"), list):
        fail("schemaVersion must be 1 and entries must be an array")
    ids: set[str] = set()
    serials: set[str] = set()
    for entry in catalog["entries"]:
        required = ["id", "title", "serials", "authors", "description", "downloadUrl", "sourceUrl", "sourceName", "license", "blockCount"]
        missing = [key for key in required if key not in entry]
        if missing:
            fail(f"{entry!r} missing {missing}")
        if entry["id"] in ids:
            fail(f"duplicate id {entry['id']}")
        ids.add(entry["id"])
        if not entry["serials"] or any(not SERIAL_RE.fullmatch(value) for value in entry["serials"]):
            fail(f"invalid serials in {entry['id']}")
        if any(value in serials for value in entry["serials"]):
            fail(f"serial appears in more than one entry: {entry['serials']}")
        serials.update(entry["serials"])
        if not entry["authors"] or entry["blockCount"] < 1:
            fail(f"empty author list or block count for {entry['id']}")
        display_values = [str(entry["title"]), str(entry["description"])] + [str(author) for author in entry["authors"]]
        if any("emucorea" in value.casefold() for value in display_values):
            fail(f"display metadata must not claim EmuCoreA authorship for {entry['id']}")
        for field in ("downloadUrl", "sourceUrl"):
            if not str(entry[field]).startswith("https://"):
                fail(f"{field} must be HTTPS for {entry['id']}")
        relative_pack = entry.get("packPath", f"files/libretro-psp/{entry['serials'][0]}.pnach")
        path = (ROOT / relative_pack).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"packPath escapes repository for {entry['id']}")
        if not path.is_file():
            fail(f"missing pack {path}")
        text = path.read_text(encoding="utf-8")
        if text.startswith("# EmuCoreA"):
            fail(f"{path.name}: pack header must identify PSP/source context, not claim EmuCoreA authorship")
        blocks = 0
        active = 0
        for line in text.splitlines():
            if line.startswith("// "):
                blocks += 1
            elif line.startswith("#") or line.startswith("Author =") or not line.strip():
                continue
            elif CODE_RE.fullmatch(line.strip()):
                active += 1
            else:
                fail(f"unsupported line in {path.name}: {line!r}")
        if blocks != entry["blockCount"]:
            fail(f"{path.name}: catalog says {entry['blockCount']} blocks, file has {blocks}")
        if active == 0:
            fail(f"{path.name}: no active code lines")
        if "sha256" in entry:
            digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
            if digest != entry["sha256"]:
                fail(f"{path.name}: sha256 does not match catalog")
    print(f"validated {len(catalog['entries'])} packs and {len(serials)} serials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
