#!/usr/bin/env python3
"""Convert a pinned libretro PSP .cht batch into EmuCoreA serial packs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SOURCE_COMMIT = "740ebdf03247073658ccea45ddedfd57ea9d2974"
SOURCE_NAME = "libretro-database PSP cheats"
SOURCE_URL = "https://github.com/libretro/libretro-database"
SOURCE_PAGE = f"https://github.com/libretro/libretro-database/blob/{SOURCE_COMMIT}/cht/Sony%20-%20PlayStation%20Portable"
LICENSE = "CC-BY-SA-4.0 repository license; individual upstream code authors remain credited"

SERIALS = {
    "ULES-01416", "ULJM-05500", "ULES-01213", "ULJS-00048", "UCUS-98645",
    "UCUS-98668", "UCES-01327", "ULJM-05261", "NPJH-50332", "NPJH-50521",
    "UCUS-98646", "ULJM-05505", "NPJH-50789", "ULJM-05402", "ULUS-10447",
    "ULJM-05255", "ULJM-05297", "ULJM-05341", "ULES-00657", "ULJM-05309",
    "NPJB-40001", "ULJM-05753", "ULES-01523", "ULES-00503", "ULJM-05637",
    # Batch 004: additional regional and Japanese entries from the same
    # pinned libretro-database PSP snapshot.
    "NPJH-50618", "ULES-01372", "ULUS-10290", "ULUS-10551", "ULUS-10511",
    "ULUS-10266", "ULUS-10368", "ULJM-05844", "ULES-01187", "NPJH-50619",
    "ULUS-10565", "ULES-01500", "ULUS-10139", "ULES-01367", "UCKS-45027",
    "NPUH-10125", "NPEH-00134", "ULJM-05775", "ULUS-10059", "NPJH-50311",
    "ULUS-10458", "ULUS-10219", "ULUS-10271", "ULUS-10200", "ULUS-10374",
    # Batch 005: additional serials now distributed only through the
    # explicitly licensed libretro source path.
    "ULUS-10479", "NPJH-50107", "ULUS-10410", "NPJH-50878", "NPJH-50352",
    "ULJM-05800", "ULUS-10041", "ULES-00151", "ULUS-10297", "ULUS-10490",
    "ULUS-10437", "ULES-00502", "UCUS-98751", "ULUS-10390", "NPJH-50443",
    "NPJH-50444", "ULUS-10391", "ULUS-10160", "UCUS-98632", "ULUS-10336",
    "ULUS-10563", "ULUS-10582", "ULUS-10466", "ULES-00182", "ULUS-10560",
}
SERIAL_RE = re.compile(r"\[([A-Z]{4}-[0-9]{5})\]\.cht$")
DESC_RE = re.compile(r'^cheat(\d+)_desc\s*=\s*("(?:\\.|[^"\\])*")$', re.MULTILINE)
CODE_RE = re.compile(r'^cheat(\d+)_code\s*=\s*("(?:\\.|[^"\\])*")$', re.MULTILINE)
LINE_RE = re.compile(r"_L\s+0x([0-9A-Fa-f]{8})\s+0x([0-9A-Fa-f]{1,8})")


def quoted(value: str) -> str:
    # libretro's INI values escape quotes, but some historical files also
    # contain backslash escapes that are not JSON escapes. Preserve text while
    # unquoting the INI value instead of rejecting an otherwise valid cheat.
    inner = value[1:-1]
    inner = inner.replace('\\"', '"')
    return inner.replace('\\\\', '\\')


def convert(path: Path, serial: str) -> tuple[str, int, int, int]:
    text = path.read_text(encoding="utf-8")
    descriptions = {int(index): quoted(value) for index, value in DESC_RE.findall(text)}
    codes = {int(index): quoted(value) for index, value in CODE_RE.findall(text)}
    output = [
        "# EmuCoreA PSP cheat pack",
        f"# Serial: {serial}",
        f"# Source: {SOURCE_PAGE}",
        "",
    ]
    blocks = excluded = malformed = 0
    for index in sorted(set(descriptions) | set(codes)):
        title = descriptions.get(index, f"Untitled cheat {index}").strip() or f"Untitled cheat {index}"
        raw_lines = LINE_RE.findall(codes.get(index, ""))
        if not raw_lines:
            excluded += 1
            continue
        lines: list[str] = []
        for address, value in raw_lines:
            if address.upper() == "00000000" and value.upper() == "00000000":
                continue
            normalized = f"{address.upper()} {value.upper()}"
            if normalized not in lines:
                lines.append(normalized)
        if not lines:
            excluded += 1
            continue
        # Any _L token that did not match the strict pair regex is excluded
        # from this block rather than silently changing upstream code.
        if codes.get(index, "").count("_L") != len(raw_lines):
            malformed += 1
            excluded += 1
            continue
        output.append(f"// {title}")
        output.append("Author = libretro-database contributors / original PSP cheat authors")
        output.extend(lines)
        output.append("")
        blocks += 1
    return "\n".join(output).rstrip() + "\n", blocks, excluded, malformed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).parents[2] / "libretro-database-psp")
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--batch-id", default="batch-005")
    parser.add_argument("--release-version", default="v1.0.5")
    args = parser.parse_args()
    source_root = args.source.resolve() / "cht" / "Sony - PlayStation Portable"
    repo = args.repo.resolve()
    output_root = repo / "files" / "libretro-psp"
    output_root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    report: list[dict[str, object]] = []
    for serial in sorted(SERIALS):
        candidates = [
            candidate for candidate in source_root.glob("*.cht")
            if (match := SERIAL_RE.search(candidate.name)) and match.group(1) == serial
        ]
        if not candidates:
            raise SystemExit(f"missing pinned libretro file for {serial}")
        # The serial suffix is unique in the upstream PSP folder.
        path = next((candidate for candidate in candidates if SERIAL_RE.search(candidate.name)), candidates[0])
        contents, blocks, excluded, malformed = convert(path, serial)
        if blocks < 1:
            raise SystemExit(f"no usable blocks for {serial}: {path.name}")
        target = output_root / f"{serial}.pnach"
        target.write_text(contents, encoding="utf-8", newline="\n")
        digest = hashlib.sha256(contents.encode("utf-8")).hexdigest().upper()
        title = path.name.rsplit(" [", 2)[0]
        entries.append({
            "id": f"libretro-psp-{serial.lower()}",
            "title": title,
            "serials": [serial],
            "authors": ["libretro-database contributors and the original PSP cheat authors"],
            "description": f"{blocks} libretro PSP cheat blocks for {serial}; {excluded} empty or malformed upstream blocks excluded.",
            "downloadUrl": f"https://raw.githubusercontent.com/sashkinbro/EmuCoreA-Cheat/main/files/libretro-psp/{serial}.pnach",
            "packPath": f"files/libretro-psp/{serial}.pnach",
            "sourceUrl": SOURCE_PAGE,
            "sourceName": SOURCE_NAME,
            "license": LICENSE,
            "blockCount": blocks,
            "updatedAt": "2026-09-19T00:00:00Z",
            "sha256": digest,
        })
        report.append({"serial": serial, "sourceFile": path.name, "blocks": blocks, "excluded": excluded, "malformed": malformed, "sha256": digest})
    catalog_path = repo / "cheats.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["entries"] = [entry for entry in catalog["entries"] if entry.get("sourceName") != SOURCE_NAME] + entries
    catalog["entries"].sort(key=lambda entry: entry["serials"][0])
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    report_path = repo / "build-report.json"
    report_data = {
        "batch": args.batch_id,
        "release": args.release_version,
        "libretroSource": f"https://raw.githubusercontent.com/libretro/libretro-database/{SOURCE_COMMIT}/cht/Sony%20-%20PlayStation%20Portable",
        "libretroCommit": SOURCE_COMMIT,
        "libretroEntries": report,
    }
    report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"generated {len(entries)} libretro PSP packs from {source_root}")
    print(f"blocks: {sum(item['blocks'] for item in report)}; excluded: {sum(item['excluded'] for item in report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
