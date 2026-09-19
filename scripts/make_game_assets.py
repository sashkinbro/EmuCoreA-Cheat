#!/usr/bin/env python3
"""Create per-game release assets from the validated catalog packs."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).parents[1]
RELEASE_REPO = "https://github.com/sashkinbro/EmuCoreA-Cheat/releases/download"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    version = args.version.strip()
    if not version or any(char in version for char in "/\\:"):
        raise SystemExit("invalid release version")
    catalog = json.loads((ROOT / "cheats.json").read_text(encoding="utf-8"))
    out = ROOT / "release" / "game-assets" / version
    out.mkdir(parents=True, exist_ok=True)
    assets: list[dict[str, object]] = []
    for entry in sorted(catalog["entries"], key=lambda item: item["serials"][0]):
        serial = entry["serials"][0]
        source = ROOT / entry["packPath"]
        pnach_name = f"EmuCoreA-Cheat-{version}-{serial}.pnach"
        zip_name = f"EmuCoreA-Cheat-{version}-{serial}.zip"
        pnach = out / pnach_name
        pnach.write_bytes(source.read_bytes())
        archive = out / zip_name
        if archive.exists():
            archive.unlink()
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            output.write(source, f"{serial}.pnach")
        assets.append({
            "serial": serial,
            "catalogId": entry["id"],
            "pnachAsset": pnach_name,
            "pnachUrl": f"{RELEASE_REPO}/{version}/{pnach_name}",
            "pnachSha256": digest(pnach),
            "zipAsset": zip_name,
            "zipUrl": f"{RELEASE_REPO}/{version}/{zip_name}",
            "zipSha256": digest(archive),
            "pnachBytes": pnach.stat().st_size,
            "zipBytes": archive.stat().st_size,
        })
    index = out / "pack-assets.json"
    index.write_text(json.dumps({"version": version, "packs": assets}, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"created {len(assets)} per-game pnach assets and ZIP assets in {out}")
    print(f"index {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
