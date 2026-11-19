# Video generation benchmark on Kaggle 2x T4

Date: 2026-11-19 UTC. Source plan: `/Users/saiduttaabhishekdash/Downloads/video-gen-plan.md`.
This is a separate project from the H3 and image-model benchmarks.

## Server and method

Measured live: 2x Tesla T4 (15360 MiB each, sm_75, driver 580.178.04), 31 GiB
RAM, 4 vCPU, CUDA 13, torch 2.11.0+cu130, diffusers 0.42.0, transformers 5.20.2,
ffmpeg present. `/kaggle/working` is a 20 GB writable loop; `/root` was writable
at first and later became read-only.

Common protocol: one English prompt describing a tabby kitten walking across a
sunlit table while holding a sign, fixed seed 42 (plus 123/999 in warm runs),
cold process unless marked warm, 1 Hz `nvidia-smi` VRAM sampling, wall clock
covering load + generation + VAE decode + MP4 export, and output validation with
ffprobe / frame extraction. Quality proxy: CLIP ViT-B/32 cosine similarity
between the exact prompt and the first decoded frame.

## Measured results

| Model | Config | Wall (s) | Frames | Peak VRAM | CLIP cosine |
|---|---|---|---|---|---|
| CogVideoX-2b (THUDM) | 50 steps, 720x480, 49f, model CPU offload | 1053.0 | 49 | 11301 MiB | **0.2645** |
| LTX-Video 2B 0.9.8 distilled | 8 steps, 768x512, 121f, cold | 131.4 | 121 | 11032 MiB | 0.2329 |
| LTX-Video 2B 0.9.8 distilled | 8 steps, 768x512, 121f, warm 3 clips | 270.4 total (90.1/clip) | 3x121 | 11033 MiB | 0.234 / 0.228 / 0.141 |
| LTX-Video 2B 0.9.8 distilled | 4 steps, 768x512, 49f, warm 3 clips | 207.7 total (69.2/clip, 27.4 after first) | 3x49 | 11033 MiB | 0.231 / 0.215 / 0.196 |

All runs exited 0 and produced valid MP4s (CogVideoX 720x480, 49 frames, 8 fps;
LTX 768x512, 121 or 49 frames, 24 fps). Raw data: `benchmark/results.csv`,
logs and videos in `benchmark/server-archive/`.

## Throughput optimization

- CogVideoX-2b: dominated by 50 sampling steps at ~19.7 s/step. Model load was
  only ~8 s, so warm-process reuse saves little. 2.14 generated frames/min.
- LTX 2B distilled: load cost ~100 s, sampling ~28 s for 8 steps at 121 frames.
  Loading once and generating three clips cut effective latency from 131 s to
  ~90 s per clip; dropping to 4 steps and 49 frames cut the steady-state clip
  to ~27 s (first clip still 51.5 s). That is about 4.9x the CogVideoX frame
  rate (1.79 vs 0.047 generated frames/second).
- Two concurrent LTX processes (one per GPU) were attempted and failed: both
  fell onto GPU 0 because `CUDA_VISIBLE_DEVICES` was initially applied only to
  the sampler; after fixing that, both processes were OOM-killed because each
  needs ~20 GB of host RAM and two copies exceed 31 GiB. So the second GPU does
  not help this 2B model unless the model is explicitly sharded, which the
  plan only recommends for the 13B case.

## Best of both

**LTX-Video 2B 0.9.8 distilled is the practical winner on this server**: 27 s
per warm 49-frame clip at 4 steps (or 90 s per 121-frame clip at 8 steps) with
~11 GiB VRAM and CLIP 0.215-0.234. **CogVideoX-2b wins raw prompt alignment**
(0.2645) but needs 1053 s for the same 49 frames, roughly 38x slower. If the
priority is a single best-looking clip and time is not constrained, use
CogVideoX; for maximum throughput with acceptable quality, use warm-process
LTX 2B distilled.

## Items from the plan that were not completed

| Plan item | Status | Evidence |
|---|---|---|
| LTX-Video 13B Distilled NF4 (rank 1) | ABANDONED | Downloaded 57 GB of ~93 GB before the container's writable layer became read-only (`Read-only file system` errors in `logs/dl_ltx13b.log`). The remaining space could not be freed because `/root` was read-only. |
| WanGP multi-model launcher | Not benchmarked | It is an interactive Gradio launcher requiring a kernel restart and manual model selection, not a single reproducible generation call; no measured numbers were produced. |
| Audio (AudioLDM2 / Kokoro) | Out of scope | The user asked for video generation models; audio was not benchmarked. |

## Gotchas and fixes
- `hf download --include` was ignored by HF CLI 1.33.0, so the LTX transformer
  was missing; fixed by naming each file explicitly.
- `CUDA_VISIBLE_DEVICES` applied only to `nvidia-smi` sent both LTX processes
  to GPU 0; fixed in the script, after which host RAM OOM remained.
- `PIL.ImageStat.Stat` has `.stddev`, not `.std`; the metric writer crashed
  after CogVideoX generation, so metrics were reconstructed from the saved
  progress log and GPU CSV.
- The writable root layer hit its quota at ~97 GB of models (13 GB CogVideoX +
  27 GB LTX 2B + 57 GB partial LTX 13B). All subsequent data went to
  `/kaggle/working`.

## Sources
- https://github.com/DamnKuldeep/ltxv-13b-distilled-free-gpu-pipeline
- https://huggingface.co/Lightricks/LTX-Video-0.9.8-13B-distilled
- https://huggingface.co/jbilcke-hf/LTX-Video-2b-0-9-8-distilled-HFIE
- https://huggingface.co/THUDM/CogVideoX-2b
- https://huggingface.co/docs/diffusers/main/en/using-diffusers/text-img2vid
- https://github.com/kayas881/WanGP-Kaggle
- https://github.com/alirezayaned/AI-Video-Generation
