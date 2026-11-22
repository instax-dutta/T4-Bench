## Purpose
Inkling-2-Mini results report: engine matrix, single-card throughput, the two-GPU split finding and vision.

## Ownership
- `docs/BENCHMARK-RESULTS.md` - measured throughput, VRAM, vision, engine verdicts and the no-split ceiling

## Local Contracts
- Every figure must match a row in `../results/inkling_results.csv`.
- The `-ngl 12` hybrid rows must never be presented as a two-GPU split; the report states the difference.
- Mark non-working engines as measured failures with the observed error, never as untested.

## Work Guidance
- Keep the verdict paragraph separate from the raw tables.

## Verification
- `node ../../../scripts/verify-doc.mjs docs/BENCHMARK-RESULTS.md 3000 5 llama.cpp t/s vision`

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
