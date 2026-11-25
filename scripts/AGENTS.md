## Purpose
Repository-owned verification oracles copied from the benchmark projects so the unified tree can be checked without reaching into nested folders.

## Ownership
- `scripts/verify-doc.mjs` - artifact size, URL count and marker checks
- `scripts/verify-dox.mjs` - DOX structure check for this root
- `scripts/verify-math.mjs` - model weight-memory recomputation
- `scripts/verify-sweep.mjs` - four-model sweep result check
- `scripts/archive_local_data.py` - rebuild the deduplicated benchmark media archive and manifest from sibling source folders

## Local Contracts
- Verification oracles are Node ESM, standard library only, no network, no writes.
- `archive_local_data.py` is the explicit exception: it writes the media archive and inventory, requires Pillow and cwebp, and reads only sibling benchmark source folders.
- Exit 0 only after all assertions pass, printing a success-only marker.
- Keep these oracles portable; nested projects keep their own copies.

## Work Guidance
- Use `node scripts/verify-dox.mjs .` from the unified root for structural checks.

## Verification
- Negative control: `node scripts/verify-math.mjs /dev/null` must fail.
- `node scripts/verify-doc.mjs docs/UNIFIED-INDEX.md 1000 3 benchmarks winner metric` after index edits.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
