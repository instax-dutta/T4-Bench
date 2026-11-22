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

QUEUED benchmark of `lodestones/Kromoss` (MOSS-Image 5B DiT text-to-image,
Qwen3.5-9B text encoder, 8-step DMD2 turbo LoRA, int8 W8A8 ComfyUI variant)
on the Kaggle 2x Tesla T4 machine. Runs after the Inkling-2-Mini sweep
completes on the VM. No measured results yet.

## Ownership

- `tooling/bench_kromoss.py` - driver: diffusers warm-process configs
  (full pipe call wall time includes text encoding, since that is what a
  T4 user pays per image), ComfyUI headless route, CLIP ViT-L/14 scoring
- `tooling/sweep_kromoss.sh` - stage orchestrator; CSV mirrors to
  /kaggle/working after every row; disk_guard enforced

## Local Contracts

- Config set: K1 diffusers 50 steps CFG 3 (TE on CPU); K2 diffusers 8 steps
  CFG 1 + DMD2 LoRA (headline); K3 same with TE int8 on GPU 1 (documented
  fallback to CPU if bitsandbytes is unavailable on CUDA 13); K4 ComfyUI
  bf16 DiT; K5 ComfyUI int8_convrot W8A8 (the T4 int8-tensor-core config).
  Quality via CLIP ViT-L/14, the model card's own metric family
  (card reports 28.13 best on PartiPrompts).
- The 18 GB Qwen3.5-9B text encoder never goes on a single T4; it encodes
  on CPU (or GPU 1 as int8). The 5B DiT runs fp16 (bf16 -> fp16 cast: T4
  sm_75 has no native bfloat16). VAE stays fp32 per the model card.
- The int8_convrot quant is ComfyUI-format only (online Hadamard rotation,
  int8 attention selection); it is not loadable via diffusers - do not
  attempt it there.
- LoRA is applied unmerged via forward hooks per the model card; never
  merged into bf16 weights.
- Storage: diffusers set resident ~30 GB; ComfyUI single files streamed and
  deleted per config; peak ~60 GB against the ~96 GB overlay quota;
  `disk_guard` (25 GB free) and the /kaggle/working CSV mirror are
  mandatory, same as the inkling-2-mini project.
- Results land here as a report plus raw CSV, never merged into another
  project's CSV.

## Work Guidance

- On the VM, run only after the Inkling sweep finishes (GPU exclusivity:
  never two benches at once).
- Fixed prompts and seeds 42/123/999; 1024x1024; record encode time
  separately from generation wall time where the pipeline allows.
- License: Apache-2.0 with the LICENSE file present in the model repo.

## Verification

- `python3 -m py_compile tooling/bench_kromoss.py`
- `bash -n tooling/sweep_kromoss.sh`
- `node ../scripts/verify-dox.mjs ..` from this folder after structural changes.

## Child DOX Index

- No child AGENTS.md. `tooling/` is a plain folder; scripts there are
  self-describing and referenced from the sections above.
