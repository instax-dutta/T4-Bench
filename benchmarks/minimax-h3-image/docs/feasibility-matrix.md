# Feasibility matrix: MiniMax-H3-Image on the measured Kaggle 2x T4 server

Server (measured over SSH 2026-11-18): 2x NVIDIA Tesla T4, 15360 MiB each
(30 GiB aggregate, **not** unified, no NVLink), Compute Capability 7.5 / sm_75,
4 vCPU Xeon @2.0GHz, 31 GiB RAM (0 swap, ~29 GiB available), CUDA 13.0,
driver 580.178.04, torch 2.11.0+cu130, Python 3.13, ~967 GB free disk.
Evidence and sources: `research/model-hardware.md`, `research/quants.md`,
`research/engines-lowvram.md`, `research/SYNTHESIS.md`.

## 1. Memory feasibility (weights only, GiB = decimal GB * 1e9 / 2^30)

| Configuration | DiT | Text encoder | VAE | Total | Fits 30 GiB VRAM? | Fits ~29 GiB RAM? |
|---|---|---|---|---|---|---|
| All BF16 | 61.7 | 62.1 | 2.2 | 126.0 | no | no |
| All FP8 | 30.9 GiB | 31.1 GiB | 2.2 GiB | 64.1 GiB | no | no |
| All 4-bit | 15.4 | 15.5 | 2.2 | 33.1 | no (and activations extra) | no |
| FP8 DiT + 4-bit text encoder | 30.9 | 15.5 | 2.2 | 48.6 | no | no |
| DiT-only GGUF Q4_K_M + 3bpp TE | ~10.8 | ~7.1 | 1.1 | ~19 | yes, across devices | yes |
| EntroPack 3bpp DiT + 3bpp TE | 7.14 | ~7.1 | 1.1 | ~15 | yes | yes |

Two decisive facts: (1) the smallest full-precision-equivalent pipeline,
33.1 GiB at 4-bit, still exceeds both VRAM and host RAM before activations;
(2) at 4096x4096 the packed sequence is roughly 20k tokens, so saved
activations and the FP32 VAE decode cost several additional GiB. Any viable
configuration must quantize **both** the DiT and the text encoder and stream
components between disk, CPU, and the two GPUs.

## 2. Kernel feasibility on sm_75

Turing has FP16 and INT8 tensor cores only. Non-viable on this server:
native BF16 (sm_80+), FP8 tensor-core GEMM and Marlin FP8 (sm_89/sm_90+),
Marlin INT4 (sm_80+), FlashAttention-2 (sm_80+; not installed), NVFP4/FP4
(Blackwell), MLX (Apple), RDNA4/ROCmFPX (AMD). What executes: generic FP16 /
FP32 cuBLAS and torch, INT8 tensor-core paths (int8_convrot, W4A8 DP4A-style
math), bnb NF4 and torchao int8 weight-only (dequantize to FP16 for the GEMM),
and ggml CUDA kernels for GGUF (dequantize to FP16, host-RAM streaming).

Therefore the benchmark is a **dequantize-to-FP16, low-VRAM** study. FP8 is
stored but emulated (slower); it is retained only as a fidelity reference.

## 3. Quant x engine matrix

Legend: FIT = plausible at reduced resolution with tuning; RISK = fits on
paper, unverified on sm_75; NO = excluded with reason.

| Id | Quant artifact | Engine / loader | GPU plan | Resolution target | sm75 | Verdict |
|---|---|---|---|---|---|---|
| A | DiffSynth EntroPack 3bpp DiT + 3bpp TE | DiffSynth-Studio, `vram_limit`, tiled VAE | DiT GPU0, TE disk/CPU stream | 1024 -> 2048 | yes (FP16 compute) | FIT (primary) |
| A2 | DiffSynth INT8 ConvRot DiT + int8 TE | DiffSynth-Studio, disk offload | DiT GPU0, TE disk stream | 2048 | yes (INT8 cores) | FIT |
| B | unsloth GGUF UD-Q4_K_XL (13.61 GB, LPIPS 0.172) | stable-diffusion.cpp `sd-cli`, `--max-vram 12` | DiT GPU0, TE streamed from RAM | 1024 -> 2048 | yes (ggml CUDA) | FIT (primary) |
| B2 | unsloth GGUF Q3_K_M (10.42 GB, LPIPS 0.271) | stable-diffusion.cpp / ComfyUI-GGUF | DiT GPU0, TE streamed | 2048 -> 4096 with tiling | yes | FIT (headroom) |
| C | Abiray GGUF Q4_K_M (11.57 GB) | ComfyUI-GGUF, `--lowvram` / block swap | DiT GPU0, TE GPU1 or RAM | 1024 -> 2048 | yes | FIT (control) |
| C2 | Comfy-Org W4A8 DiT (14.88 GiB) + quantized TE | ComfyUI, `--lowvram --reserve-vram 1.5` | DiT GPU0, TE streamed | <=2048 | INT8 yes | RISK (tight) |
| D | unsloth FP8-INT8-ConvRot (20.27 GB, LPIPS 0.140) | ComfyUI, streamed | DiT GPU0 streamed, TE RAM | 1024 -> 2048 | emulated | RISK (quality reference) |
| E | SD-Next SDNQ uint4 (DiT 19.7 GB, TE 21.8 GB) | SD.Next / diffusers ModularPipeline | offload both | 1024 | dequant to FP16 | RISK (experimental) |
| F | diffusers + bnb NF4 / torchao int8 | diffusers ModularPipeline, sequential CPU offload | offload both | 1024 -> 2048 | yes | FIT (API reference) |
| - | SGLang / vLLM-Omni FP8-Marlin | official serving | multi-GPU | any | no (sm80+, NVLink) | NO |
| - | NVFP4 / MLX / ROCmFPX / RDNA4 | platform-specific | n/a | any | no | NO |

## 4. Selected stack (what the benchmark actually measures)

Primary: **Track A** (DiffSynth-Studio + EntroPack 3bpp) and **Track B**
(unsloth GGUF UD-Q4_K_XL via `stable-diffusion.cpp`) answer the two decisive
questions: smallest official footprint and most reliable Turing-native loader.
Controls: Track C (ComfyUI-GGUF, community ecosystem) and Track F (diffusers
weight-only quant) isolate engine effects. Track D is the fidelity ceiling.

Resolution ladder, applied identically to every track:
1. **1024x1024** smoke tier - correctness, throughput ceiling, lowest memory.
2. **2048x2048** main tier - the published default `min_generation_area` and
   the resolution where the shortlist LPIPS numbers were measured.
3. **4096x4096** stretch tier - attempt only on tracks B2/A with tiled VAE and
   `--max-vram`/block-swap tuning; abandon cleanly on OOM and record it.

Fixed generation contract: 6 NFEs, guidance_scale 1, no negative prompt,
`generator_device=cpu`, seeds 42/123/999, one discarded warmup generation,
at least 5 measured generations per cell. Metrics: load time, median/p95
end-to-end latency, images/hour, peak VRAM per GPU, peak host RAM, output
determinism (sha256), and LPIPS against the best available reference.

## 5. Why not benchmark more variants

The 32-repo catalogue collapses into a few families (GGUF K-quants, FP8,
NVFP4, SDNQ, OrbitQuant, bnb NF4, MLX). Within-family variants share a loader
and differ mainly in size/fidelity, so the plan samples the knee (UD-Q4_K_XL),
a smaller headroom point (Q3_K_M), a cross-repo control (Abiray Q4_K_M), and a
quality ceiling (Q5_K_M / FP8). NVFP4/MLX/ROCm/RDNA4 and all sm80+-only serving
paths are excluded with reasons above. This keeps the matrix reproducible
inside a finite Kaggle session.

## 6. Risks carried forward
- All "fits in 15 GB" claims are extrapolated from H20/4090/3090/L4 reports;
  first-run OOM is expected and tuning is part of the measurement protocol.
- Kaggle session lifetime is finite; downloads must resume (hf cache) and long
  runs must checkpoint results after each cell.
- MiniMax-H3-Image Community License has regional restrictions; do not publish
  derived outputs or weights without confirming jurisdiction and attribution.

## Sources
- https://huggingface.co/MiniMaxAI/MiniMax-H3-Image
- https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3-Image
- https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3-Image.md
- https://huggingface.co/unsloth/MiniMax-H3-Image-GGUF/raw/main/README.md
