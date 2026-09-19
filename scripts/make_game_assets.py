#!/usr/bin/env python3
"""Create per-game release assets from the validated catalog packs.

The Android client consumes the individual ``.pnach`` URLs in ``cheats.json``.
Use ``--pnach-only`` for the release index when GitHub's release asset limit
matters; ZIPs remain available for local archival builds and the aggregate
release archive.
"""
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
    parser.add_argument(
        "--pnach-only",
        action="store_true",
        help="write the index without per-game ZIP fields/assets",
    )
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
        pnach_name = f"PSP-Cheat-Catalog-{version}-{serial}.pnach"
        pnach = out / pnach_name
        pnach.write_bytes(source.read_bytes())
        item: dict[str, object] = {
            "serial": serial,
            "catalogId": entry["id"],
            "pnachAsset": pnach_name,
            "pnachUrl": f"{RELEASE_REPO}/{version}/{pnach_name}",
            "pnachSha256": digest(pnach),
            "pnachBytes": pnach.stat().st_size,
        }
        if not args.pnach_only:
            zip_name = f"PSP-Cheat-Catalog-{version}-{serial}.zip"
            archive = out / zip_name
            if archive.exists():
                archive.unlink()
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
                # Pin ZIP metadata so rebuilding the same pack preserves its SHA.
                info = zipfile.ZipInfo(f"{serial}.pnach", date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                output.writestr(info, source.read_bytes())
            item.update({
                "zipAsset": zip_name,
                "zipUrl": f"{RELEASE_REPO}/{version}/{zip_name}",
                "zipSha256": digest(archive),
                "zipBytes": archive.stat().st_size,
            })
        assets.append(item)
    index = out / "pack-assets.json"
    index.write_text(json.dumps({"version": version, "packs": assets}, indent=2) + "\n", encoding="utf-8", newline="\n")
    mode = "pnach assets" if args.pnach_only else "per-game pnach assets and ZIP assets"
    print(f"created {len(assets)} {mode} in {out}")
    print(f"index {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
