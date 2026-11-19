#!/usr/bin/env python3
"""Copy generated benchmark media and source research notes into the repo."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT.parent
MEDIA_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.webm'}
SOURCES = ['image-model-bench', 'video-gen-bench', 'minimax-h3-bench']

manifest = []

# Generated media from the three original benchmark projects.
for source in SOURCES:
    src_root = HOME / source
    if not src_root.exists():
        continue
    target_root = ROOT / 'benchmarks' / 'media' / source
    for path in src_root.rglob('*'):
        if path.is_file() and path.suffix.lower() in MEDIA_EXT:
            rel = path.relative_to(src_root)
            target = target_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            manifest.append(f"benchmarks/media/{source}/{rel}")

out = ROOT / 'DATA-INVENTORY.md'
out.write_text(
    "# Local data archived into this repository\n\n"
    "Generated on 2026-11-19. This file lists every file copied from local-only "
    "benchmark folders so the repository remains the single source of truth.\n\n"
    f"**Media files copied:** {sum(1 for m in manifest if m.startswith('benchmarks/media/'))}\n\n"
    "ZIP archives from the old project folders were not copied. They are snapshots "
    "of files already present here.\n\n"
    "## Manifest\n\n" + "\n".join(f"- `{m}`" for m in sorted(manifest)) + "\n",
    encoding='utf-8')
print(f"copied {len(manifest)} files; wrote {out}")
