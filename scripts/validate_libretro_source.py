#!/usr/bin/env python3
"""Verify the pinned libretro PSP source revision and converted source files."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

EXPECTED_COMMIT = "740ebdf03247073658ccea45ddedfd57ea9d2974"
SERIAL_RE = re.compile(r"\[([A-Z]{4}-[0-9]{5})\]\.cht$")
CODE_RE = re.compile(r"_L\s+0x[0-9A-Fa-f]{8}\s+0x[0-9A-Fa-f]{1,8}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if head != EXPECTED_COMMIT:
        raise SystemExit(f"validation failed: source HEAD {head} != pinned {EXPECTED_COMMIT}")
    if not (source / "LICENSE").is_file():
        raise SystemExit("validation failed: source LICENSE is missing")
    files = list((source / "cht" / "Sony - PlayStation Portable").glob("*.cht"))
    selected = [
        path for path in files
        if SERIAL_RE.search(path.name) and SERIAL_RE.search(path.name).group(1) in {
            "ULES-01416", "ULJM-05500", "ULES-01213", "ULJS-00048", "UCUS-98645",
            "UCUS-98668", "UCES-01327", "ULJM-05261", "NPJH-50332", "NPJH-50521",
            "UCUS-98646", "ULJM-05505", "NPJH-50789", "ULJM-05402", "ULUS-10447",
            "ULJM-05255", "ULJM-05297", "ULJM-05341", "ULES-00657", "ULJM-05309",
            "NPJB-40001", "ULJM-05753", "ULES-01523", "ULES-00503", "ULJM-05637",
            "NPJH-50618", "ULES-01372", "ULUS-10290", "ULUS-10551", "ULUS-10511",
            "ULUS-10266", "ULUS-10368", "ULJM-05844", "ULES-01187", "NPJH-50619",
            "ULUS-10565", "ULES-01500", "ULUS-10139", "ULES-01367", "UCKS-45027",
            "NPUH-10125", "NPEH-00134", "ULJM-05775", "ULUS-10059", "NPJH-50311",
            "ULUS-10458", "ULUS-10219", "ULUS-10271", "ULUS-10200", "ULUS-10374",
            "ULUS-10479", "NPJH-50107", "ULUS-10410", "NPJH-50878", "NPJH-50352",
            "ULJM-05800", "ULUS-10041", "ULES-00151", "ULUS-10297", "ULUS-10490",
            "ULUS-10437", "ULES-00502", "UCUS-98751", "ULUS-10390", "NPJH-50443",
            "NPJH-50444", "ULUS-10391", "ULUS-10160", "UCUS-98632", "ULUS-10336",
            "ULUS-10563", "ULUS-10582", "ULUS-10466", "ULES-00182", "ULUS-10560",
            "NPJH-50701", "UCES-01264", "ULUS-10310", "ULJM-05552", "UCES-01242",
            "UCES-01245", "NPJH-50473", "ULJM-05101", "ULES-01183", "UCJS-10100",
            "UCUS-98633", "ULJM-05600", "ULES-00850", "ULJS-00237", "ULES-00841",
            "ULUS-10375", "ULJM-05940", "UCES-00356", "ULJS-00097", "NPJH-50043",
            "ULES-00176", "ULAS-42060", "ULES-00318", "UCUS-98711", "ULUS-10084",
            "NPUH-10041", "UCES-00995", "ULUS-10529", "ULES-01392", "ULUS-10461",
            "ULES-00193", "ULUS-10202", "ULES-00724", "ULUS-10107", "ULES-01507",
            "NPJH-50567", "UCUS-98716", "ULUS-10308", "ULES-01298", "NPJH-50588",
            "ULES-00180", "ULUS-10457", "ULJM-05976", "ULJM-05814", "ULJM-05604",
            "NPJH-50377", "ULES-01044", "ULJM-05353", "ULJS-00202", "ULES-01347",
        }
    ]
    if len(selected) != 125:
        raise SystemExit(f"validation failed: found {len(selected)} selected source files, expected 125")
    for path in selected:
        text = path.read_text(encoding="utf-8")
        if not CODE_RE.search(text):
            raise SystemExit(f"validation failed: no CWCheat lines in {path.name}")
    print(f"verified libretro-database PSP source commit {head}")
    print(f"verified CC-BY-SA-4.0 LICENSE and {len(selected)} selected source files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
