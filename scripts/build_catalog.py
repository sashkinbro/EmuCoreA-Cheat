#!/usr/bin/env python3
"""Build deterministic, serial-specific EmuCoreA packs from a CWCheat DB."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SOURCE_COMMIT = "750261bccdc39569dec5eaee380902ac1442a007"
SOURCE_RAW = f"https://raw.githubusercontent.com/Saramagrean/CWCheat-Database-Plus-/{SOURCE_COMMIT}/cheat.db"
SOURCE_PAGE = f"https://github.com/Saramagrean/CWCheat-Database-Plus-/blob/{SOURCE_COMMIT}/cheat.db"
SOURCE_NAME = "CWCheat Database Plus"
LICENSE = "Upstream terms; no blanket open-source license published"

# US releases with a useful, established code set. Keep regional revisions as
# separate entries when they are not byte-compatible.
SERIALS = {
    "ULUS-10041", "ULUS-10160", "ULUS-10490", "ULUS-10336", "ULUS-10297",
    "ULUS-10560", "ULUS-10437", "ULUS-10566", "UCUS-98653", "UCUS-98737",
    "ULUS-10505", "ULUS-10509", "ULUS-10202", "ULUS-10391", "ULUS-10084",
    "ULUS-10512", "ULUS-10466", "ULUS-10582", "UCUS-98751", "ULUS-10114",
    "ULUS-10383", "ULUS-10455", "ULUS-10277", "ULUS-10251", "ULUS-10263",
    # Batch 002: additional regional and Japanese serials from the same
    # pinned CWCheat Database Plus snapshot.
    "ULUS-10479", "ULJS-00266", "NPJH-50352", "UCUS-98632", "NPJH-50107",
    "NPJH-50878", "NPJH-50701", "NPJH-50832", "UCES-01245", "UCJS-10100",
    "NPUH-10041", "ULUS-10410", "ULUS-10563", "NPJH-50443", "NPJH-50444",
    "UCES-00995", "ULJM-05798", "ULUS-10529", "ULES-00318", "ULAS-42060",
    "ULES-00176", "ULUS-10154", "ULES-00530", "ULJM-05800", "ULES-00151",
}
CODE_RE = re.compile(r"^([0-9A-Fa-f]{8})[\s:+-]+([0-9A-Fa-f]{1,8})$")
SERIAL_RE = re.compile(r"^[A-Z]{4}-[0-9]{5}$")


def parse_db(text: str) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {}
    serial = ""
    game: dict[str, object] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("_S "):
            serial = line[3:].strip().upper()
            game = None
        elif line.startswith("_G ") and serial in SERIALS:
            game = {"title": line[3:].strip(), "blocks": []}
            result.setdefault(serial, []).append(game)
        elif line.startswith("_C") and game is not None:
            # CWCheat uses _C0/_C1 as the enabled flag; EmuCoreA controls that
            # state itself, so retain the block title and leave it disabled.
            title = line[3:].strip()
            if title.startswith("0") or title.startswith("1"):
                title = title[1:].lstrip()
            game["blocks"].append({"title": title or "Untitled cheat", "lines": [], "invalid": False})
        elif line.startswith("_L ") and game is not None and game["blocks"]:
            block = game["blocks"][-1]
            match = CODE_RE.match(line[3:].replace("0x", "", 2))
            if not match:
                block["invalid"] = True
                continue
            block["lines"].append(f"{match.group(1).upper()} {match.group(2).upper()}")
    return result


def pack_for(serial: str, game: dict[str, object]) -> tuple[str, int, int]:
    blocks: list[dict[str, object]] = []
    excluded = 0
    for block in game["blocks"]:
        # A zero address/value pair is a CWCheat placeholder, not an
        # executable code line. Remove it even when a block also contains
        # valid lines; an all-placeholder block is excluded below.
        lines = [line for line in block["lines"] if line != "00000000 00000000"]
        if block["invalid"] or not lines:
            excluded += 1
            continue
        blocks.append({"title": block["title"], "lines": list(dict.fromkeys(lines))})
    out: list[str] = []
    out.append(f"# EmuCoreA PSP cheat pack\n# Serial: {serial}\n# Source: {SOURCE_PAGE}\n")
    for block in blocks:
        out.append(f"// {block['title']}\nAuthor = Saramagrean / original CWCheat authors\n")
        out.extend(f"{line}\n" for line in block["lines"])
        out.append("\n")
    return "".join(out).rstrip() + "\n", len(blocks), excluded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).parents[2] / "CWCheat-Database-Plus" / "cheat.db")
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--batch-id", default="batch-002")
    parser.add_argument("--release-version", default="v1.0.2")
    args = parser.parse_args()
    source = args.source.resolve()
    repo = args.repo.resolve()
    source_bytes = source.read_bytes()
    text = source_bytes.decode("utf-8", errors="strict")
    # Git checkout settings may materialize the pinned blob with CRLF on
    # Windows. Hash the canonical UTF-8/LF representation so local and raw
    # GitHub verification produce the same provenance digest.
    canonical_source_bytes = text.replace("\r\n", "\n").encode("utf-8")
    parsed = parse_db(text)
    files = repo / "files" / "cwcheat-db-plus"
    files.mkdir(parents=True, exist_ok=True)
    for old in files.glob("*.pnach"):
        old.unlink()
    entries: list[dict[str, object]] = []
    report: list[dict[str, object]] = []
    for serial in sorted(SERIALS):
        games = parsed.get(serial, [])
        if not games:
            continue
        game = max(games, key=lambda value: len(value["blocks"]))
        contents, block_count, excluded = pack_for(serial, game)
        if block_count == 0:
            continue
        target = files / f"{serial}.pnach"
        target.write_text(contents, encoding="utf-8", newline="\n")
        digest = hashlib.sha256(contents.encode("utf-8")).hexdigest().upper()
        title = str(game["title"])
        entries.append({
            "id": f"cwcheat-{serial.lower().replace('-', '-')}",
            "title": title,
            "serials": [serial],
            "authors": ["Saramagrean and the original CWCheat code authors"],
            "description": f"{block_count} serial-specific CWCheat blocks for {serial}; {excluded} malformed upstream blocks excluded during conversion.",
            "downloadUrl": f"https://raw.githubusercontent.com/sashkinbro/EmuCoreA-Cheat/main/files/cwcheat-db-plus/{serial}.pnach",
            "sourceUrl": SOURCE_PAGE,
            "sourceName": SOURCE_NAME,
            "license": LICENSE,
            "blockCount": block_count,
            "updatedAt": "2026-09-19T00:00:00Z",
            "sha256": digest,
        })
        report.append({"serial": serial, "title": title, "blocks": block_count, "excluded": excluded, "sha256": digest})
    catalog = {"schemaVersion": 1, "generatedAt": "2026-09-19T00:00:00Z", "entries": entries}
    (repo / "cheats.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (repo / "build-report.json").write_text(json.dumps({"batch": args.batch_id, "release": args.release_version, "source": SOURCE_RAW, "sourceSha256": hashlib.sha256(canonical_source_bytes).hexdigest().upper(), "entries": report}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"generated {len(entries)} packs from {source}")
    print(f"source sha256: {hashlib.sha256(canonical_source_bytes).hexdigest().upper()}")
    for row in report:
        print(f"{row['serial']}: {row['blocks']} blocks, {row['excluded']} excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
