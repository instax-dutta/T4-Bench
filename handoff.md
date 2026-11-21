# Handoff — LongCat-Video-Avatar-1.6 benchmark on GPU VM

## Status
**PENDING — ongoing work, resume later.** Updated 2026-11-21 after a full prep
session on a fresh VM. The run is blocked by VM storage, not by the model:
the writable overlay hit its ~96 GB quota mid-download and flipped read-only
(same failure mode as the old LTX-13B attempt), so a fresh VM session is
needed. Nothing has been measured yet. All resume tooling is preserved at
`benchmarks/longcat-video-avatar/tooling/` (decision 2026-11-21: keep the
work pending rather than record an unconfirmed verdict).

## Goal
Benchmark `meituan-longcat/LongCat-Video-Avatar-1.6` on **2× Tesla T4** and
determine feasibility (VRAM fit, throughput s/clip), then record results in
T4-Bench style under `benchmarks/video-generation/`.

## Feasibility expectation (2026-11-21 code audit — unconfirmed, needs phase 0)
**Likely infeasible, pending one cheap measured confirmation.** The original
assumption "13.6B DiT must span both GPUs" is wrong for this codebase:

- `--context_parallel_size=2` splits *activations* (`split_cp_2d` in
  `longcat_video/modules/avatar/longcat_video_dit_avatar.py`), **not weights**.
  Each rank holds the full DiT.
- INT8 DiT shards total **15,880,383,936 bytes = 14.78 GiB**, vs a T4's
  15360 MiB (15.0 GiB) minus CUDA context. The model core alone is ~98.5% of
  the card before whisper (~3.1 GiB fp16), VAE (~0.5 GiB), text encoder
  (11.35 GiB fp16 — must stay on CPU) or any activations.
- fp16 DiT (31.7 GB) and single-GPU INT8 are strictly worse.

The confirmation run (phase 0, ~15.9 GB download) loads the INT8 DiT on one
T4 and records peak VRAM / OOM into `int8_load_test.json`. If it OOMs —
document as a measured negative result in the video-generation report
(precedent: LTX-13B abandonment). If it fits — continue to the full sweep.

## VM access (Kaggle-style forwarded port)
```
sshpass -p 'kaggle' ssh \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  -p 9191 root@127.0.0.1
```
Use the multiplexed helper `vmssh` (local staging dir) — one ControlMaster
TCP connection reused for every command, so the tunnel/notebook is not
stressed and does not die mid-run. Long jobs always run under `nohup` on the
VM and are polled with short multiplexed calls.

## VM environment (verified 2026-11-21)
| Item | Value |
|---|---|
| GPUs | 2× Tesla T4, 15360 MiB each (sm_75 Turing) |
| Driver / CUDA | 580.178.04 / 13.0 |
| RAM / cgroup | 31 GiB (memory.max 32212254720) |
| CPU | 4 cores |
| Disk | overlay 8.0T total but **writable-layer quota ~96 GB**; `/kaggle/working` separate 20 GB loop; `/dev/shm` 14 GB |
| Python | 3.13.16, torch 2.11.0+cu130, diffusers 0.42.0, transformers 5.20.2 |
| xformers | 0.0.36 via `pip install xformers` (works; `flash_attn` does NOT build on CUDA 13) |
| nvidia-smi | needs `LD_LIBRARY_PATH=/usr/local/nvidia/lib64:/usr/local/cuda-13.0/lib64` |

**Quota lesson:** full both-repo download is ~112 GB (whisper ships ~15 GB of
fp32/bin/flax duplicates; base `dit/` 27 GB and `lora/` 5.4 GB are unused by
the avatar pipeline) and will kill any session at ~96 GB. Downloads must be
selective, with explicit file lists (`--include` is ignored by HF CLI 1.33 —
repo gotcha). `/kaggle/working` and `/dev/shm` stay writable after the overlay
dies, but are too small to salvage the weights.

## Code audit findings (2026-11-21, repo HEAD)
- `avatar-v1.6` is aliased to the `avatar-v1.5` path internally
  (`run_demo_avatar_single_audio_to_video.py` line 49).
- bfloat16 hardcodes live in exactly two files:
  `run_demo_avatar_single_audio_to_video.py`,
  `longcat_video/modules/quantization.py`.
- Checkpoint `config.json` pins `"enable_flashattn2": true` — must be flipped
  to xformers (flash-attn unbuildable on CUDA 13).
- The demo hardcodes `pipe.to(local_rank)` (puts the 11.35 GiB fp16 umT5 on
  each GPU); `WhisperModel.from_pretrained` defaults to fp32 (6.2 GiB).
- umT5-XXL encoder = 22.73 GB fp32 / 5 shards; pipeline encodes the prompt
  per segment via `_get_t5_prompt_embeds`, so a CPU text encoder works.

## Staged tooling (preserved in-repo at `benchmarks/longcat-video-avatar/tooling/`)
| File | Purpose |
|---|---|
| `prepare.sh` | phase0: INT8-only download (15.9 GB) + all patches + measured load test. phase1: rest of sweep weights (~32 GB). phase2: fp16 `base_model` for config C (31.7 GB). Idempotent, resumable. |
| `int8_load_test.py` | phase0 verdict: loads INT8 DiT, `.to(0)`, records OOM/peak VRAM to `int8_load_test.json` |
| `benchmark_avatar.py` | sweep driver, CSV schema `tag,resolution,segments,run,wall_s,exit_code,gpu0_peak_mib,gpu1_peak_mib,frames,duration_s,fps,video`, 1 Hz nvidia-smi sampling, ffprobe validation, warm-up runs recorded as run=0 |
| `vmssh` | multiplexed SSH helper (single ControlMaster connection) |

Patches applied by `prepare.sh` (document in the final report):
- P1 `torch.bfloat16 -> torch.float16` in the two audited files
- P2 whisper `torch_dtype="float16"`
- P3 text encoder stays on CPU; `_get_t5_prompt_embeds` encodes on CPU,
  moves embeds to device; `pipe.to(local_rank)` -> `pipe.vae.to(local_rank)`
- P4 checkpoint configs: `enable_flashattn2:false, enable_xformers:true`

## Sweep matrix (only if phase 0 fits)
| Config | Quant | GPUs | Resolution | Segments |
|---|---|---|---|---|
| A | `--use_int8` | 2 (ctx=2) | 480p | 1 | primary |
| B | `--use_int8` | 2 (ctx=2) | 720p | 1 | resolution ceiling |
| C | fp16 | 2 (ctx=2) | 480p | 1 | expect OOM (needs prepare phase2) |
| D | `--use_int8` | 1 | 480p | 1 | single GPU |
| E | `--use_int8` | 2 (ctx=2) | 480p | 3 | continuation |

Invocation: `python3 /workspace/benchmark_avatar.py <res> <segments> <runs> y y avatar-v1.6 [int8|fp16] [1|2] <tag>`.

## What to do next (on the fresh VM)
1. Restart the Kaggle VM, reconnect (port may change — check the tunnel).
2. Upload the four staged files to `/workspace/`.
3. `nohup bash /workspace/prepare.sh phase0 &` — poll `weights/logs/dl.log`.
4. Read `int8_load_test.json`:
   - OOM (expected) → the benchmark is done: record the measured negative
     result + all audit findings under `benchmarks/video-generation/`
     (new folder), update `docs/UNIFIED-INDEX.md`, `website` data, this file.
   - OK → `prepare.sh phase1`, run sweep A-E, save `benchmark_results.csv`
     and outputs back to the repo, update report/AGENTS chain.
