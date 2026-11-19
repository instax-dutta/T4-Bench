# Synthesis: MiniMax-H3-Image on 2x Kaggle T4

This node reconciles three verified research leaves into one ranked evidence
base. Leaf sources: `model-hardware.md` (server + architecture + memory math),
`quants.md` (32-variant catalogue), `engines-lowvram.md` (engines, low-VRAM
methods, GitHub/forum evidence). Raw claims and URLs stay in those leaves.

Sources used here: https://huggingface.co/MiniMaxAI/MiniMax-H3-Image ,
https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3-Image.md ,
https://github.com/city96/ComfyUI-GGUF , https://github.com/leejet/stable-diffusion.cpp .

## 1. Two independent walls

**Memory wall.** The official component sizes sum to 126.0 GiB at BF16 (DiT
61.7 GiB + text encoder 62.1 GiB + VAE 2.2 GiB). Even an all-4-bit pipeline is
33.1 GiB, above the 30 GiB aggregate VRAM and the ~29 GiB available host RAM,
before activations. The two T4s are discrete with no NVLink, so 30 GiB is not a
single addressable pool. Native-resolution 16 MP generation with the full
pipeline resident is not possible here.

**Kernel wall.** T4 is Compute Capability 7.5 (sm_75, Turing). Turing has FP16
and INT8 tensor cores but no native BF16, FP8, FP4/NVFP4, Marlin INT4, or
FlashAttention-2 path. FA2/Marlin need sm_80+, FP8 needs sm_89/sm_90, NVFP4
needs Blackwell, and flash-attn is not installed. Any plan that assumes those
kernels is a plan for different hardware.

Consequence: the benchmark must be a **low-VRAM, dequantize-to-FP16** study.
That is the user's actual question and it is answerable: measure how far each
quant/engine combination gets under these constraints.

## 2. What the quant leaf concluded

- Almost every public "quant" is a **pruned DiT-only** release. The 32B
  Qwen3-VL text encoder (62.1 GiB BF16) must be supplied and quantized/offloaded
  separately. HF's "20B"/"18B"/"33B" labels are storage-counting artifacts.
- Mature, sm75-native loaders exist for GGUF: `stable-diffusion.cpp` (`sd-cli`,
  ggml CUDA backend supports Turing and streams weights from host RAM) and
  `ComfyUI-GGUF`. These dequantize to FP16 on CUDA cores, so they actually run.
- Unsloth's published fidelity/VRAM curve for `unsloth/MiniMax-H3-Image-GGUF`:
  Q2_K LPIPS 0.438 / 9.4 GiB; Q4_K_M 0.195 / 14.0 GiB; UD-Q4_K_XL 0.172 /
  14.8 GiB (knee); Q5_K_M 0.157 / 15.8 GiB; Q8_0 0.083 / 23.0 GiB. A 24 GB L4
  ran UD-Q4_K_XL at 1.12-1.18 s/step at 1024x1024, and 3.91 s/step with
  `--max-vram 12` while producing byte-identical images: host-RAM streaming is
  proven and is the key mechanism for a 15 GB T4.
- FP8 files (20.27 GB) are emulated on sm75 and are slower; SGLang/vLLM FP8
  Marlin serving is non-viable. NVFP4, MLX, RDNA4/ROCmFPX are non-viable.
- Quant shortlist: unsloth UD-Q4_K_XL, unsloth Q3_K_M, Abiray Q4_K_M,
  Hearthscale Q5_K_M, unsloth FP8-INT8-ConvRot (quality reference).

## 3. What the engine leaf concluded

The engine leaf's ranked table (reproduced in condensed form):

| Rank | Engine / method | sm75 status | Notes |
|---|---|---|---|
| 1 | DiffSynth-Studio + EntroPack INT8/3bpp + disk/CPU VRAM manager | works with FP16 compute | Only engine with explicit official low-VRAM flags and 3-bit quants for this exact model; 3bpp DiT is 7.14 GiB, matching 3bpp text encoder exists |
| 2 | ComfyUI + W4A8 (14.88 GiB) or GGUF Q4 + quantized TE + `--lowvram`/block swapping | works for int8/GGUF | Largest ecosystem; `--lowvram`, `--novram`, `--reserve-vram`, block swapping; FP8/NVFP4 must be avoided |
| 3 | diffusers ModularPipeline + sequential CPU offload + bnb NF4 / torchao int8 | works with FP16 + weight-only quant | Clean API, no H3-Image-on-T4 measurement upstream |
| 4 | LightX2V INT8 W8A8 + hierarchical offload | works for INT8 | sm75 unmeasured; NVFP4 path non-viable |
| 5 | vLLM-Omni DLO layerwise offload | unqualified | Qwen3-VL Turing backend closed as not planned |
| 6 | SGLang layerwise offload | non-viable in practice | FA/FP8 and NVLink assumptions exclude T4 |

Explicit low-VRAM levers from GitHub and forums: CPU/sequential offload,
block swapping, a quantized text encoder (the single biggest lever,
62.1 GiB -> ~7-24 GiB), GGUF K-quants, bnb NF4 / torchao int8, SDNQ uint4,
`min_generation_area` (1024 disables the 2048x2048 default canvas), sequence
parallelism across two GPUs, cold sequential component loading, and 2/6-step
distilled variants. Key caution from a ComfyUI forum thread: "CPU offload costs
more than precision tradeoffs", i.e. prefer a smaller quant before adding
offload. All "fits in 15 GB" figures are extrapolations from H20/4090/3090, so
expect an initial OOM and tune `vram_limit` / block-swap counts empirically.

## 4. Reconciliation: why the two #1 picks do not conflict

The quant leaf optimized for **loader maturity on sm75** and picked
`stable-diffusion.cpp` + GGUF. The engine leaf optimized for **official
low-VRAM support** and picked DiffSynth-Studio + EntroPack int8/3bpp. They are
answers to different questions, and both belong in the benchmark:

- DiffSynth-Studio answers "what is the smallest official memory footprint?"
  (3bpp DiT 7.14 GiB + 3bpp text encoder, disk streaming, `vram_limit`).
- `stable-diffusion.cpp` answers "what runs most reliably on Turing today?"
  (ggml CUDA, no Python code execution, proven host-RAM streaming, published
  LPIPS/VRAM numbers).
- ComfyUI answers "what does the broadest community stack achieve?"
  (int8_convrot uses Turing INT8 tensor cores, `--lowvram`, block swapping,
  largest quant ecosystem).

A credible benchmark compares them under identical prompts, sizes, seeds and
step counts rather than crowning one in advance.

## 5. Final shortlist to benchmark (ranked)

| Rank | Track | Artifact + engine | Rationale |
|---|---|---|---|
| 1 | A | DiffSynth-Studio + EntroPack 3bpp DiT/TE, `vram_limit`, tiled VAE | lowest official footprint; best chance at 15 GB |
| 2 | B | unsloth GGUF UD-Q4_K_XL + `stable-diffusion.cpp sd-cli`, `--max-vram` | best sm75-native fidelity/knee; published LPIPS 0.172 |
| 3 | C | unsloth GGUF Q3_K_M / Abiray Q4_K_M + ComfyUI-GGUF, `--lowvram` | ecosystem + INT8 tensor cores / block swap |
| 4 | D | unsloth GGUF Q5_K_M or FP8-INT8-ConvRot + ComfyUI | quality ceiling / fidelity reference; slower |
| 5 | E | diffusers ModularPipeline + bnb NF4 int8 + sequential offload | API-level reference, sm75 weight-only path |

Excluded with reason: NVFP4 (Blackwell), MLX (Apple), RDNA4/ROCmFPX (AMD),
FP8-Marlin via SGLang/vLLM (sm80+), SGLang diffusion (no sm75 recipe, NVLink
assumptions), LightX2V W4A4 (Blackwell), NF4 LoRA training repo (training only).

## 6. Open risks carried into the plan
- First-run OOM is expected; tuning (`vram_limit`, `--max-vram`, block-swap
  count, `min_generation_area`) is part of the method, not a failure.
- Some DiffSynth attention/ConvRot kernels are arch-specific; force FP16 compute
  and the plain int8/NF4 path.
- Kaggle session lifetime is finite; downloads and long runs need a resume path.
- License is MiniMax-H3-Image Community License with regional restrictions
  (EU/UK/KR/US excluded); confirm before any derived data is published.
