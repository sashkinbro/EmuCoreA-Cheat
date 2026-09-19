#!/usr/bin/env python3
"""Create a deterministic release ZIP containing the catalog and PSP packs."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, help="release tag, for example v1.0.0")
    args = parser.parse_args()
    version = args.version.strip()
    if not version or any(char in version for char in '/\\:'):
        raise SystemExit("invalid release version")
    catalog = json.loads((ROOT / "cheats.json").read_text(encoding="utf-8"))
    release = ROOT / "release"
    release.mkdir(exist_ok=True)
    archive = release / f"EmuCoreA-Cheat-{version}.zip"
    if archive.exists():
        archive.unlink()
    members = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "CONTRIBUTING.md", ROOT / "sources.json", ROOT / "cheats.json", ROOT / "build-report.json"]
    members += sorted((ROOT / "files" / "cwcheat-db-plus").glob("*.pnach"))
    unique: list[Path] = []
    seen: set[Path] = set()
    for member in members:
        if member not in seen:
            seen.add(member)
            unique.append(member)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for member in unique:
            output.write(member, member.relative_to(ROOT).as_posix())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest().upper()
    (release / f"EmuCoreA-Cheat-{version}.zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="ascii", newline="\n")
    print(f"created {archive} ({archive.stat().st_size} bytes)")
    print(f"sha256 {digest}")
    print(f"packs {len(catalog['entries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
