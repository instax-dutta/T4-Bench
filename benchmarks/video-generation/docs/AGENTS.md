## Purpose
Video benchmark report: CogVideoX-2b, LTX 2B distilled, throughput optimization and abandoned LTX 13B.

## Ownership
- `docs/BENCHMARK-RESULTS.md` - measured latency, VRAM, CLIP scores, winners and gaps

## Local Contracts
- Mark uncompleted plan items explicitly; never promote an attempted run into a measured result.
- Quote the exact config (steps, frames, size, warm/cold) with every latency.

## Work Guidance
- Keep the best-of-both verdict separate from the raw table.

## Verification
- `node ../../scripts/verify-doc.mjs docs/BENCHMARK-RESULTS.md 3000 5 measured latency VRAM models`

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
