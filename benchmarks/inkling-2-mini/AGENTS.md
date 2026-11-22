# DOX framework

- DOX is highly performant AGENTS.md hierarchy installed here
- Agent must follow DOX instructions across any edits

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it

## Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Purpose

COMPLETED 2026-11-22: full engine x quant benchmark of
`thinkingmachines/Inkling-2-Mini` (26.4B MoE, 3.4B active, looped
transformer, multimodal) on the Kaggle 2x Tesla T4 machine. llama.cpp
b12633 (CUDA 12.8 prebuilt) is the only working engine: 22-26 t/s
single-card generation on quants up to 12.7 GiB, vision at 37.3 s per
image chat, no cross-GPU split exists for the 4-bit tiers. Results in
`docs/BENCHMARK-RESULTS.md`, raw CSV in `results/`, session issue log
in `tooling/ISSUES.md`.

## Ownership

- `docs/BENCHMARK-RESULTS.md` - authoritative report (owned by `docs/AGENTS.md`)
- `results/inkling_results.csv` - raw rows for every measurement
- `results/logs/` - llama-bench tables, attempt logs, vision logs and the recorded image-chat response
- `tooling/bench_inkling.py` - driver: llama-bench wrapper with 1 Hz
  nvidia-smi peak sampling, Ollama /api/generate pass, vision end-to-end
  pass, and attempt-engine rows; CSV schema in the file header
- `tooling/sweep_inkling.sh` - full matrix orchestrator; quota-aware
  (downloads each quant, benches every engine that can use it, deletes
  before the next; peak disk ~24 GB)
- `tooling/ISSUES.md` - session issue log: every failure, its cause and
  the fix that unblocked it
- `tooling/ollama_import.sh` - local GGUF import for same-file engine
  comparison
- `tooling/transformers_attempt.py` - native-checkpoint failure row
- Root `handoff.md` links: none for this project

## Local Contracts

- Matrix scope: llama.cpp (>= b12600 merged loop arch, PR #32694 layout
  only) across UD-IQ1_M / AD-IQ2_M / UD-Q2_K_XL / UD-IQ3_XXS / AD-IQ3_S /
  UD-Q3_K_XL on 1 GPU and AD-Q4_K / UD-Q4_K_M / UD-Q4_K_XL / UD-Q8_K_XL
  on 2 GPUs (`--tensor-split 1,1`); Ollama official tag plus two local
  imports; vision via mmproj-F16; vLLM, SGLang and transformers-native as
  documented attempt rows. Engines that are GUI-only wrappers (LM Studio,
  Jan, Lemonade, Unsloth Desktop) are out of scope, stated in the report.
- Every row records: engine, quant, gpus, ctx, run, throughput, load time,
  wall time, exit code and per-GPU peak VRAM. Fixed prompt, seed 42,
  temperature 0, capped output tokens (the model's reasoning cannot fully
  disable).
- Native NVFP4/MXFP8 checkpoint is arithmetic-infeasible on T4 (dequant
  ~53 GB bf16 vs 15 GB VRAM / 31 GB RAM; card recommends 32 GB+); recorded
  as an attempt row, never as a measured throughput.
- Total quant downloads (~139 GB) exceed the ~96 GB writable-layer quota
  (verified 2026-11-21: the overlay flips read-only and kills every write,
  including result CSVs). Three mandatory mitigations, all built into the
  staged scripts: (1) download-bench-delete lifecycle, one quant file on
  disk at a time; (2) the results CSV mirrors to /kaggle/working (separate
  20 GB loop, stays writable after overlay death) after every row; (3)
  `disk_guard` before every big write - require 25 GB free on /, reclaim
  HF/xet chunk caches, pip caches and Ollama blobs first, abort loudly
  rather than die mid-bench. Ollama blob copies are removed after each
  bench (`ollama rm`), and vLLM/SGLang are pip-uninstalled after their
  attempt rows.
- Results land here as a report plus raw CSV, never merged into another
  project's CSV.

## Work Guidance

- On a fresh VM: upload `tooling/` to `/workspace/`, then
  `nohup bash /workspace/sweep_inkling.sh &` and poll
  `weights/inkling_results.csv` with short multiplexed SSH calls
  (same `vmssh` approach as the longcat-video-avatar project).
- The AtomicChat uncensored rows (AD-* quants) are the user's intended
  Kaggle-T4 workload; give them their own verdict paragraph in the report.
- Licenses: base model Apache-2.0 (card-declared, no LICENSE file in the
  thinkingmachines repo); unsloth and AtomicChat GGUF repos are Apache-2.0,
  AtomicChat carries the LICENSE file. Cite licenses in the report.

## Verification

- `python3 -m py_compile tooling/bench_inkling.py tooling/transformers_attempt.py`
- `bash -n tooling/sweep_inkling.sh tooling/ollama_import.sh`
- `node ../scripts/verify-dox.mjs ..` from this folder after structural changes.

## Child DOX Index

- `docs/AGENTS.md` - measured results report
- `tooling/`, `results/` - plain folders; files there are self-describing
  and referenced from the sections above.
