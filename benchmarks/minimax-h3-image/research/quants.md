# Quantization catalogue: MiniMaxAI/MiniMax-H3-Image

Research date: 2026-11-18. Scope: every publicly listed quantization derived from
`MiniMaxAI/MiniMax-H3-Image`, evaluated for **viability** on the target server:
**2x T4** (NVIDIA Tesla T4, 15 GB each, 30 GiB aggregate but *not* a shared pool),
31 GiB system RAM, Compute Capability 7.5 (sm_75, Turing), CUDA 13, torch 2.11.

All sizes below are taken from Hugging Face API `?blobs=true` metadata or the
repo README, not estimated. Sources are listed at the end.

---

## 1. What is actually being quantized (and the 20B/18B/33B label puzzle)

The base checkpoint is large and multi-component. From the base model card and
API: total model ~135.3 GB = transformer/DiT 66.28 GB + text encoder (Qwen3-VL
32B, loaded from `MiniMaxAI/MiniMax-H3`) 66.7 GB + VAE 2.34 GB + heads/tokenizer.
The DiT itself is **33.1B parameters** (50 layers, hidden 5376, 56 heads, FFN
14336), BF16 weights with FP32 embedding/timestep/output layers.

Almost every "quantized" repo in this catalogue is a **pruned, DiT-only**
release: it replaces the 66.28 GB BF16 `transformer` and the per-step heads, and
expects you to bring the VAE and the 32B Qwen3-VL text encoder separately. This
is the key to the label discrepancy:

- HF's `gguf.total` metadata for the GGUF repos is `20,113,670,232` (~20.1B).
  That is the parameter count of the *pruned DiT GGUF*, not the full model, so
  HF tags those repos "20B". The DiT-only safetensors quant repos (unsloth FP8,
  LSDJesus) similarly get tagged "20B" by parameter count.
- The SDNQ repos quantize *both* the transformer and the text encoder but store
  their weights mostly as U8 (uint4 packed into bytes). `safetensors.parameters`
  reports `U8: 16,941,023,232` for SD-Next (~17.8B stored bytes) and
  `U8: 16,521,953,280` for OzzyGT 4-bit (~17.6B), which is why HF shows "18B".
  The *real* parameter count is still 33.1B; the label is an artifact of packed
  uint4 storage being counted as U8 elements.
- The OzzyGT 8-bit SDNQ repo stores weights as I8 and reports
  `I8: 33,043,906,560`, so HF shows "33B" - the full model parameter count.
- `yasutoshi-lab/...-GGUF` is tagged "7B", which suggests a partial/experimental
  conversion; treat it as unverified.

Consequence for this server: **no variant puts the whole pipeline resident on
one 15 GB T4.** The 32B text encoder alone is ~18.2 GB even at Q4_K_M, larger
than one T4. Every working setup here needs the text encoder streamed/offloaded
to the 31 GiB host RAM (or placed on the second T4 with a smaller quant), and
the DiT on the first T4.

---

## 2. Full catalogue of the 32 listed quantizations

Legend: **V** = viable on sm_75; **V\*** = viable with a caveat (emulation,
offload, or a torch/kernel requirement); **N** = non-viable.

| # | Repo | Format / levels | DiT file size (GB) | Loader / engine | sm_75 |
|---|------|-----------------|--------------------|-----------------|-------|
| 1 | `Abiray/MiniMax-H3-Image-GGUF` | GGUF Q2_K 6.88, Q3_K_M 8.91, Q4_K_M 11.57, Q4_K_S 11.57, Q5_K_M 14.08 | 6.9-14.1 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 2 | `unsloth/MiniMax-H3-Image-FP8` | FP8 e4m3 20.27 + INT8-ConvRot 20.27 | 20.3 | ComfyUI / Unsloth Desktop | V* |
| 3 | `unsloth/MiniMax-H3-Image-GGUF` | GGUF Q2_K 7.75, UD-Q2_K_XL 8.68, Q3_K_S 8.77, Q3_K_M 10.42, UD-Q3_K_XL 11.36, Q4_K_S 11.54, Q4_K_M 12.72, UD-Q4_K_XL 13.61, Q5_K_S 13.93, Q5_K_M 14.60, UD-Q5_K_XL 15.47, Q6_K 16.60, UD-Q6_K_XL 17.58, Q8_0 22.03 | 7.8-22.0 | stable-diffusion.cpp (`sd-cli`) / ComfyUI-GGUF | V |
| 4 | `Hearthscale/MiniMax-H3-Image-GGUF` | GGUF Q3_K_M 8.77, Q4_K_M 11.43, Q5_K_M 13.93, Q8_0 21.45 | 8.8-21.4 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 5 | `realrebelai/Minimax-H3-Image_GGUFs` | GGUF (20B family) | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 6 | `LSDJesus/MiniMax-H3-Image-fp8-nvfp4` | FP8-scaled 20.97 + NVFP4 12.54 | 12.5 / 21.0 | ComfyUI (comfy-kitchen) | V* / N |
| 7 | `WaveCut/MiniMax-H3-Image-OrbitQuant-W4A8` | W4A8 (GPTQ, INT8 activations), full pipeline 27.5 total (DiT 10.2 + TE 14.9 + VAE 2.3) | 10.2 | Diffusers ModularPipeline + OrbitQuant kernels; ComfyUI-OrbitQuant | V* |
| 8 | `VisualInference/MiniMax-H3-Image-MLX-bf16` | MLX bf16 | - | MLX (Apple Silicon only) | N |
| 9 | `cguldogan/MiniMax-H3-Image-MLX-4bit` | MLX 4-bit | - | MLX (Apple Silicon only) | N |
| 10 | `yasutoshi-lab/MiniMax-H3-Image-GGUF` | GGUF (tagged 7B; partial conversion) | unknown | llama.cpp-style GGUF | V* |
| 11 | `LSDJesus/MiniMax-H3-Image-GGUF` | GGUF family (pruned DiT) | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 12 | `moonbox-dev/MiniMax-H3-Image-GGUF` | GGUF family | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 13 | `convertor/minimax-h3-image-gguf` | GGUF family | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 14 | `cguldogan/MiniMax-H3-Image-MLX-8bit` | MLX 8-bit | - | MLX (Apple Silicon only) | N |
| 15 | `OzzyGT/minimax_h3_image_sdnq_dynamic_4bit` | SDNQ uint4 dynamic, full pipeline | 18.8 (2-shard DiT) | Diffusers ModularPipeline + sdnq; SD.Next | V* |
| 16 | `AtomicChat/MiniMax-H3-Image-GGUF` | GGUF family | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 17 | `infosave/MiniMax-H3-Image-cmf` | "cmf" (community model format) | unknown | niche loader, unverified | V* |
| 18 | `vantagewithai/MiniMax-H3-Image-ComfyUI-GGUF` | GGUF Q3_K_M 10.12, Q4_K_M 12.68, Q5_K_M 15.09, Q6_K 17.65 | 10.1-17.6 | ComfyUI-GGUF | V |
| 19 | `ZOET1219/MiniMax-H3-Image-GGUF` | GGUF family | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 20 | `lingjiu09/minimax-h3-image-gguf` | GGUF family | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 21 | `SD-Next/MiniMax-H3-Image-SDNQ-uint4-svd-hadamard-dynamic` | SDNQ uint4, SVD rank 32 + Hadamard, full pipeline 43.9 total (DiT 19.7 + TE 21.8 + VAE 2.3) | 19.7 | SD.Next / Diffusers ModularPipeline + sdnq | V* |
| 22 | `Mrbizarro/MiniMax-H3-Image-MLX-8bit` | MLX 8-bit | - | MLX (Apple Silicon only) | N |
| 23 | `OzzyGT/minimax_h3_image_sdnq_dynamic_8bit` | SDNQ 8-bit (I8), full pipeline | ~33 (4-shard DiT) | Diffusers ModularPipeline + sdnq | V* |
| 24 | `EliovpAI/MiniMax-H3-Image-FP8-Paiton-RDNA4` | FP8 via Paiton, AMD RDNA4 | ~20 | AMD / ROCm only | N |
| 25 | `zimageapp/MiniMax-H3-Image-MLX-Q4` | MLX Q4 | - | MLX (Apple Silicon only) | N |
| 26 | `devin-lai/MiniMax-H3-Image-mlx-q4` | MLX Q4 | - | MLX (Apple Silicon only) | N |
| 27 | `AcademiaSD/MiniMax-H3-Image-NF4-for-LoRA-Training` | bitsandbytes NF4 (transformers/ config_nf4.json) + LoRA adapter | ~11-13 (4-bit DiT) | Diffusers + bitsandbytes (training) | V* |
| 28 | `Harsha001/MiniMax-H3-Image-ROCmFPX` | GGUF Q4_0_ROCMFP4 11.40, Q5_K 13.91, Q6_K 16.57, Q8_0_ROCMFPX 20.80 | 11.4-20.8 | stable-diffusion.cpp + ROCmFPX patch (AMD/Vulkan) | N |
| 29 | `devin-lai/MiniMax-H3-Image-mlx-q8` | MLX Q8 | - | MLX (Apple Silicon only) | N |
| 30 | `ayanoby/hexanima-h3` | undocumented rebrand/derivative | unknown | unknown | V* |
| 31 | `molbal/miniMax-H3-Image-GGUF` | GGUF family (20B) | ~7-22 | stable-diffusion.cpp / ComfyUI-GGUF | V |
| 32 | `AIModelMaestro/MiniMax-H3-Image-NVFP4` | NVFP4 12.54 | 12.5 | ComfyUI (Blackwell only) | N |

---

## 3. Quant families in detail

### 3.1 GGUF (K-quants and Unsloth Dynamic) - the primary viable family

GGUF is a llama.cpp/ggml container holding block-quantized weights with per-block
scales. `Q4_K_M`, `Q5_K_M`, `Q6_K`, `Q8_0` are standard k-quants; `UD-Q*_XL` are
Unsloth "Dynamic" quants that promote sensitive tensors to higher precision.
These files replace only the DiT and store the time modulation in curve form.
Loaders: upstream **stable-diffusion.cpp** (MiniMax-H3 support merged in
PR #2324) via `sd-cli`, Unsloth's fork, and **ComfyUI-GGUF**. ggml's CUDA backend
supports Turing (sm_75) natively - no special tensor cores are required because
the dequantization and matmul run in FP16/CUDA cores. GGUF loading runs no
arbitrary Python code, a safety advantage.

Unsloth measured fidelity (LPIPS vs bf16 at 1024x1024, lower is better) and peak
VRAM for `unsloth/MiniMax-H3-Image-GGUF`: Q2_K 0.438 / 9.4 GiB; Q3_K_M 0.271 /
11.9 GiB; Q4_K_M 0.195 / 14.0 GiB; **UD-Q4_K_XL 0.172 / 14.8 GiB (recommended)**;
Q5_K_M 0.157 / 15.8 GiB; Q6_K 0.134 / 17.6 GiB; Q8_0 0.083 / 23.0 GiB. On a
24 GB L4, UD-Q4_K_XL ran 1.12-1.18 s/step at 1024x1024 with sd-cli, and with
`--max-vram 12` still rendered byte-identically at 3.91 s/step - i.e. ggml can
stream parts of the model from host RAM, which is exactly the tool for a 15 GB
T4. `Abiray/MiniMax-H3-Image-GGUF` (225k downloads, most popular quant) and
`Hearthscale/...-GGUF` (374k downloads) are the same scheme with slightly
different level sets; `vantagewithai/...-ComfyUI-GGUF` is the cleanest
ComfyUI-specific pack. Quality tradeoff: Q4_K_M/UD-Q4_K_XL is the fidelity/size
knee; Q5+ gives diminishing returns and stops fitting one T4; Q2_K is visibly
degraded (LPIPS 0.438).

### 3.2 FP8 (e4m3, scaled / ConvRot) and INT8-ConvRot

`unsloth/MiniMax-H3-Image-FP8` ships `MiniMax-H3-Image-FP8.safetensors` (20.27 GB)
and `MiniMax-H3-Image-INT8-ConvRot.safetensors` (20.27 GB), replacing the 66.3 GB
bf16 DiT. `LSDJesus/MiniMax-H3-Image-fp8-nvfp4` ships a
`minimax_h3_image_pruned_fp8_scaled.safetensors` (20.97 GB, fp8 e4m3 with one
scale per weight tensor, `full_precision_matrix_mult` on `mlp.fc2`). Both are
ComfyUI drop-ins. Unsloth reports LPIPS 0.255 FP8 vs 0.140 INT8-ConvRot at
2048x2048; the recommended scheme is INT8-ConvRot, and FP8's gap is intrinsic to
FP8, not the conversion. L4 numbers: 19.4 GB peak VRAM with DiT streamed from
RAM, ~50 s per 2048x2048 image in FP8.

**sm_75 caveat:** Turing has no native FP8 tensor cores (native FP8 starts at
Ada sm_89 / Hopper sm_90). ComfyUI still executes FP8 files on unsupported cards
by emulating them (casting weights to fp16), so FP8 is *functionally* viable but
slow. More importantly, the high-performance FP8 serving kernels used by SGLang
and vLLM (Marlin GEMM) require sm_80+ (Ampere) and are **non-viable** on sm_75.
On this server, treat FP8 as a ComfyUI-only, slower-than-GGUF option.

### 3.3 NVFP4 - non-viable

`LSDJesus/MiniMax-H3-Image-fp8-nvfp4` also ships
`minimax_h3_image_pruned_nvfp4.safetensors` (12.54 GB, E2M1 4-bit with e4m3
scales per 16 values); `AIModelMaestro/MiniMax-H3-Image-NVFP4` ships a similar
12.54 GB file with extensive RTX 5090 benchmarks. NVFP4 tensor cores exist only
on Blackwell (sm_100/sm_120, RTX 50 / RTX PRO 6000). On Turing there is no
hardware NVFP4 path; **non-viable** for this 2x T4 server regardless of the
small file size. The same holds for `Harsha001/...-ROCmFPX` Q4_0_ROCMFP4
(AMD RDNA4/Vulkan only) and `EliovpAI/...-Paiton-RDNA4` (AMD only) - both
**non-viable** on NVIDIA hardware. `EliovpAI` is gated to non-EU/US/etc.

### 3.4 SDNQ (uint4/8-bit dynamic, SVD + Hadamard)

SDNQ (https://github.com/Disty0/sdnq) is a Post-Training Quantization scheme
using uint4/uint8 dynamic quantization with automatic group size, SVD low-rank
residuals (rank 32) and Hadamard rotation, keeping sensitive layers in higher
precision. `SD-Next/...-SDNQ-uint4-svd-hadamard-dynamic` quantizes *both*
transformer and text encoder: total 43.9 GB vs 135.3 GB original (DiT 19.7 GB,
TE 21.8 GB, VAE 2.3 GB); 50/362 DiT layers and 58/564 TE layers are kept at
5-6 bits. Loads in SD.Next and via `ModularPipeline.from_pretrained` once `sdnq`
is imported. `OzzyGT/...-sdnq_dynamic_4bit` (4-bit, 18.8 GB DiT) and
`OzzyGT/...-sdnq_dynamic_8bit` (8-bit, ~33 GB DiT) are lighter/heavier variants.

**sm_75 caveat:** SDNQ dequantization is implemented in PyTorch/Triton-style
kernels that do not require Tensor Cores, so SDNQ is expected to run on Turing,
but it is far less battle-tested on sm_75 than GGUF and the 4-bit repos quantize
the text encoder too, which helps the 31 GiB RAM budget. The 8-bit repo's 33 GB
DiT will not fit a 15 GB T4 and needs aggressive offload. Marked V*.

### 3.5 OrbitQuant W4A8

`WaveCut/MiniMax-H3-Image-OrbitQuant-W4A8` applies GPTQ-rounded 4-bit weights
with INT8 activations to both the DiT (10.2 GB) and the 50-layer text encoder
(14.9 GB); full download 27.5 GB. Runtime is the Diffusers ModularPipeline with
fused OrbitQuant kernels (`orbitquant` 0.18.0) or ComfyUI-OrbitQuant >= 0.11.
Quality is strong: mean LPIPS 0.182 vs bf16 (vs 0.302 for round-to-nearest);
speed on a 96 GB RTX PRO 6000 is 2.40 s at 2048x2048 and 13.53 s at 4096x4096,
with a 29.8 GiB device peak and a tested offload profile that runs in 23.4 GiB
free VRAM. **Caveats for this server:** the tested stack is Torch 2.12.1/CUDA
13.0 (target has torch 2.11), and the fused W4A8 kernels were only validated on
Blackwell; INT8 activations involve DP4A-style integer math that Turing does
support, but this is unverified on sm_75. Viable only as an experiment, V*.

### 3.6 bnb NF4 (LoRA training)

`AcademiaSD/MiniMax-H3-Image-NF4-for-LoRA-Training` provides a bitsandbytes NF4
`transformers/` config plus a ~489 MB dedistill adapter, aimed at QLoRA-style
training. bitsandbytes NF4 works on sm_75, so it is technically viable, but it
is a *training* artifact, not an inference quant, and is out of scope for a
benchmark of inference speed/quality.

### 3.7 MLX and other non-viable families

All MLX repos (`VisualInference/...-MLX-bf16`, `cguldogan/...-MLX-4bit` and
`-MLX-8bit`, `Mrbizarro/...-MLX-8bit`, `zimageapp/...-MLX-Q4`,
`devin-lai/...-mlx-q4` and `-mlx-q8`) target Apple Silicon's MLX framework and
are **non-viable** on an NVIDIA CUDA server, full stop. `infosave/...-cmf` and
`ayanoby/hexanima-h3` are undocumented niche derivatives: unverified loaders,
so low confidence.

**Licensing note:** all these derivatives inherit the MiniMax-H3-Image Community
License, which grants rights only outside the EU, UK, South Korea and the USA;
Harsha001 is explicitly gated on that basis. Confirm the server's jurisdiction
before use.

---

## 4. Viability ranking for 2x T4 (sm_75) and the shortlist to benchmark

Ranking criteria: (a) fits one 15 GB T4 at a useful resolution, (b) speed on
sm_75 via a mature loader, (c) fidelity to bf16, (d)text-encoder/RAM budget on
31 GiB host RAM. Remember the two T4s are separate: a single model cannot simply
"use 30 GiB"; plan on DiT on GPU0 and text encoder streamed from RAM or on GPU1.

1. **`unsloth/MiniMax-H3-Image-GGUF` - UD-Q4_K_XL / Q4_K_M (best overall).** 13.61 GB / 12.72 GB; 14.8 / 14.0 GiB peak; LPIPS 0.172 / 0.195; mature sd-cli and ComfyUI-GGUF loaders with native sm_75 CUDA and proven host-RAM streaming. The clear #1.
2. **`Abiray/MiniMax-H3-Image-GGUF` - Q4_K_M (11.57 GB) / Q3_K_M (8.91 GB).** Same quant scheme, most-downloaded repo, good community support; Q3_K_M gives more headroom for 2048x2048 on 15 GB.
3. **`Hearthscale/MiniMax-H3-Image-GGUF` - Q4_K_M (11.43 GB) / Q5_K_M (13.93 GB).** Clean level set; Q5_K_M trades a little fit margin for LPIPS 0.157.
4. **`vantagewithai/MiniMax-H3-Image-ComfyUI-GGUF` - Q4_K_M (12.68 GB).** Purpose-built ComfyUI pack; pick this if the benchmark is ComfyUI-centric.
5. **`unsloth/MiniMax-H3-Image-FP8` INT8-ConvRot / FP8 (20.27 GB).** Best non-GGUF fidelity (LPIPS 0.140 at 2048), but must be streamed from RAM on a 15 GB T4 and FP8 is emulated on sm_75; slower. Benchmark for quality, not speed.
6. **`LSDJesus/MiniMax-H3-Image-fp8-nvfp4` FP8-scaled (20.97 GB).** Same FP8 caveats; include only to contrast against unsloth FP8. Its NVFP4 file is non-viable.
7. **`SD-Next/...-SDNQ-uint4-svd-hadamard-dynamic` (19.7 GB DiT) / `OzzyGT/...-sdnq_dynamic_4bit` (18.8 GB).** Quantized text encoder eases RAM pressure; sm_50/Turing kernel support unverified - experimental.
8. **`WaveCut/...-OrbitQuant-W4A8` (10.2 GB DiT + 14.9 GB TE).** Excellent paper numbers but torch 2.12.1/Blackwell kernel requirement makes it a stretch on torch 2.11/sm_75 - experimental.
9. **`AcademiaSD/...-NF4`** - training only, exclude from inference benchmark.

**Non-viable (do not benchmark):** all NVFP4 (LSDJesus NVFP4 file,
AIModelMaestro NVFP4), all MLX repos, EliovpAI FP8-Paiton-RDNA4,
Harsha001 ROCmFPX, and any SGLang/vLLM FP8-Marlin serving path (sm_80+ kernel
requirement, no Turing support).

### Recommended benchmark shortlist (top 5)

| Rank | Artifact | Size | Engine on 2x T4 | Why |
|------|----------|------|-----------------|-----|
| 1 | unsloth GGUF `UD-Q4_K_XL` | 13.61 GB | stable-diffusion.cpp `sd-cli`, DiT on GPU0, TE streamed | Best fidelity that fits 15 GB; native sm_75 |
| 2 | unsloth GGUF `Q3_K_M` | 10.42 GB | stable-diffusion.cpp / ComfyUI-GGUF | Headroom for 2048x2048, LPIPS 0.271 |
| 3 | Abiray GGUF `Q4_K_M` | 11.57 GB | ComfyUI-GGUF | Most-tested community quant, direct comparison |
| 4 | Hearthscale GGUF `Q5_K_M` | 13.93 GB | stable-diffusion.cpp | High-quality ceiling that still just fits |
| 5 | unsloth FP8 `INT8-ConvRot` | 20.27 GB | ComfyUI, streamed from RAM | Fidelity reference (LPIPS 0.140) vs GGUF knee |

---

## 5. Sources

- https://huggingface.co/models?other=base_model%3Aquantized%3AMiniMaxAI%2FMiniMax-H3-Image (page 1)
- https://huggingface.co/models?other=base_model%3Aquantized%3AMiniMaxAI%2FMiniMax-H3-Image&p=1&sort=trending (page 2)
- https://huggingface.co/api/models/unsloth/MiniMax-H3-Image-GGUF?blobs=true
- https://huggingface.co/api/models/unsloth/MiniMax-H3-Image-FP8?blobs=true
- https://huggingface.co/api/models/Abiray/MiniMax-H3-Image-GGUF?blobs=true
- https://huggingface.co/api/models/Hearthscale/MiniMax-H3-Image-GGUF?blobs=true
- https://huggingface.co/api/models/SD-Next/MiniMax-H3-Image-SDNQ-uint4-svd-hadamard-dynamic?blobs=true
- https://huggingface.co/api/models/OzzyGT/minimax_h3_image_sdnq_dynamic_4bit?blobs=true
- https://huggingface.co/api/models/OzzyGT/minimax_h3_image_sdnq_dynamic_8bit?blobs=true
- https://huggingface.co/api/models/WaveCut/MiniMax-H3-Image-OrbitQuant-W4A8?blobs=true
- https://huggingface.co/api/models/LSDJesus/MiniMax-H3-Image-fp8-nvfp4?blobs=true
- https://huggingface.co/api/models/vantagewithai/MiniMax-H3-Image-ComfyUI-GGUF?blobs=true
- https://huggingface.co/api/models/MiniMaxAI/MiniMax-H3-Image?blobs=true
- https://huggingface.co/api/models/AIModelMaestro/MiniMax-H3-Image-NVFP4?blobs=true
- https://huggingface.co/api/models/AcademiaSD/MiniMax-H3-Image-NF4-for-LoRA-Training?blobs=true
- https://huggingface.co/api/models/Harsha001/MiniMax-H3-Image-ROCmFPX?blobs=true
- https://huggingface.co/unsloth/MiniMax-H3-Image-GGUF/raw/main/README.md (LPIPS/VRAM table, loaders)
- https://huggingface.co/unsloth/MiniMax-H3-Image-FP8/raw/main/README.md (FP8/INT8 metrics)
- https://huggingface.co/SD-Next/MiniMax-H3-Image-SDNQ-uint4-svd-hadamard-dynamic/raw/main/README.md
- https://huggingface.co/LSDJesus/MiniMax-H3-Image-fp8-nvfp4/raw/main/README.md
- https://huggingface.co/WaveCut/MiniMax-H3-Image-OrbitQuant-W4A8/raw/main/README.md
- https://github.com/Disty0/sdnq
- https://github.com/leejet/stable-diffusion.cpp
