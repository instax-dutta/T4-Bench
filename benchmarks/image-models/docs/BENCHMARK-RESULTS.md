# Four image-generation models on 2x Kaggle T4: measured results

Date: 2026-11-18 (UTC). This is a **separate project** from `minimax-h3-bench`;
no H3 data or conclusions are mixed in here.

Canonical model IDs used in `benchmark/results.csv`: `z-image-turbo`,
`qwen-image-2.1-viggle-4step`, `sdxl`, `flux2-klein-4b`.

## Protocol (identical for all four models)

- Server: 2x NVIDIA Tesla T4, 15360 MiB each (sm_75, Turing), 31 GiB RAM,
  4 vCPU, CUDA 13.0 / driver 580.178.04.
- Engine: one binary for all four, `stable-diffusion.cpp` built from source
  with CUDA and `-DCMAKE_CUDA_ARCHITECTURES=75`. This avoids engine-specific
  confounds: every difference below is model/quant/VAE/text-encoder, not runtime.
- Workload: 1024x1024, prompt "A silver tabby kitten holding a sign reading
  'sd.cpp', natural daylight", fixed seeds 42/123/999, one cold process per run,
  Euler sampler, `--offload-to-cpu --vae-tiling --max-vram 12`.
- Each model uses its own published step count and guidance: Z-Image-Turbo 8 /
  CFG 1.0, Qwen-Image-2.1 Viggle 4-step 4 / CFG 1.0, FLUX.2 klein 4B 4 / CFG
  1.0, SDXL 30 / CFG 7.0. Defaults differ from the H3 benchmark deliberately.
- Measurement: 1 Hz `nvidia-smi` CSV plus wall clock; wall time includes model
  load, text encoding, sampling and VAE decode. Determinism was checked with a
  repeated seed 42 for Z-Image, FLUX and SDXL (byte-identical PNG SHA256 for
  all three). Qwen weights were freed before the repeat step, so its
  determinism was not retested here.
- Raw data: `benchmark/results.csv`, full server archive in
  `benchmark/server-archive/` (per-run logs, PNGs, GPU CSVs and scripts).

## Measured latency and VRAM

| Model | Quant / components | Steps | Median latency (s) | Images/hr | Peak VRAM |
|---|---|---|---|---|---|
| FLUX.2 klein 4B | leejet Q4_0 DiT + Qwen3-4B Q4_K_M TE + flux2 VAE | 4 | **23.7** | 151.9 | 3677 MiB (3.59 GiB) |
| Z-Image-Turbo | leejet Q4_K DiT + Qwen3-4B Q4_K_M TE + ae VAE | 8 | **47.6** | 75.6 | 4651 MiB (4.54 GiB) |
| Qwen-Image 2.1 Viggle 4-step | Abiray Q4_K_M DiT + Qwen3-VL-8B Q4_K_M TE + Qwen VAE | 4 | **64.0** | 56.2 | 5867 MiB (5.73 GiB) |
| SDXL 1.0 base | stabilityai fp16 checkpoint + sdxl-vae-fp16-fix | 30 | **63.5** | 56.7 | 7313 MiB (7.14 GiB) |

All 15 runs exited 0, produced 1024x1024 PNGs, and were non-empty by pixel
statistics. Where applicable the Qwen outputs were RGBA with an alpha channel
(~254.6 mean), consistent with that model's transparency feature.

## Claims vs measured

The following claims came from the model shortlist that prompted this sweep.
They are checked against the numbers above, not repeated as facts.

| Claim | Measured | Verdict |
|---|---|---|
| Z-Image-Turbo: "16 GB VRAM native, fits single T4" | 4.54 GiB peak | True and very conservative; a Q4_K DiT plus a 4B encoder fits with ~10 GB to spare |
| Z-Image-Turbo: "~seconds to tens of seconds per 1024x1024 on T4" | 47.6 s median | Within the stated range, at the slow end |
| Qwen-Image 2.1 + Viggle 4-step: "~23-30 s per image on 2x T4" | 64.0 s median | **Not reproduced.** The 4-step DiT is fast, but the 8B text encoder and a 15.9 s VAE decode dominate |
| Qwen-Image 2.1: "INT8 DiT + W4A8 Qwen3-VL encoder" | Q4_K_M GGUF DiT + Q4_K_M 8B encoder | Different quant stack: GGUF was used because the engine is sd.cpp; the claim is about a ComfyUI stack |
| SDXL: "~15-20 s/image" | 63.5 s at 30 steps | **Not reproduced** with the base fp16 checkpoint; Turbo/Lightning variants were not part of this sweep |
| FLUX.2 klein 4B: "fastest raw, 4 steps, runs on 2x T4" | 23.7 s median, 3.59 GiB | Confirmed: fastest and lightest of the four |
| FLUX.2 klein: "1920x1088" | only 1024x1024 measured | Untested; no claim made about that resolution |
| "2x T4 (16 GB VRAM each)" | 15360 MiB per card | Minor correction: 15 GiB, not 16 |
| Z-Image "Apache 2.0-ish" | `license:apache-2.0` on Tongyi-MAI/Z-Image-Turbo | Confirmed |
| FLUX.2 klein "Apache 2.0" | `license:apache-2.0` on black-forest-labs/FLUX.2-klein-4B | Confirmed |
| SDXL "OpenRAIL++-M, commercial OK" | `license:openrail++` | Confirmed as tagged; read the full license for commercial terms |
| Qwen/Viggle licence | `license:other` on both Qwen/Qwen-Image-2.1 and Viggle/Qwen-Image-2.1-viggle-turbo | Research/non-commercial terms; do not assume commercial use |

## Interpretation

For this exact hardware and a single-image, cold-process latency metric, the
ranking is FLUX.2 klein 4B, then Z-Image-Turbo, then a near-tie between SDXL and
Qwen Viggle 4-step. Step count alone does not predict latency: the 4-step Qwen
model is slower than the 8-step Z-Image model because text encoding and VAE
decode are fixed costs that dominate short samplers. SDXL's ecosystem advantage
(LoRAs) is real but does not appear in these numbers.

The engine choice was held constant, so these are not absolute best-in-class
numbers for each model. A ComfyUI stack with INT8/W4A8 encoders, a warmed
process, batched requests, or a different resolution could change the ranking.
In particular the user's 23-30 s figure for Qwen may be achievable in a warm
ComfyUI server; this sweep measures cold, one-image-at-a-time latency.

## Throughput optimization (second pass)

Baseline numbers above are cold, one-image-per-process. Two levers were then
applied to every model, keeping the same engine, prompt, resolution, steps and
seed: (1) `--batch-count 4` in one process, amortizing load and text encoding;
(2) two processes with `CUDA_VISIBLE_DEVICES=0` and `=1`, each generating two
images, so both T4s work in parallel. Full data: `benchmark/optimization-results.csv`.

| Model | Cold 1 image | Batch 4, one GPU | 2 images x 2 GPUs | Best throughput |
|---|---|---|---|---|
| FLUX.2 klein 4B | 23.7 s (152/hr) | 86.3 s / 4 (167/hr) | **41.3 s / 4** | **349 img/hr** |
| Qwen-Image 2.1 Viggle 4-step | 64.0 s (56/hr) | 160.2 s / 4 (90/hr) | **96.1 s / 4** | **150 img/hr** |
| Z-Image-Turbo | 47.6 s (76/hr) | 178.0 s / 4 (81/hr) | **97.7 s / 4** | **147 img/hr** |
| SDXL 1.0 base | 63.5 s (57/hr) | 248.7 s / 4 (58/hr) | **134.8 s / 4** | **107 img/hr** |

Pushing batch size further on FLUX gave 197 img/hr (batch 8 on one GPU, 146.3 s
for 8 images) and the best observed configuration overall: **374 img/hr** with
batch 4 per GPU on both cards (77.0 s for 8 images). Dual-GPU execution gives
1.8-2.0x over a single GPU. Batching alone helps
little for SDXL/Z-Image because sampling dominates; it helps FLUX/Qwen because
their text encoders are a larger share of a short 4-step run. Peak VRAM per GPU
was unchanged by batching (3.67 GiB FLUX, 4.65 GiB Z-Image, 5.87 GiB Qwen,
7.14 GiB SDXL), and both cards were used simultaneously in the dual setup.

The earlier one-GPU tests are therefore not the maximum throughput this server
can deliver. The best measured configuration for every model is the dual-GPU
one, and the winner on throughput is FLUX.2 klein 4B by a wide margin.

## Quality measurement

Quality was proxied by CLIP (openai/clip-vit-base-patch32) cosine similarity
between each generated image and the exact prompt used for it, including two
extra prompts (photorealistic fox; neon text-rendering sign). Raw scores:
`benchmark/server-archive/results/clip_by_prompt.json`. Scorer:
`benchmark/server-archive/score_by_prompt.py`.

| Model | Images scored | Mean CLIP cosine | Min | Max |
|---|---|---|---|---|
| FLUX.2 klein 4B | 14 | **0.3924** | 0.3490 | 0.4083 |
| SDXL 1.0 base | 14 | 0.3894 | 0.3545 | 0.4108 |
| Qwen-Image 2.1 Viggle 4-step | 11 | 0.3839 | 0.3776 | 0.3922 |
| Z-Image-Turbo | 12 | 0.3814 | 0.3751 | 0.3902 |

On the two extra prompts FLUX scored 0.349 / 0.382 and SDXL 0.355 / 0.370, so
the quality lead is small and prompt-dependent. CLIP measures prompt alignment,
not aesthetics, realism or historical accuracy; the user's claim that FLUX has
weaker historical accuracy was not tested and remains unverified.

## Winner: best of both

**FLUX.2 klein 4B** is the best model on this 2x T4 under the measured criteria:
highest throughput (374 images/hour with both GPUs at batch 4 each) and highest mean CLIP
alignment (0.3924). SDXL is a close second on quality (0.3894) but runs at only
107 images/hour, less than a third of FLUX. Z-Image and Qwen are slower and
score lower on this prompt set. The decision is evidence-based only for the
prompts, quant levels, 1024x1024 resolution and cold-process protocol measured
here.

## Sources
- https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
- https://huggingface.co/leejet/Z-Image-Turbo-GGUF
- https://huggingface.co/Abiray/Qwen-Image-2.1-viggle-4-steps-turbo-GGUF
- https://huggingface.co/Viggle/Qwen-Image-2.1-viggle-turbo
- https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- https://huggingface.co/black-forest-labs/FLUX.2-klein-4B
- https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/models/z_image.md
- https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/models/qwen_image_2.1.md
- https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/models/flux2.md
- https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/models/sd.md
