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
RELEASE_REPO = "https://github.com/sashkinbro/EmuCoreA-Cheat/releases/download"
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
    # Batch 006: additional serials from the same pinned libretro snapshot.
    "NPJH-50701", "UCES-01264", "ULUS-10310", "ULJM-05552", "UCES-01242",
    "UCES-01245", "NPJH-50473", "ULJM-05101", "ULES-01183", "UCJS-10100",
    "UCUS-98633", "ULJM-05600", "ULES-00850", "ULJS-00237", "ULES-00841",
    "ULUS-10375", "ULJM-05940", "UCES-00356", "ULJS-00097", "NPJH-50043",
    "ULES-00176", "ULAS-42060", "ULES-00318", "UCUS-98711", "ULUS-10084",
    # Batch 007: additional PSP serials from the same pinned libretro snapshot.
    "NPUH-10041", "UCES-00995", "ULUS-10529", "ULES-01392", "ULUS-10461",
    "ULES-00193", "ULUS-10202", "ULES-00724", "ULUS-10107", "ULES-01507",
    "NPJH-50567", "UCUS-98716", "ULUS-10308", "ULES-01298", "NPJH-50588",
    "ULES-00180", "ULUS-10457", "ULJM-05976", "ULJM-05814", "ULJM-05604",
    "NPJH-50377", "ULES-01044", "ULJM-05353", "ULJS-00202", "ULES-01347",
    # Batch 008: additional PSP serials from the same pinned libretro snapshot.
    "ULUS-10251", "ULES-00756", "ULUS-10142", "ULUS-10263", "ULUS-10380",
    "ULJM-05410", "NPJH-50721", "NPJH-50435", "ULUS-10505", "ULJM-05490",
    "ULJM-05262", "ULUS-10141", "ULUS-10432", "ULJS-00183", "NPJH-50625",
    "NPJH-50045", "NPJH-50263", "ULUS-10438", "ULES-01376", "UCUS-98612",
    "ULUS-10097", "ULUS-10211", "ULJM-05299", "NPJH-50681", "ULJS-00293",
    # Batch 009: additional PSP serials from the same pinned libretro snapshot.
    "ULES-01144", "NPHH-00068", "ULJS-00363", "ULUS-10495", "ULUS-10134",
    "ULJM-05493", "ULES-00982", "ULES-00981", "ULUS-10543", "ULUS-10345",
    "ULUS-10292", "ULJM-05427", "ULES-00999", "ULUS-10087", "ULES-01151",
    "ULUS-10416", "ULUS-10323", "ULUS-10282", "UCKS-45076", "NPUH-10126",
    "ULUS-10452", "ULJM-05781", "UCJS-10093", "ULES-00419", "NPJH-50276",
    # Batch 010: additional PSP serials from the same pinned libretro snapshot.
    "ULES-01441", "ULUS-10086", "ULJS-00178", "ULES-01489", "ULJS-00460",
    "ULES-01472", "ULUS-10068", "ULES-01154", "NPJH-50353", "ULUS-10277",
    "ULES-01537", "ULJS-00167", "ULES-01431", "ULES-01045", "NPJH-50430",
    "NPUH-10197", "NPUH-10191", "ULJS-00175", "ULUS-10289", "ULUS-10089",
    "ULJS-00377", "ULUS-10593", "ULUS-10045", "ULES-00987", "ULES-00645",
    # Batch 011: additional PSP serials from the same pinned libretro snapshot.
    "UCES-01312", "NPJH-50044", "ULES-01322", "ULUS-10383", "NPJH-50530",
    "ULES-00959", "ULUS-10409", "NPUH-10198", "ULJM-05611", "ULJM-05492",
    "UCES-00001", "NPJH-50717", "NPJH-50331", "ULJM-06081", "ULJM-05440",
    "NPJH-50459", "ULUS-10506", "ULJM-05524", "ULES-01429", "NPJH-50316",
    "ULUS-10340", "ULJS-00188", "ULUS-10400", "ULES-01330", "NPUH-10195",
    # Batch 012: additional PSP serials from the same pinned libretro snapshot.
    "NPJH-50716", "ULUS-10513", "ULUS-10442", "ULUS-10218", "ULUS-10176",
    "ULJM-05676", "ULJM-05241", "ULJM-05127", "ULJM-05472", "UCJS-10095",
    "NPJH-50441", "ULUS-10455", "ULJM-05300", "NPJH-50566", "ULUS-10515",
    "ULUS-10339", "ULJS-00168", "ULES-01145", "NPUZ-00132", "ULJS-00190",
    "ULJS-00169", "ULJM-05321", "ULES-00740", "UCUS-98640", "UCJS-10109",
    # Batch 013: additional PSP serials from the same pinned libretro snapshot.
    "ALJS-00351", "CAVE-00960", "CAVE-00992", "CSPS-01360", "NPEG-00004",
    "NPEG-00008", "NPEG-00009", "NPEG-00017", "NPEG-00018", "NPEG-00019",
    "NPEG-00023", "NPEG-00025", "NPEG-00028", "NPEG-00037", "NPEG-00044",
    "NPEG-00046", "NPEG-00047", "NPEG-00048", "NPEG-00049", "NPEG-20029",
    "NPEG-90003", "NPEG-90008", "NPEG-90009", "NPEG-90012", "NPEG-90014",
    # Batch 014: additional PSP serials from the same pinned libretro snapshot.
    "NPEG-90015",    "NPEG-90018",    "NPEG-90019",    "NPEG-90020",    "NPEG-90025",
    "NPEG-90026",    "NPEG-90030",    "NPEG-90035",    "NPEH-00002",    "NPEH-00003",
    "NPEH-00007",    "NPEH-00017",    "NPEH-00020",    "NPEH-00021",    "NPEH-00027",
    "NPEH-00029",    "NPEH-00031",    "NPEH-00033",    "NPEH-00064",    "NPEH-00065",
    "NPEH-00073",    "NPEH-00076",    "NPEH-00077",    "NPEH-00100",    "NPEH-00124",
    # Batch 015: 100 additional PSP serials from the same pinned libretro snapshot.
    "NPEH-00154",    "NPEH-00166",    "NPEH-00170",    "NPEH-10029",    "NPEH-90001",
    "NPEH-90006",    "NPEH-90011",    "NPEH-90014",    "NPEH-90015",    "NPEH-90022",
    "NPEH-90026",    "NPEH-90028",    "NPEH-90032",    "NPEH-90038",    "NPEH-90049",
    "NPEH-90051",    "NPEX-00004",    "NPEX-00005",    "NPEZ-00001",    "NPEZ-00002",
    "NPEZ-00003",    "NPEZ-00004",    "NPEZ-00007",    "NPEZ-00009",    "NPEZ-00011",
    "NPEZ-00021",    "NPEZ-00022",    "NPEZ-00023",    "NPEZ-00024",    "NPEZ-00025",
    "NPEZ-00027",    "NPEZ-00031",    "NPEZ-00032",    "NPEZ-00041",    "NPEZ-00042",
    "NPEZ-00043",    "NPEZ-00044",    "NPEZ-00045",    "NPEZ-00046",    "NPEZ-00047",
    "NPEZ-00058",    "NPEZ-00080",    "NPEZ-00081",    "NPEZ-00087",    "NPEZ-00093",
    "NPEZ-00094",    "NPEZ-00095",    "NPEZ-00096",    "NPEZ-00098",    "NPEZ-00100",
    "NPEZ-00101",    "NPEZ-00107",    "NPEZ-00108",    "NPEZ-00115",    "NPEZ-00117",
    "NPEZ-00118",    "NPEZ-00122",    "NPEZ-00124",    "NPEZ-00126",    "NPEZ-00130",
    "NPEZ-00131",    "NPEZ-00133",    "NPEZ-00135",    "NPEZ-00136",    "NPEZ-00140",
    "NPEZ-00145",    "NPEZ-00147",    "NPEZ-00149",    "NPEZ-00151",    "NPEZ-00153",
    "NPEZ-00154",    "NPEZ-00157",    "NPEZ-00158",    "NPEZ-00164",    "NPEZ-00166",
    "NPEZ-00167",    "NPEZ-00168",    "NPEZ-00171",    "NPEZ-00176",    "NPEZ-00178",
    "NPEZ-00184",    "NPEZ-00185",    "NPEZ-00195",    "NPEZ-00196",    "NPEZ-00199",
    "NPEZ-00200",    "NPEZ-00203",    "NPEZ-00205",    "NPEZ-00212",    "NPEZ-00215",
    "NPEZ-00217",    "NPEZ-00218",    "NPEZ-00219",    "NPEZ-00222",    "NPEZ-00225",
    "NPEZ-00229",    "NPEZ-00230",    "NPEZ-00235",    "NPEZ-00236",    "NPEZ-00237",

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
        "# PSP cheat pack",
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
    parser.add_argument("--batch-id", default="batch-015")
    parser.add_argument("--release-version", default="cheat-catalog")
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
            "downloadUrl": f"{RELEASE_REPO}/{args.release_version}/PSP-Cheat-Catalog-{args.release_version}-{serial}.pnach",
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
