# MiniMax-H3-Image: model and target-server research

Raw, source-cited research for the benchmark plan. Every factual claim below is tied to either a live measured command on the target server or a fetched upstream source. No guesses. Weight sizes are converted with decimal GB * 1e9 / 2^30 and reported in GiB; GB and GiB are never mixed silently.

## Sources

1. Model card and file manifest: https://huggingface.co/MiniMaxAI/MiniMax-H3-Image
2. Prompt-expander (PE) model card: https://huggingface.co/MiniMaxAI/MiniMax-H3-Image-PE
3. NVIDIA CUDA GPU compute-capability table: https://developer.nvidia.com/cuda-gpus
4. FlashAttention official repo (README: FA2/FA3/FA4 hardware requirements): https://github.com/Dao-AILab/flash-attention
5. Marlin FP16xINT4 kernel repo (requirements): https://github.com/IST-DASLab/marlin
6. Turing microarchitecture reference (Tesla T4, tensor cores, FP16/INT8): https://en.wikipedia.org/wiki/Turing_(microarchitecture)
7. CUDA Toolkit 13.0 release notes (Turing support floor, driver floor): https://docs.nvidia.com/cuda/archive/13.0.0/cuda-toolkit-release-notes/index.html

## 1. Measured server facts

### First SSH probe (measured over SSH, verbatim)

| Item | Measured value |
| --- | --- |
| GPUs | 2x NVIDIA Tesla T4, 15360 MiB each, GPU 0 107 MiB used / GPU 1 3 MiB used, both 0% util |
| Architecture / driver / runtime | Compute capability 7.5 (Turing, sm_75), driver 580.178.04, CUDA 13.0 reported by nvidia-smi |
| Python ML stack | torch 2.11.0+cu130, torchvision 0.26.0+cu130, tensorflow 2.21.0, transformers 5.20.2, numpy 2.1.3, pandas 2.3.3, Python 3.13.16 |
| CPU / memory | 4 vCPU Intel Xeon @ 2.00GHz (2 cores x 2 threads), 31 GiB RAM, 0 swap, ~29 GiB available |
| Disk / OS / identity | 8 TB overlay disk, ~967 GB free; Ubuntu 24.04.4 LTS x86_64, root, host 01c4738f38f8 |

Aggregate VRAM is 2 x 15360 MiB = 30720 MiB = 30 GiB. The two cards are discrete PCIe Tesla T4 parts (no NVLink on T4), so this is not a single unified 30 GiB pool; transparent pooling requires software model/sequence parallelism over PCIe.

### Second SSH probe (measured live on the same host)

These were measured live on a second probe of the same server:

| Item | Measured value |
| --- | --- |
| HF tooling | `hf` CLI installed at /usr/local/bin/hf, version 1.33.0 (huggingface_hub 1.33.0); a newer 2.4.0 is available |
| Installed libs | diffusers 0.42.0 and accelerate 1.15.0 ARE installed |
| Missing libs | bitsandbytes, torchao, xformers, flash-attn, sentencepiece are NOT installed (pip install needed) |
| pip | pip 26.2.2 on Python 3.13 |
| Network | Hugging Face is reachable: `curl -sI https://huggingface.co/MiniMaxAI/MiniMax-H3-Image/resolve/main/model_index.json` returns HTTP/2 307 with a resolve-cache location, so downloads work |
| Session | Live Kaggle Jupyter kernel (jupyter-server PID 12, colab_kernel_launcher PID 50), container uptime ~22 min at probe time; zrok TCP tunnel to localhost:22 runs via /kaggle/working/tunnel_supervisor.sh; a `nvidia-smi -l 1` monitor (PID 53) is already running |
| Env | No KAGGLE_* env vars in the plain SSH shell |

Plan implications from the live probe: install bitsandbytes/torchao at runtime; expect a finite Kaggle session lifetime (plan a checkpoint/resume path); do not rely on flash-attn being present on sm_75; downloads are possible to the ~967 GB-free disk.

## 2. Model architecture facts (source [1])

MiniMax-H3-Image unifies text-to-image and image editing in one checkpoint. The H3-Base design has the audio branch removed. Text prompt and reference images are encoded by the H3 text encoder; reference images are also encoded by the image VAE; all tokens form one packed sequence for a single-stream transformer that predicts the target latent, which the VAE decodes.

- Diffusion transformer (DiT): 33.1B parameters, dense single-stream, 50 layers, hidden size 5376, 56 attention heads, FFN size 14336, 3D multimodal RoPE, same as H3-Omni-Transformer. Weights are BF16; embedding, timestep and output layers are FP32.
- Text encoder: the full Qwen3-VL text encoder of MiniMax-H3, unchanged. The DiT reads hidden states of layer 50.
- Image VAE: CNN encoder plus 2D ViT decoder (24 layers), 16x spatial downsampling, 24 latent channels. The DiT patchifies the latent with a 2x2 patch, so each transformer token covers 32x32 pixels.
- Sampling: distilled to 6 sampling steps (6 NFEs) with no classifier-free guidance.
- Output: about 16 MP at every aspect ratio, from 4096x4096 (1:1) to 6272x2688 (21:9), directly and without an upscaler. Effective working range ~4-20 MP, best near 16 MP.
- Component sizes (decimal GB, source [1]): `transformer/` 66.28 GB; text encoder (in the MiniMax-H3 repo, folder `text_encoder/`) 66.7 GB; `vae/` 2.34 GB FP32; per-step heads 12 MB; tokenizer/processor 23 MB.
- License: minimax-h3-image-community-license-agreement.

Provider recipes listed in the model card (SGLang, vLLM-Omni, diffusers, LightX2V, DiffSynth-Studio, ComfyUI) target accelerators such as H200, RTX PRO 6000 Blackwell and AMD MI350X in the cited vLLM-Omni recipe, not T4.

## 3. Weight-memory math, in GiB

Conversion: GiB = decimal GB * 1e9 / 2^30 (2^30 = 1,073,741,824). Params-based figures: BF16 = 2 bytes/param, FP8 = 1 byte/param, 4-bit = 0.5 byte/param.

### Per component

| Component | Basis (decimal) | Size (GiB) |
| --- | --- | --- |
| DiT BF16 | 33.1B x 2 B = 66.2 GB (~66.28 GB on disk) | 61.7 GiB |
| DiT FP8 | 33.1B x 1 B = 33.1 GB | 30.9 GiB |
| DiT 4-bit | 33.1B x 0.5 B = 16.55 GB | 15.4 GiB |
| Text encoder BF16 | 66.7 GB | 62.1 GiB |
| Text encoder 4-bit | 33.35 GB | 15.5 GiB |
| Image VAE FP32 | 2.34 GB | 2.2 GiB |

### Whole-pipeline totals (weights + VAE; 12 MB/23 MB headers omitted)

| Configuration | Sum | Total |
| --- | --- | --- |
| All BF16 | 61.7 GiB DiT + 62.1 GiB text encoder + 2.2 GiB VAE | 126.0 GiB |
| All FP8 | 30.9 GiB DiT + 31.1 GiB text encoder + 2.2 GiB VAE | 64.1 GiB |
| All 4-bit | 15.4 GiB DiT + 15.5 GiB text encoder + 2.2 GiB VAE | 33.1 GiB |
| Mixed: FP8 DiT + 4-bit text encoder | 30.9 GiB + 15.5 GiB + 2.2 GiB VAE | 48.6 GiB |

### What fits and what does not

Available: 30 GiB aggregate VRAM (2x T4) and ~29 GiB host RAM available. Disk (~967 GB free) is sufficient to store every variant, so download/storage is never the bottleneck; resident memory is.

- All-BF16 126.0 GiB: cannot fit in 30 GiB VRAM, and cannot fit in ~29 GiB host RAM either. Not close.
- All-FP8 64.1 GiB: cannot fit in VRAM or host RAM; also FP8 compute is unavailable on sm_75 (section 4).
- All-4-bit 33.1 GiB: still exceeds 30 GiB VRAM and ~29 GiB available RAM; no sm_75 4-bit tensor-core kernel exists (section 4).
- Mixed FP8 DiT + 4-bit text encoder 48.6 GiB: cannot fit.
- DiT alone at BF16 (61.7 GiB): cannot fit.
- DiT alone at 4-bit (15.4 GiB): nominally just over one card's 15 GiB, but would fit across the two cards with explicit model parallelism; however the text encoder (15.5 GiB at 4-bit) must also be resident for a real request, which pushes past 30 GiB once activations are counted.

Activation memory is additional and material. At 4096x4096 = 16,777,216 px with 32x32 px per token, the latent is 16,384 tokens; adding up to 4096 truncated text tokens gives roughly 20k packed tokens. At hidden 5376 in 16-bit, a single saved activation tensor is ~0.22 GB, so 50 layers of attention/MLP intermediates cost several GiB, and the FP32 VAE decode at 16 MP is itself memory-heavy. Any real fit must budget weights plus activations plus workspace, not weights alone.

## 4. Compute capability sm_75 constraints

Source [3] places NVIDIA T4 at compute capability 7.5 (Turing), below Ampere 8.0, Ada 8.9, Hopper 9.0 and Blackwell 10.0/12.0. Source [6] confirms Turing tensor cores accelerate FP16 and INT8 matrix math; there is no BF16, FP8 or FP4 tensor-core path on Turing. Source [7] states CUDA 13.0 supports all NVIDIA architectures from Turing through Grace Blackwell, and removed offline/library support only for Maxwell, Pascal and Volta; the installed driver 580.178.04 meets the CUDA 13.0 floor of 580.65.06. So basic cuBLAS/torch sm_75 kernels exist, but the specialized kernels this model needs are gated to newer compute capability. This is the decisive constraint: memory is the first wall, kernel availability is the second.

- BF16: native BF16 tensor cores begin at Ampere (sm_80), not Turing. FlashAttention's official README [4] states FA2 supports Ampere/Ada/Hopper and that "bf16 requires Ampere, Ada, or Hopper GPUs"; Turing is redirected to a separate reduced flash-attention-turing repo. On T4, BF16 matmuls fall back to FP32 CUDA cores or FP16 emulation, losing tensor-core throughput; the native BF16 serving path in [1] is not viable. With flash-attn absent (live probe), PyTorch SDPA's flash backend will also be unavailable on sm_75 and will fall back to memory-efficient/math attention.
- FP8: FP8 tensor-core GEMM is an Ada/Hopper-class feature (compute capability 8.9/9.0), not Turing. FlashAttention-3's FP8 forward explicitly requires H100/H800 [4]. T4 can at best store FP8 weights and dequantize to FP16 at compute time; it cannot execute FP8 matmul, so all-FP8 64.1 GiB buys no compute benefit and still will not fit.
- 4-bit (INT4/NF4): the fast Marlin FP16xINT4 kernel explicitly requires NVIDIA GPU with compute capability >= 8.0 (Ampere or Ada) and CUDA >= 11.8 [5], so it cannot run on sm_75. bitsandbytes NF4/FP4 can load on Turing, but it dequantizes to FP16 for the actual matmul, giving memory savings with no 4-bit tensor-core speedup. This makes even a hypothetical 4-bit path slow as well as memory-tight.
- NVFP4: native FP4 is Blackwell-class (compute capability 10.0/12.0 per [3]). The PE checkpoint ships NVFP4 and the PE model card [2] notes that GPUs with native FP4 support run NVFP4 directly while other GPUs use a bitsandbytes FP4 fallback; on T4 there is no native FP4, so NVFP4 is non-viable.
- Engines/kernels verdict for compute capability 7.5: FA2 (sm_80+), Marlin (sm_80+), FP8 kernels (sm_89/sm_90), FA3/FA4 (Hopper/Blackwell) and NVFP4 (Blackwell) are all non-viable. Only generic FP16/FP32 torch and cuBLAS paths, plus bitsandbytes-style dequantize-to-FP16 quantization, can execute on sm_75, and flash-attn is not installed.

## 5. Text encoder and prompt expansion

The text encoder is itself a 33B-class model: the Qwen3-VL encoder from MiniMax-H3, 66.7 GB BF16 (62.1 GiB). It cannot be left in BF16; it must be quantized and/or offloaded alongside the DiT. At 4-bit it is 15.5 GiB, still comparable to a whole T4. Any credible serving design must account for both the DiT and this encoder, not just the 33.1B transformer.

Prompt expansion via MiniMax-H3-Image-PE [2] is not viable on this server. The PE checkpoint is NVFP4, listed at 17.9 GB in the model zoo (about 19 GiB of GPU memory as the FP4 weights), needs native FP4 (Blackwell) or falls back to bitsandbytes FP4, and is a separate 27B-class Qwen-derived model. Running it locally would add another multi-GiB resident model on top of an already over-budget pipeline, and its native NVFP4 path cannot execute on sm_75. Use the hosted H3-Image-Context-IR API for prompt expansion instead, as the main model card [1] documents.

## 6. Verdict

Feasible on this exact server:
- Download and store all weights to the ~967 GB-free disk (HF reachable; hf 1.33.0, diffusers 0.42.0, accelerate 1.15.0 present), and install bitsandbytes/torchao at runtime.
- CPU/FP16 component smoke tests, tokenizer/processor checks, config and latent-token math, and API-driven prompt expansion via H3-Image-Context-IR.
- At most a reduced-resolution, heavily offloaded FP16/4-bit dequantize-to-FP16 experiment that accepts no tensor-core acceleration and no FA2; this is a robustness test, not a faithful 16 MP benchmark of the released model.

Not feasible on this exact server:
- Faithful end-to-end generation at native ~16 MP in BF16, FP8 or 4-bit: the smallest full pipeline is 33.1 GiB, above both 30 GiB VRAM and ~29 GiB available RAM, before activations.
- Any native BF16, FP8, Marlin 4-bit, FA2/FA3/FA4 or NVFP4 compute: all require compute capability >= 8.0 (many >= 8.9 or Blackwell), while T4 is sm_75; flash-attn is not installed anyway.
- Local MiniMax-H3-Image-PE prompt expansion (NVFP4, 17.9 GB) and transparent pooling of the two T4s as one 30 GiB device (no NVLink).

Operational risks: finite Kaggle session lifetime (container uptime ~22 min at probe) means long downloads/inference need a checkpoint/resume path; no KAGGLE_* env vars in the plain SSH shell; a pre-existing `nvidia-smi -l 1` monitor (PID 53) is running. These are process-level concerns, not blockers for the research conclusions above.
