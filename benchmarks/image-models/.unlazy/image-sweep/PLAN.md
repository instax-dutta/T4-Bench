# PLAN: four image-generation models on 2x Kaggle T4

Scope id: `image-sweep`. Contract revision: 1.
This is a NEW project, separate from `minimax-h3-bench`. No H3 data is touched.
Server data lives in `/kaggle/working/quadbench`, never in the H3 `bench/` tree.

## Contract inventory

| Id | Required outcome | Owner | Observation | Disposition |
|---|---|---|---|---|
| S1 | Z-Image-Turbo measured | runner | >=3 successful runs in results.csv | required |
| S2 | Qwen-Image-2.1 Viggle 4-step measured | runner | >=3 successful runs | required |
| S3 | SDXL measured | runner | >=3 successful runs | required |
| S4 | FLUX.2 klein 4B measured | runner | >=3 successful runs | required |
| S5 | Same engine/prompt/seed/size methodology across all four | report | report documents shared protocol | required |
| S6 | Comparative report with sources and verdicts | docs/BENCHMARK-RESULTS.md | verify-sweep.mjs | required |
| S7 | Original claims from the user checked against measurements | report | report has a claims-vs-measured table | required |

## Method contract
- One engine: stable-diffusion.cpp (already built with CUDA sm_75 on the server).
- Same prompt, seed set, resolution (1024x1024), warmup policy, and measurement
  wrapper (1 Hz nvidia-smi + wall clock) for every model.
- Each model uses its published step count and CFG; deviations are recorded.
- Peak VRAM, latency, determinism (one repeated seed), and image validity are
  captured per run. Server-side raw data is archived locally after each model.

## Ledgers
- root: `.unlazy/image-sweep/GATES.md`
- no sub-leaves: this is a single sequential execution line, not a fan-out.
