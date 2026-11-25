# Local data archived into this repository

Generated on 2026-11-19; storage normalized on 2026-11-25. This repository keeps benchmark media in one optional-extraction archive instead of a loose media tree.

## Archive

- `benchmarks/media/benchmark-media.tar.gz.*` - 121,535,569 bytes total (116 MiB) in two parts (80 MiB + 36 MiB)
- 112 logical media paths, deduplicated to 63 unique payloads with tar hardlinks
- 104 lossless WebP stills and 8 MP4 videos
- Decoded WebP pixels are identical to the original PNG benchmark outputs
- `benchmarks/media/MANIFEST.json` records the archive hash and every file's hash, size, dimensions and decoded RGBA SHA-256

## Extract when needed

```bash
python3 benchmarks/media/extract.py --check   # verify only
python3 benchmarks/media/extract.py           # extract the original tree
```

Extraction recreates `benchmarks/media/image-model-bench/`, `benchmarks/media/minimax-h3-bench/` and `benchmarks/media/video-gen-bench/`. Those directories are ignored by Git.

ZIP archives from the old project folders were not copied; they were snapshots of files already present here.
