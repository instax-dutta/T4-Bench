## Purpose
Comparative report for Z-Image-Turbo, Qwen-Image 2.1 Viggle 4-step, SDXL and FLUX.2 klein 4B, including the claims-vs-measured check.

## Ownership
- `docs/BENCHMARK-RESULTS.md` - baseline and optimized latency, VRAM, CLIP quality and winner

## Local Contracts
- Every figure must trace to `benchmark/results.csv`, `benchmark/optimization-results.csv` or the server archive.
- State the engine, resolution, batch mode and prompt set when quoting a result.

## Work Guidance
- Keep the winner section separate from raw results so the evidence stays inspectable.

## Verification
- `node ../../scripts/verify-doc.mjs docs/BENCHMARK-RESULTS.md 5000 8 Throughput optimization winner dual CLIP`

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
