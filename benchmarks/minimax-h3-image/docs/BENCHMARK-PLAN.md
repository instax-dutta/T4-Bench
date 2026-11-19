# MiniMax-H3-Image inference benchmark plan on 2x Kaggle T4

Version: 1.0 (perfected plan, ready to execute). Date: 2026-11-18.
Hardware source: live SSH probes of the Kaggle session described in
`research/model-hardware.md`. Research base: `research/SYNTHESIS.md`,
`research/quants.md`, `research/engines-lowvram.md`. Server-specific selection
logic: `docs/feasibility-matrix.md`. Results format: `benchmark/results-template.md`.
Work contracts for every folder are in the DOX tree rooted at `AGENTS.md`.

## Executive Summary

The full model cannot run on this server: its BF16 weights total 126.0 GiB,
while the machine has 30 GiB of discrete VRAM and ~29 GiB of available host
RAM, and Turing (sm_75) lacks the BF16/FP8/FP4/Marlin/FlashAttention-2 kernels
that the official serving stacks rely on. This benchmark therefore measures the
thing that *is* answerable here: how the available low-VRAM quantizations and
engines perform under a dequantize-to-FP16 regime, at what latency, memory cost,
and fidelity loss.

The plan compares four tracks under one fixed workload: (A) DiffSynth-Studio
with official EntroPack int8/3bpp models and its disk/CPU VRAM manager,
(B) `stable-diffusion.cpp` with unsloth GGUF quants and a quantized text
encoder, (C) ComfyUI + ComfyUI-GGUF with low-VRAM flags and block swapping, and
(F) diffusers ModularPipeline with weight-only NF4/int8 plus sequential CPU
offload. A fifth track (D) supplies a fidelity reference with FP8/INT8-ConvRot
weights, which are emulated on Turing and expected to be slow. SGLang,
vLLM-Omni, NVFP4, MLX, and all ROCm/RDNA paths are excluded with recorded
reasons rather than silently dropped.

The benchmark is deliberately conservative: start at 1024x1024, promote to
2048x2048 only for configs that fit, and treat 4096x4096 as a stretch tier with
a clean abandonment path. Every run is recorded in `benchmark/results-template.md`
with fixed seed, warmup policy, measured peak VRAM, and an acceptance verdict.

## 1. Server and constraints (measured, not assumed)

| Item | Value |
|---|---|
| GPUs | 2x NVIDIA Tesla T4, 15360 MiB each, no NVLink |
| Compute capability | 7.5 (sm_75, Turing); FP16 + INT8 tensor cores only |
| Driver / runtime | 580.178.04 / CUDA 13.0 |
| Host | 4 vCPU Xeon @2.0GHz, 31 GiB RAM, 0 swap (~29 GiB free), ~967 GB disk, Ubuntu 24.04 |
| Installed | torch 2.11.0+cu130, diffusers 0.42.0, accelerate 1.15.0, transformers 5.20.2, hf CLI 1.33.0 |
| Missing (install at runtime) | bitsandbytes, torchao, xformers, flash-attn, sentencepiece |
| Network | Hugging Face reachable (HTTP 307 resolve-cache); Kaggle Jupyter kernel behind zrok SSH tunnel |

### Weight memory, recomputed from model-card component sizes

Conversion: decimal GB * 1e9 / 2^30, rounded to 1 decimal. These figures are
recomputed independently by `scripts/verify-math.mjs` at gate time.

| Component / config | Size |
|---|---|
| DiT BF16 | 61.7 GiB |
| DiT FP8 | 30.9 GiB |
| DiT 4-bit | 15.4 GiB |
| Text encoder BF16 | 62.1 GiB |
| Text encoder 4-bit | 15.5 GiB |
| Full BF16 pipeline | 126.0 GiB |
| Full FP8 pipeline | 64.1 GiB |
| Full 4-bit pipeline | 33.1 GiB |
| FP8 DiT + 4-bit text encoder | 48.6 GiB |

Even the 33.1 GiB all-4-bit pipeline exceeds both VRAM and host RAM before
activations, and the 16 MP path adds several GiB of activations plus a heavy
FP32 VAE decode. Quantizing *both* the DiT and the text encoder, plus streaming
between disk, CPU and GPU, is mandatory. Kernel constraints on sm_75: BF16
needs sm_80+, FP8 GEMM sm_89/sm_90+, Marlin INT4 sm_80+, FlashAttention-2
sm_80+ (and is not installed), NVFP4 Blackwell. Only FP16/FP32 cuBLAS, INT8
tensor-core paths, and dequantize-to-FP16 weight-only quant actually run.

## 2. Research base and exclusions

The 32 public quant repos were catalogued with real file sizes from the Hugging
Face API. They collapse into a few families: GGUF K-quants (mature loaders,
native sm_75 CUDA), FP8/INT8-ConvRot (emulated, quality reference), NVFP4
(Blackwell only), SDNQ uint4, OrbitQuant W4A8, bnb NF4, and MLX (Apple only).
Nearly all "quant" repos are pruned DiT-only releases; the 32B Qwen3-VL text
encoder must be supplied separately. HF's "20B"/"18B"/"33B" labels reflect
storage-counting conventions, not real parameter counts.

Exclusions with reasons: NVFP4 and W4A4 (Blackwell), MLX (Apple), ROCmFPX /
RDNA4 (AMD), SGLang diffusion (no sm_75 recipe, FlashAttention and NVLink
assumptions), vLLM-Omni serving (Qwen3-VL Turing backend closed as not planned;
FP8 Marlin needs sm_80+), NF4 LoRA training repo (training, not inference).
LightX2V INT8 is a documented but unmeasured fallback, not part of the main
matrix. No variant is excluded merely for being slow: FP8 is kept as a fidelity
reference precisely because it is emulated.

## 3. Benchmark Matrix

All tracks use the same 6 NFEs, guidance_scale 1, Euler sampler, the
`minimax-h3-image` sigma schedule, and the same prompt/seed set. Placement is
GPU0 for the DiT; the text encoder is either a small quantized file on GPU1 or
streamed from host RAM/disk.

| Track | Quant artifact | Engine / loader | Key flags | Why included |
|---|---|---|---|---|
| A | DiffSynth EntroPack 3bpp DiT + 3bpp TE (7.14 GiB DiT) | DiffSynth-Studio | `vram_limit`, `offload_vram_config` disk offload, tiled VAE, FP16 compute | Smallest official footprint; primary |
| A2 | DiffSynth INT8 ConvRot DiT + int8 TE | DiffSynth-Studio | `vram_limit=13`, disk streamed TE, tiled VAE | Near-lossless INT8 reference |
| B | unsloth GGUF UD-Q4_K_XL (13.61 GB, LPIPS 0.172) | stable-diffusion.cpp `sd-cli` | `--offload-to-cpu`, `--vae-tiling`, `--max-vram 12`, `--rng cpu` | Best sm_75-native loader; published fidelity knee; primary |
| B2 | unsloth GGUF Q3_K_M (10.42 GB, LPIPS 0.271) + P-H3 4B text encoder (~5 GB) | stable-diffusion.cpp `sd-cli` | same as B, plus `--llm` P-H3-Image encoder | Headroom tier; official small-TE path |
| B3 | unsloth GGUF Q5_K_M (14.60 GB, LPIPS 0.157) | stable-diffusion.cpp | `--max-vram 12`, `--offload-to-cpu` | Quality ceiling that still just fits |
| C | Abiray GGUF Q4_K_M (11.57 GB) | ComfyUI + ComfyUI-GGUF | `--lowvram`, `--reserve-vram 1.5`, block swap | Community control; INT8 tensor cores |
| C2 | Comfy-Org W4A8 DiT (14.88 GiB) + quantized TE | ComfyUI | `--lowvram --novram` | Tightest ComfyUI config; RISK |
| D | unsloth FP8-INT8-ConvRot (20.27 GB, LPIPS 0.140) | ComfyUI, streamed from RAM | default, no FP8 kernels | Fidelity reference; emulated, slow |
| E | SD-Next SDNQ uint4 (DiT 19.7 GB) | SD.Next / diffusers ModularPipeline | sequential offload | Experimental, only if time remains |
| F | bnb NF4 / torchao int8 on DiT + TE | diffusers ModularPipeline | `manager.enable_auto_cpu_offload(device="cuda")`, `pipe.enable_sequential_cpu_offload()` | Clean API reference; weight-only quant |

Run order: smoke tier first (B, B2, A), then main tier (B, A, A2, C, F, D),
then stretch (B2/B3/A at 4096), then experimental E only if the session allows.

## 4. Methodology

### Workload
- Tasks: text-to-image (primary) and one reference-image edit per track to
  check that the encoder/connector path works.
- Prompt set P1..P5: (P1) photoreal portrait, (P2) detailed scene with text
  rendering, (P3) product still life, (P4) stylized illustration, (P5) the
  official "Astronaut in a jungle, cold color palette, muted colors, detailed,
  8k" card prompt. Store each prompt verbatim and record its SHA256.
- Prompt expansion: skip local MiniMax-H3-Image-PE (NVFP4, non-viable). Use
  either the raw prompt or the hosted H3-Image-Context-IR API; record which.
- Sizes: 1024x1024 (smoke), 2048x2048 (main), 4096x4096 (stretch). All multiples
  of 32. Where an engine exposes `min_generation_area`, pass 1024 to generate
  at the requested size instead of the 2048x2048 default canvas.
- Fixed generation: 6 steps, CFG 1, no negative prompt, `generator_device=cpu`
  / `--rng cpu`, seeds 42, 123, 999, one discarded warmup generation after load.

### Measurements
For each (track, size, seed) cell, record: load time; 5+ end-to-end latency
samples; median, mean and p95 latency; per-step latency (median / 6);
throughput in images/hour (3600 / median latency); peak VRAM on each GPU
(sampled with `nvidia-smi --query-gpu=... --format=csv` at 1 s intervals during
the run, plus `torch.cuda.max_memory_allocated()` where the engine exposes it);
peak host RAM; output file and its SHA256. Two consecutive runs with the same
seed must hash identically, otherwise the cell is invalid. Check output
dimensions and that the image is non-empty/non-black.

### Isolation and tuning policy
Run one track at a time. Kill the previous engine process, confirm GPU memory
returns to baseline, and restart before the next track. A first-run OOM is
expected, not a failure: tune in this order, recording each change:
(1) drop resolution, (2) use the smaller quant, (3) use the 4B text encoder,
(4) lower `vram_limit` / raise `--max-vram` streaming, (5) enable block swapping
or sequential offload, (6) enable tiled VAE. Do not change seed, step count or
prompt set when tuning. A cell is ABANDONED only after all six steps fail;
record the reason.

### Acceptance criteria
- PASS: correct dimensions, deterministic hash, non-empty image, measured
  peak VRAM within the device limit, all metrics captured.
- FAIL: engine crashes after tuning, non-deterministic output, wrong size.
- ABANDONED: configuration cannot fit after the full tuning ladder; recorded
  with the smallest failing configuration and the last OOM message.
- No number is reported without a matching results-template entry.

## 5. Runbook

### 5.1 Connect and preflight
```sh
sshpass -p 'kaggle' ssh -tt -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no -p 9191 root@127.0.0.1
nvidia-smi --query-gpu=index,name,memory.used,memory.free --format=csv
df -h /kaggle/working
```

### 5.2 Install and download (resumable)
```sh
pip install -U "diffusers>=0.42" accelerate bitsandbytes torchao gguf sentencepiece
git clone https://github.com/leejet/stable-diffusion.cpp /kaggle/working/stable-diffusion.cpp
cd /kaggle/working/stable-diffusion.cpp && mkdir -p build && cd build
cmake -DSD_CUDA=ON .. && cmake --build . -j4
git clone https://github.com/modelscope/DiffSynth-Studio.git /kaggle/working/DiffSynth-Studio
cd /kaggle/working/DiffSynth-Studio && pip install -e . "diffsynth[quant]" diffsynth==2.2.2 cupy-cuda13x
git clone https://github.com/Comfy-Org/ComfyUI.git /kaggle/working/ComfyUI
git clone https://github.com/city96/ComfyUI-GGUF /kaggle/working/ComfyUI/custom_nodes/ComfyUI-GGUF
hf download unsloth/MiniMax-H3-Image-GGUF --include "*Q4_K_M*" --local-dir /kaggle/working/models/unsloth-gguf
hf download unsloth/MiniMax-H3-Image-GGUF --include "*Q3_K_M*" --local-dir /kaggle/working/models/unsloth-gguf
hf download leejet/MiniMax-H3-GGUF --include "*Q4_K_M*" --local-dir /kaggle/working/models/text-encoder
hf download PrunaAI/P-H3-Image-Comfy --include "*int8*" --local-dir /kaggle/working/models/p-h3-te
hf download Comfy-Org/MiniMax-H3-Image --include "vae/*" --local-dir /kaggle/working/models/comfy
```
`hf` resumes partial downloads from its cache, which matters because the
session lifetime is finite.

### 5.3 Track B launch (canonical sm_75 path)
```sh
cd /kaggle/working/stable-diffusion.cpp/build
./bin/sd-cli \
  --diffusion-model /kaggle/working/models/unsloth-gguf/minimax_h3_image-UD-Q4_K_XL.gguf \
  --vae /kaggle/working/models/comfy/vae/minimax_h3_image_vae_fp16.safetensors \
  --llm /kaggle/working/models/text-encoder/qwen3vl_32b_minimax_h3-Q4_K_M.gguf \
  -p "A silver tabby kitten holding a sign reading 'sd.cpp', natural daylight" \
  --cfg-scale 1.0 --steps 6 --sampling-method euler --sigmas minimax-h3-image \
  -W 1024 -H 1024 --rng cpu --offload-to-cpu --vae-tiling --max-vram 12 -v
```
For track B2 replace `--llm` with the P-H3-Image 4B encoder (~5 GB) and use
the Q3_K_M DiT. `--diffusion-fa` is optional; if it fails to build on sm_75,
drop it. Width and height are aligned up to multiples of 32.

### 5.4 Track A launch (DiffSynth-Studio)
Use the official MiniMax-H3-Image low-VRAM example from
https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3-Image.md .
Set `vram_limit = free_GiB - 2` (start at 13 on a 15 GB T4), use the EntroPack
3bpp DiT + 3bpp text encoder, `offload_vram_config` with
`"offload_device": "disk"` for the encoder, `tiled=True` for the VAE, and FP16
compute. Avoid the sm90-only `sage_attention_h20_fast` kernel.

### 5.5 Track C launch (ComfyUI)
```sh
cd /kaggle/working/ComfyUI
python main.py --lowvram --reserve-vram 1.5
```
Load the official T2I template, select a GGUF DiT via ComfyUI-GGUF, a quantized
text encoder, and the fp16 VAE. If OOM occurs, add `--novram` and enable block
swapping / unload nodes. Never select `fp8_scaled`, NVFP4 or Comfy-Kitchen FP4
models on this server.

### 5.6 Measurement wrapper
Start a background sampler before each run:
```sh
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total \
  --format=csv,noheader -l 1 > /kaggle/working/results/<run-id>-gpu.csv &
```
Time the run with `/usr/bin/time -v` to capture wall clock and peak RSS, then
copy the CSV and output PNG into `benchmark/results/<run-id>/` and append a
filled block from `benchmark/results-template.md`. Checkpoint after every cell.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Finite Kaggle session | Resume downloads via hf cache; checkpoint each cell; run smoke tier first |
| First-run OOM (expected) | Six-step tuning ladder in section 4; ABANDONED verdict with evidence |
| sm_75 kernel gaps | Force FP16 compute; plain int8/NF4 path; avoid FA2, FP8, NVFP4, sm90 kernels |
| Extrapolated "fits in 15 GB" claims | Treat every fit claim as a hypothesis; measure peak VRAM, never assume |
| Text encoder 62.1 GiB at BF16 | Always use a quantized TE (4B P-H3 ~5 GB, GGUF Q4, int8 or 3bpp) |
| Determinism | Fixed seed + `--rng cpu` / `generator_device=cpu`; rerun and compare SHA256 |
| License (regional restrictions) | Do not publish derived weights/outputs without confirming jurisdiction and attribution |
| No local prompt expander | Use raw prompts or the hosted Context-IR API; record which |

## 7. Reporting

Results are appended to `benchmark/results-template.md` and summarised in its
per-config table. Final reporting ranks tracks by median latency and images/hour
at a common resolution, reports peak VRAM and fidelity where available, and
states explicitly which tracks were ABANDONED and why. No geometry or kernel
assumption from this plan is promoted to a finding without a measured run.

## 8. Sources
- https://huggingface.co/MiniMaxAI/MiniMax-H3-Image
- https://huggingface.co/unsloth/MiniMax-H3-Image-GGUF/raw/main/README.md
- https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/models/minimax_h3_image.md
- https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3-Image.md
- https://docs.comfy.org/tutorials/image/minimax/minimax-h3-image
- https://huggingface.co/docs/diffusers/main/en/api/pipelines/minimax_h3_image
- https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3-Image
- https://recipes.vllm.ai/MiniMaxAI/MiniMax-H3-Image
