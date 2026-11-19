## Purpose
Raw, source-cited research that grounds the MiniMax-H3-Image benchmark plan: model/hardware facts, quant catalogue, and inference-engine / low-VRAM methods.

## Ownership
- `research/model-hardware.md` - measured server facts, architecture, memory math, sm_75 constraints
- `research/quants.md` - quant variant catalogue and viability ranking
- `research/engines-lowvram.md` - engines and low-VRAM methods from GitHub, docs and forums
- `research/SYNTHESIS.md` - ranked synthesis of the three leaves

## Local Contracts
- Every factual claim carries a source URL or measured command output; no guesses.
- Weight sizes are stated in GiB using decimal-GB * 1e9 / 2^30, never mixed with GB silently.
- Each quant/engine verdict states whether it works on Compute Capability 7.5 (sm_75, Turing) and why.
- Non-viable options (NVFP4, MLX, RDNA4/ROCm-only, sm80+-only kernels) are marked non-viable with a reason.
- Research stays raw and evidence-first; recommendations live in `docs/`.

## Work Guidance
- Fetch the upstream HF repo, engine docs, GitHub issues and forum threads before asserting capabilities.
- Record exact commands and flags, not paraphrases, where a method is proposed.

## Verification
- `node scripts/verify-doc.mjs research/<file> <min-bytes> <min-urls> <markers...>`
- Leaf gates live in `.unlazy/bench-plan/gates/leaf-1.1.*.md`.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
