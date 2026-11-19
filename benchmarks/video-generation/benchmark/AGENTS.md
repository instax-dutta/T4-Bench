## Purpose
Measured video runs and archived MP4s, logs and quality scores.

## Ownership
- `benchmark/results.csv` - authoritative run table
- `benchmark/server-archive/**` - videos, logs, CLIP scores and runner scripts

## Local Contracts
- A run is not recorded without a valid MP4, wall time and peak VRAM.
- Keep abandoned attempts in the docs, not in the results CSV.

## Work Guidance
- Preserve the exact prompt with each clip; CLIP scores depend on it.

## Verification
- `node ../../scripts/verify-doc.mjs benchmark/results.csv 200 0 model_id frames wall_s peak_vram`

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
