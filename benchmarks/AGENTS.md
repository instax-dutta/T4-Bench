## Purpose
Hold the completed benchmark projects intact, sorted by subject, with their original contracts and data preserved, plus pending/queued staging folders and the clone-friendly media archive.

## Ownership
- `benchmarks/llm-and-training/**` - LLM inference, agent, long-context and fine-tuning campaigns on the same 2x T4 machine. Owned by its nested `AGENTS.md`.
- `benchmarks/minimax-h3-image/**` - MiniMax-H3-Image on 2x T4: quant/engine research, feasibility, benchmark plan, measured results and server archive. Owned by its nested `AGENTS.md`.
- `benchmarks/image-models/**` - Z-Image-Turbo, Qwen-Image 2.1 Viggle 4-step, SDXL and FLUX.2 klein 4B: baseline and throughput optimization. Owned by its nested `AGENTS.md`.
- `benchmarks/video-generation/**` - CogVideoX-2b, LTX 2B distilled and the abandoned LTX 13B attempt. Owned by its nested `AGENTS.md`.
- `benchmarks/media/**` - generated benchmark images and videos; stills are lossless WebP with a pixel-hash manifest. Owned by its nested `AGENTS.md`.
- `benchmarks/longcat-video-avatar/**` - PENDING: staged tooling and resume plan for LongCat-Video-Avatar-1.6 on 2x T4; paused on VM storage quota, no measured results yet. Owned by its nested `AGENTS.md`.
- `benchmarks/inkling-2-mini/**` - COMPLETED: Inkling-2-Mini engine-x-quant matrix (llama.cpp b12633 prebuilt is the only working engine; 22-26 tok/s single-card; no cross-GPU split; vision at 37.3 s per image chat). Owned by its nested `AGENTS.md`.
- `benchmarks/kromoss/**` - QUEUED: staged MOSS-Image 5B DiT sweep (diffusers 50-step and 8-step LoRA configs, ComfyUI bf16 and int8 W8A8); started 2026-11-22, aborted before first result when the VM session closed, to run on a future session. Owned by its nested `AGENTS.md`.

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
- `benchmarks/llm-and-training/AGENTS.md` - LLM, agent and training benchmarks
- `benchmarks/minimax-h3-image/AGENTS.md` - H3 quant/engine benchmark
- `benchmarks/image-models/AGENTS.md` - four image-generation models benchmark
- `benchmarks/video-generation/AGENTS.md` - video-generation benchmark
- `benchmarks/media/AGENTS.md` - clone-friendly lossless WebP media and pixel-hash manifest
- `benchmarks/longcat-video-avatar/AGENTS.md` - pending avatar benchmark: staged tooling, no results yet
- `benchmarks/inkling-2-mini/AGENTS.md` - completed Inkling-2-Mini engine-x-quant sweep: report, CSV and issue log
- `benchmarks/kromoss/AGENTS.md` - queued Kromoss image-model sweep: staged tooling, not yet run
