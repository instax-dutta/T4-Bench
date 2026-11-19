## Purpose
Authoritative raw measurements and archived server artifacts for the four-image-model sweep.

## Ownership
- `benchmark/results.csv` - 15 measured runs across four models
- `benchmark/optimization-results.csv` - baseline, batch and dual-GPU throughput rows
- `benchmark/server-archive/**` - per-run PNGs, logs, CLIP scores and runner scripts

## Local Contracts
- Never overwrite a measured row; append or archive instead.
- Keep the local archive checksum-identical to the server originals when the session is live.

## Work Guidance
- Use the same prompt, resolution and seed set when adding a comparison run.

## Verification
- `node ../../scripts/verify-sweep.mjs 3` from the project root.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
