#!/usr/bin/env python3
"""Verify the pinned CWCheat source hash and generated build report."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).parents[1]
EXPECTED_URL = "https://raw.githubusercontent.com/Saramagrean/CWCheat-Database-Plus-/750261bccdc39569dec5eaee380902ac1442a007/cheat.db"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    if args.source:
        payload = args.source.read_bytes()
    else:
        request = Request(EXPECTED_URL, headers={"User-Agent": "EmuCoreA-Cheat-validator"})
        with urlopen(request, timeout=45) as response:
            payload = response.read()
    digest = hashlib.sha256(payload).hexdigest().upper()
    report = json.loads((ROOT / "build-report.json").read_text(encoding="utf-8"))
    if report.get("source") != EXPECTED_URL:
        raise SystemExit("validation failed: build report source is not pinned")
    if report.get("sourceSha256") != digest:
        raise SystemExit(f"validation failed: source hash {digest} != report {report.get('sourceSha256')}")
    print(f"verified pinned source {EXPECTED_URL}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
