## Purpose
Hold the three completed benchmark projects intact, sorted by subject, with their original contracts and data preserved.

## Ownership
- `benchmarks/minimax-h3-image/**` - MiniMax-H3-Image on 2x T4: quant/engine research, feasibility, benchmark plan, measured results and server archive. Owned by its nested `AGENTS.md`.
- `benchmarks/image-models/**` - Z-Image-Turbo, Qwen-Image 2.1 Viggle 4-step, SDXL and FLUX.2 klein 4B: baseline and throughput optimization. Owned by its nested `AGENTS.md`.
- `benchmarks/video-generation/**` - CogVideoX-2b, LTX 2B distilled and the abandoned LTX 13B attempt. Owned by its nested `AGENTS.md`.

## Local Contracts
- Do not edit files inside a project without first reading that project's AGENTS.md chain.
- Never merge results from different projects into one CSV; each project keeps its own authoritative table.
- All numbers in the cross-project index must cite the owning project's report and row.

## Work Guidance
- When comparing models, state the metric and protocol; CLIP scores from different prompt sets are not directly comparable.
- Treat nested gate ledgers as the completion record for each project.

## Verification
- From this folder: `node ../scripts/verify-dox.mjs ..` after any structural change.
- Each nested project has its own unlazy ledger and verification scripts.

## Child DOX Index
- `benchmarks/minimax-h3-image/AGENTS.md` - H3 quant/engine benchmark
- `benchmarks/image-models/AGENTS.md` - four image-generation models benchmark
- `benchmarks/video-generation/AGENTS.md` - video-generation benchmark
