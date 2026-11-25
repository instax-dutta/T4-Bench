#!/usr/bin/env python3
"""Archive generated benchmark media into one deduplicated gzip tar.

Sources are sibling folders next to the repository (the original local-only
benchmark projects). Stills are converted to lossless WebP and verified by
decoded RGBA hash; videos are copied unchanged. Duplicate payloads are stored
once in the tar and recreated as hardlinks on extraction.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT.parent
MEDIA_ROOT = ROOT / "benchmarks" / "media"
SOURCES = ["image-model-bench", "video-gen-bench", "minimax-h3-bench"]
STILL_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
VIDEO_EXT = {".mp4", ".webm"}
ARCHIVE = MEDIA_ROOT / "benchmark-media.tar.gz"
PART_SIZE = 80 * 1024 * 1024
MANIFEST = MEDIA_ROOT / "MANIFEST.json"
INVENTORY = ROOT / "DATA-INVENTORY.md"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_oid(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def lossless_webp(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["cwebp", "-quiet", "-lossless", "-z", "9", str(source), "-o", str(target)],
        check=True,
    )
    with Image.open(source) as a, Image.open(target) as b:
        aa, bb = a.convert("RGBA"), b.convert("RGBA")
        if aa.size != bb.size or aa.tobytes() != bb.tobytes():
            raise RuntimeError(f"lossless conversion changed pixels: {source}")


def main() -> None:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="t4-media-") as tmp:
        stage = Path(tmp)
        seen: dict[str, Path] = {}
        for source_name in SOURCES:
            src_root = HOME / source_name
            if not src_root.exists():
                continue
            for source in sorted(src_root.rglob("*")):
                if not source.is_file():
                    continue
                suffix = source.suffix.lower()
                if suffix not in STILL_EXT | VIDEO_EXT:
                    continue
                rel = source.relative_to(src_root)
                is_still = suffix in STILL_EXT
                target_rel = rel.with_suffix(".webp") if is_still else rel
                target = stage / source_name / target_rel
                target.parent.mkdir(parents=True, exist_ok=True)
                original = source.read_bytes()
                if is_still:
                    lossless_webp(source, target)
                else:
                    shutil.copy2(source, target)
                data = target.read_bytes()
                digest = sha256_bytes(data)
                if digest in seen:
                    os.link(seen[digest], target)
                else:
                    seen[digest] = target
                entry = {
                    "path": f"benchmarks/media/{source_name}/{target_rel.as_posix()}",
                    "kind": "image" if is_still else "video",
                    "bytes": len(data),
                    "sha256": digest,
                }
                if is_still:
                    with Image.open(target) as im:
                        rgba = im.convert("RGBA")
                        entry.update(
                            width=im.width,
                            height=im.height,
                            decodedRgbaSha256=sha256_bytes(rgba.tobytes()),
                            originalBytes=len(original),
                            originalPngBlob=git_blob_oid(original),
                        )
                entries.append(entry)

        if not entries:
            raise SystemExit("no source media found")
        temp_archive = MEDIA_ROOT / ".benchmark-media.tar.gz.tmp"
        with tarfile.open(temp_archive, "w:gz", compresslevel=9) as tf:
            for source_name in SOURCES:
                folder = stage / source_name
                if folder.exists():
                    tf.add(folder, arcname=source_name)

    archive_bytes = temp_archive.read_bytes()
    for old_part in MEDIA_ROOT.glob("benchmark-media.tar.gz.*"):
        old_part.unlink()
    parts = []
    for index, offset in enumerate(range(0, len(archive_bytes), PART_SIZE)):
        chunk = archive_bytes[offset:offset + PART_SIZE]
        part = MEDIA_ROOT / f"benchmark-media.tar.gz.{index:03d}"
        part.write_bytes(chunk)
        parts.append({
            "path": f"benchmarks/media/{part.name}",
            "bytes": len(chunk),
            "sha256": sha256_bytes(chunk),
        })
    temp_archive.unlink()
    unique = {e["sha256"] for e in entries}
    manifest = {
        "schemaVersion": 3,
        "generated": "2026-11-25",
        "archive": {
            "format": "gzip-compressed tar with hardlink deduplication, split into 80 MiB parts",
            "bytes": len(archive_bytes),
            "sha256": sha256_bytes(archive_bytes),
            "logicalFileCount": len(entries),
            "uniqueFileCount": len(unique),
            "parts": parts,
        },
        "pixelEquivalence": "Archived WebP stills decode to the same RGBA pixels as the original source images.",
        "fileCount": len(entries),
        "uniqueFileCount": len(unique),
        "files": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    INVENTORY.write_text(
        "# Local data archived into this repository\n\n"
        "Generated on 2026-11-19; storage normalized on 2026-11-25. "
        "Benchmark media lives in one optional-extraction archive split below GitHub's file-size limit.\n\n"
        "## Archive\n\n"
        f"- `benchmarks/media/benchmark-media.tar.gz.*` - {len(archive_bytes):,} bytes total "
        f"({len(archive_bytes) / 1024 / 1024:.1f} MiB) in {len(parts)} parts\n"
        f"- {len(entries)} logical media paths, {len(unique)} unique payloads\n"
        f"- {sum(e['kind'] == 'image' for e in entries)} lossless WebP stills and "
        f"{sum(e['kind'] == 'video' for e in entries)} videos\n"
        "- `benchmarks/media/MANIFEST.json` records archive and per-file hashes\n\n"
        "## Extract when needed\n\n"
        "```bash\n"
        "python3 benchmarks/media/extract.py --check\n"
        "python3 benchmarks/media/extract.py\n"
        "```\n",
        encoding="utf-8",
    )
    print(f"archived {len(entries)} files ({len(unique)} unique) to {len(parts)} parts")


if __name__ == "__main__":
    main()
