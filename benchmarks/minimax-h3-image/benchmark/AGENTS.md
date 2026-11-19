## Purpose
Runnable benchmark assets and the results record format for the MiniMax-H3-Image runs on 2x T4.

## Ownership
- `benchmark/results-template.md` - the table and fields every measured run must fill
- `benchmark/results-summary.csv` - durable local copy of the raw measured runs (server originals are ephemeral)
- `benchmark/server-archive/**` - full local archive of server data: per-run metrics/PNGs/GPU logs, runner scripts and build/download logs under `working/`, and the original read-only-layer logs and scripts under `root/`
- Future run scripts and captured result files under `benchmark/`

## Local Contracts
- A run is not reported without: config id, quant, engine, seed, size, warmup count, latency samples, median latency, peak VRAM, and acceptance verdict.
- Peak VRAM is measured with `nvidia-smi`/`torch.cuda.max_memory_allocated`, not estimated.
- Results are appended, never overwritten; raw numbers are kept with their provenance.

## Work Guidance
- Keep the template copy-paste ready for the Kaggle SSH session.
- Do not invent measurements; leave pending fields blank until a real run fills them.

## Verification
- `node scripts/verify-doc.mjs benchmark/results-template.md 1200 0 Run ID median peak VRAM acceptance`

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
