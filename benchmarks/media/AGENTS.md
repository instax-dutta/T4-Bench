## Purpose
Preserve generated benchmark images and videos in one deduplicated, compressed archive so clones stay small and extraction is optional.

## Ownership
- `benchmark-media.tar.gz.000`, `benchmark-media.tar.gz.001` - gzip tar split below GitHub's 100 MiB file limit; 112 logical media paths and 63 unique payloads (hardlink deduplication)
- `MANIFEST.json` - archive hash plus per-file hashes, sizes, dimensions and decoded RGBA SHA-256
- `extract.py` - archive verifier and extractor

## Local Contracts
- Do not commit loose media under `image-model-bench/`, `minimax-h3-bench/` or `video-gen-bench/`; they are ignored extraction outputs.
- Archived still images are lossless WebP. Decoded RGBA pixels are identical to the original PNG benchmark outputs.
- Keep `benchmark-media.tar.gz.*` and `MANIFEST.json` current whenever media is added or replaced.
- Original benchmark CSVs, reports and server logs remain the authoritative measurements; media is evidence, not a second results table.

## Work Guidance
- Verify without extracting: `python3 benchmarks/media/extract.py --check`
- Extract the original tree: `python3 benchmarks/media/extract.py`
- Build new archives with hardlink deduplication before tar/gzip; repeated seeded outputs are common.

## Verification
- `python3 benchmarks/media/extract.py --check`
- `python3 benchmarks/media/extract.py` in a temporary checkout, then confirm every manifest hash.
- `git fsck --full --no-progress`

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
