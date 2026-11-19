# Inference engines and low-VRAM techniques for MiniMax-H3-Image on 2x Tesla T4 (sm_75)

Raw, source-cited research. Evidence-first; the full benchmark plan and final recommendation live in `docs/`. This leaf file gives the engine/method viability verdicts that the synthesis consumes.

## Scope and constraints

Target server: 2x NVIDIA Tesla T4 15 GB, sm_75 (Turing, compute capability 7.5), 31 GiB host RAM, 4 vCPU, CUDA 13, torch 2.11.0+cu130, Ubuntu 24.04.

- No native BF16 tensor cores. sm_75 has FP16 and INT8 tensor cores only; BF16 and FP8 tensor-core paths are Ampere+/Hopper+ features. Sources: vLLM issue #29743 shows T4 auto-falling back `torch.bfloat16` to `torch.float16` for Qwen3-VL ([GitHub](https://github.com/vllm-project/vllm/issues/29743)); the Alauda CC table lists Turing 7.5 as FP16/INT8 and Ampere 8.0+ as BF16/TF32/FP8 ([source](https://docs.alauda.io/container_platform/4.0/hardware_accelerator/application_development/trouble_shooting/gpu_computer_less_shooting.html)).
- CUDA 13 formally drops pre-Turing, so sm_75 is the floor ([CUDA CC chart](https://gpusmith.com/articles/en/cuda-compute-capability-table-gpu)).
- Weight footprint at BF16 is about 135 GB decimal = **125.7 GiB** (DiT 66.28 GB = 61.7 GiB; Qwen3-VL text encoder 66.7 GB = 62.1 GiB; VAE 2.34 GB = 2.18 GiB). Source for component sizes: SD-Next SDNQ model card ([Hugging Face](https://huggingface.co/SD-Next/MiniMax-H3-Image-SDNQ-uint4-svd-hadamard-dynamic)) and DiffSynth-Studio docs ([GitHub](https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3-Image.md)). 135e9 / 2^30 = 125.73 GiB. This exceeds 2x15 GB VRAM by roughly 8x, so quantization and/or offloading is mandatory.
- Unit convention (per `research/AGENTS.md`): decimal-GB figures from upstream cards are converted to GiB as `GB * 1e9 / 2^30` and labelled GiB below. VRAM-budget claims (e.g. "8 GB VRAM") are kept in the units the upstream source used.

---

## Part A: Engines

### A1. SGLang Diffusion (official)

Source: [SGLang MiniMax-H3-Image cookbook](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3-Image) and [installation guide](https://docs.sglang.io/docs/sglang-diffusion/installation.md); code on [GitHub](https://github.com/sgl-project/sglang).

Official serve command from the brief/cookbook:
```
sglang serve --model-path MiniMaxAI/MiniMax-H3-Image --num-gpus 4 --ulysses-degree 4
```
Install from source:
```
git clone https://github.com/sgl-project/sglang.git
cd sglang
pip install uv
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e "python[diffusion]" --prerelease=allow
```
Relevant documented options and facts:
- `--warmup-mode off` is explicitly documented as skipping startup warmup ("prepares the full grids... `--warmup-mode off` skips this preparation").
- The separate text encoder checkpoint is `MiniMaxAI/MiniMax-H3` (about 33.4B); downloads total about 135 GB. The brief references a `--text-encoder-path` flag; the cookbook page fetched documents the separate checkpoint and points to the [CLI reference](https://docs.sglang.io/docs/sglang-diffusion/api/cli.md) for options but I did not find that exact flag on the page, so treat `--text-encoder-path` as unverified rather than confirmed.
- **Layerwise offload** "streams the DiT, text encoder and VAE decoder blocks from host RAM while preserving native precision... the capacity option for smaller GPUs." Capacity validation used an 8 GiB allocator limit and 10.01 GiB whole-GPU peak on a constrained B300 allocator; "It is not a latency measurement on the listed consumer GPUs."
- **Component offload** and **Layerwise offload** are the two small-GPU paths; Auto keeps all components resident only when each GPU has >=130 GiB available at startup.
- AdaLN precomputation "releases their weights", reducing peak reserved memory by about 24.6-24.7 GiB on one GPU, but only on H200/B300/GB10/RTX PRO 6000 Blackwell; other GPUs keep projection weights by default.
- Ulysses/Ring split the packed sequence, TP shards DiT projections; "choose degrees compatible with the 56 attention heads."
- `min_generation_area` is a request-level integer in [1024, 16777216]; default canvas is 2048x2048; smaller requests are generated larger and resized with LANCZOS.

sm_75 verdict: **non-viable / not supported in practice.** No T4 or sm_75 recipe exists. The hardware table covers B200/GB200, MI355X, H100/H800, RTX PRO 6000, RTX 6000 Ada, RTX 5090/4090, RTX 3090 (24 GB) and "listed 12-48 GB cards" with layerwise offload, but Turing is absent. The DiT uses dense FlashAttention; FP8 attention is SM120/SM121-only and MXFP8 is Blackwell/Hopper; the guide says "use FP8 on older supported GPUs" but does not include sm_75 among measured hardware. 2x T4 without NVLink also breaks the multi-GPU assumptions. Multi-GPU recommendations assume NVLink. Status: official engine, but the MiniMax-H3-Image diffusion path is effectively sm80+ only.

### A2. vLLM-Omni (official)

Source: [vLLM-Omni MiniMax-H3-Image recipe](https://recipes.vllm.ai/MiniMaxAI/MiniMax-H3-Image) and [GitHub repo](https://github.com/vllm-project/vllm-omni).

Official serve command:
```
vllm serve MiniMaxAI/MiniMax-H3-Image \
  --host 0.0.0.0 --num-gpus 4 --usp 4 --text-encoder-tp-size 4 \
  --port 8000 --omni
```
Install:
```
pip install vllm==0.33.0
git clone https://github.com/vllm-project/vllm-omni.git
cd vllm-omni && pip install -e .
```
Key measured profiles (H200) from the recipe:
- 1 GPU, DiT resident + text encoder offloaded: `--num-gpus 1 --diffusion-offload-config '{"mode":"layer","components":["text_encoder"]}'`, peak 73.4 GiB/GPU.
- 1 GPU, DLO both: `--num-gpus 1 --diffusion-offload-config '{"mode":"layer","components":["dit","text_encoder"]}'`, peak **14.7 GiB/GPU**, 8.3 s for 2048^2.
- 2 GPU Ulysses + DLO: `--num-gpus 2 --usp 2 --text-encoder-tp-size 2 --diffusion-offload-config '{"mode":"layer","components":["dit","text_encoder"],"layer_options":{"dit":{"weight_transfer":"allgather"},"text_encoder":{"weight_transfer":"rank-local"}}}'`, peak **12.0 GiB/GPU**, 5.6 s.
- "Keep `resident_layers` at 0"; CFG parallel and HSDP are rejected; "model CPU offload, quantization and cache acceleration are not qualified."

sm_75 verdict: **experimental, unqualified, high risk.** vLLM's general GPU floor is CC 7.5 ([vLLM GPU docs](https://docs.vllm.ai/en/stable/getting_started/installation/gpu)), so T4 technically clears the install floor, but the Qwen3-VL backend used by this model has no Turing support and that feature request was closed as not planned ([GitHub #29743](https://github.com/vllm-project/vllm/issues/29743)). On T4 vLLM auto-casts bf16 to fp16, and SymmMemCommunicator reports "Device capability 7.5 not supported". The recipe's hardware list is h100/h200/b200/gb200/b300/gb300/rtx_pro_6000/mi300x-mi355x; no T4. The only low-VRAM success story is a single RTX 4090 (sm89) community deployment using the 1-GPU DLO command ([RTX 4090 recipe](https://github.com/vllm-project/vllm-omni/blob/main/recipes/MiniMaxAI/MiniMax-H3-Image-4090.md)). DLO layerwise offload is the relevant technique but quantization is explicitly not qualified, so the ~12-15 GiB/GPU peaks are not established on Turing. Official engine, sm75 status unverified and likely broken for the Qwen3-VL encoder.

### A3. diffusers (official library)

Source: [diffusers MiniMax-H3-Image docs](https://huggingface.co/docs/diffusers/main/en/api/pipelines/minimax_h3_image) and [GitHub](https://github.com/huggingface/diffusers).

The integration is Modular Diffusers blocks with `ComponentsManager` auto offload:
```
pip install -U diffusers
```
```python
import torch
from diffusers import ComponentsManager, ModularPipeline

manager = ComponentsManager()
manager.enable_auto_cpu_offload(device="cuda")
pipe = ModularPipeline.from_pretrained("MiniMaxAI/MiniMax-H3-Image", components_manager=manager)
pipe.load_components(dtype=torch.bfloat16)
```
Documented facts: transformer and text encoder are "about 62 GB each in bfloat16 and do not fit on an 80 GB GPU together"; a 4736x3552 image peaks at about 65 GB with auto offload. `min_generation_area` defaults to 4194304; "Pass 1024 to always generate at the requested size." The classic `DiffusionPipeline.from_pretrained(..., dtype=torch.bfloat16, device_map="cuda")` form in the brief is the non-modular path; the docs for this specific model use `ModularPipeline` + `ComponentsManager`. Offload helpers available in diffusers generally are `enable_model_cpu_offload()` and `enable_sequential_cpu_offload()`; the modular equivalent used here is `manager.enable_auto_cpu_offload(device="cuda")`. Quantization configs: `TorchAoConfig("int8_weight_only")`, `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=...)` ([diffusers quantization blog](https://huggingface.co/blog/diffusers-quantization), [bnb doc](https://huggingface.co/docs/diffusers/en/quantization/bitsandbytes)).

sm_75 verdict: **viable with FP16 compute + quantization + sequential offload**, but the stock recipe is not. On T4 use `dtype=torch.float16` (not bfloat16) because there are no BF16 tensor cores. ~65 GB peak for auto offload still exceeds 15 GB; must combine sequential/CPU offload with int8/NF4 weight-only quantization. bnb NF4 works from Pascal and `LLM.int8()` from Turing ([bnb hardware table](https://github.com/bitsandbytes-foundation/bitsandbytes)), so weight-only NF4/int8 with fp16 compute is sm75-compatible. Note that int8/NF4 are dequantized to fp16 for the GEMM, so storage drops but compute stays fp16. Official engine and official quant backends; the exact combination for H3-Image on T4 is not measured upstream.

### A4. DiffSynth-Studio (official, strongest explicit low-VRAM support)

Source: [DiffSynth-Studio GitHub](https://github.com/modelscope/DiffSynth-Studio) and the [MiniMax-H3-Image model doc](https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3-Image.md). Advertised "low VRAM inference & training"; the README's Nov 10 2026 entry says MiniMax-H3-Image support includes "low VRAM inference, and full/LoRA training", and EntroPack quantized models from 8-bit down to extreme 3-bit, with the 3-bit package shrinking the DiT from 40.2 GB in BF16 to **7.67 GB (7.14 GiB)**.

Install:
```
git clone https://github.com/modelscope/DiffSynth-Studio.git
cd DiffSynth-Studio
pip install -e .
pip install "diffsynth[quant]"
# exact pinned versions from the doc:
pip install diffsynth==2.2.2
pip install cupy-cuda13x
```
Exact low-VRAM flags/config from the official doc:
- The `vram_limit` parameter: `vram_limit=torch.cuda.mem_get_info("cuda")[1] / (1024 ** 3) - 2`, and in the 24 GB recipe `vram_limit=20`.
- `ModelConfig` per-component `vram_config` dict: `offload_dtype/offload_device`, `onload_dtype/onload_device`, `preparing_dtype/preparing_device`, `computation_dtype/computation_device`. For the 24 GB / 32 GB RAM recipe, the DiT uses `quant_vram_config` (bf16 on CPU, preparing/computing on cuda) and the text encoder uses `offload_vram_config` with `"offload_dtype": "disk", "offload_device": "disk"` (disk offload streaming).
- Official measured statement: "The low VRAM example streams the text encoder and the VAE from disk and stores the transformer and the per-step output heads as int8 in host memory: generating a 4096x4096 image and then editing it takes about 4.5 minutes in total including model loading, and peaks at about **38 GiB of VRAM**" (H20). That still exceeds 15 GB, so the EntroPack recipes are needed for T4.
- RTX 4090 Option 1 (24 GB VRAM + 32 GB RAM): INT8 ConvRot DiT `models/dit_8bit_int8.safetensors` + text encoder `text_encoder_int8_convrot.safetensors` disk-offloaded + `vae_int8.safetensors`, `vram_limit=20`, "image quality is almost lossless."
- RTX 4090 Option 2 (24 GB VRAM + 8 GB RAM): "8.5-bit, 5-bit and 2.9-bit mixed quantization that averages 3 bits per parameter, with no offload at all, which is the fastest recipe when generating many images" (`dit_extreme_3bpp.safetensors`, `text_encoder_3bpp.safetensors`).
- Also supports `tiled=True` VAE (256 px tiles, >=64 overlap) to cut VAE decode memory; `tiling=False` "needs far more VRAM."
- The H20 fast path registers a custom `sage_attention_h20_fast` kernel using `sageattn_qk_int8_pv_fp8_cuda_sm90` — this is sm90-specific and does not apply to T4.

sm_75 verdict: **highest official viability.** The VRAM manager explicitly schedules disk <-> CPU <-> GPU, and NF4/int8 weight-only formats dequantize to fp16 compute that Turing supports. The upstream NF4 model for video is documented as running "from 8 GB of VRAM" ([awesome index](https://github.com/MiniMax-AI/awesome-minimax-h3-integration)). The 3bpp EntroPack DiT is 7.14 GiB and a matching 3bpp text encoder exists. 31 GiB host RAM is enough for the disk/CPU streaming design (the doc's hardest option uses 8 GB RAM). Caveat: some fast attention kernels and cu130-specific ConvRot ops are arch-specific; use the plain int8/NF4 path with fp16 compute. Official engine, official low-VRAM flags, sm75-compatible weight formats.

### A5. LightX2V (official)

Source: [LightX2V GitHub](https://github.com/ModelTC/LightX2V). November 11 2026 news: "We now support MiniMax-H3-Image... We support TP/SP parallelism and CPU offload." Core features listed: "Quantization & Optimized Kernels: W8A8 (INT8 / FP8) and W4A4 (NVFP4)... Hierarchical Offloading: Manage weights across disk, CPU, and GPU with model-level and block-level offloading... Feature Caching: TeaCache, MagCache, TaylorSeer... Parallel Inference: TP, SP, CFG parallelism... Variable-Resolution Inference."

Install:
```
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
pip install -r requirements.txt
```
- Usage guide: [scripts/minimax_h3_image/README.md](https://github.com/ModelTC/LightX2V/blob/main/scripts/minimax_h3_image/README.md); [low-resource deployment doc](https://lightx2v-en.readthedocs.io/en/latest/deploy_guides/for_low_resource.html), [offload doc](https://lightx2v-en.readthedocs.io/en/latest/method_tutorials/offload.html).
- W4A4/NVFP4 requires Blackwell-class hardware (FP4 tensor cores), so it is **non-viable on sm75**. W8A8 INT8 and the hierarchical/block-level CPU+disk offload are the sm75-relevant levers.
- LightX2V is the home of the MiniMax-H3 Turbo 4-step/8-step distilled LoRAs ([weights](https://huggingface.co/lightx2v/Minimax-h3-Turbo)), though those are video-oriented.

sm_75 verdict: **viable with INT8 W8A8 + CPU/disk offload**, experimental on this exact model; NVFP4 path non-viable. Official engine, active community.

### A6. ComfyUI + ComfyUI-GGUF (official engine, community quant nodes)

Sources: [ComfyUI MiniMax-H3-Image tutorial](https://docs.comfy.org/tutorials/image/minimax/minimax-h3-image), [ComfyUI-GGUF GitHub](https://github.com/city96/ComfyUI-GGUF), [awesome index](https://github.com/MiniMax-AI/awesome-minimax-h3-integration).

ComfyUI has native MiniMax-H3-Image support (templates need ComfyUI 0.45.0+, template pack 0.11.104+). Official T2I and edit templates exist ([workflow templates](https://github.com/Comfy-Org/workflow_templates)); the T2I template "opens at 4 MP on a square canvas, deliberately below the model's native resolution so low-VRAM machines do not run out of memory."

Official Comfy-Org single-file weights (decimal GB -> GiB):
- DiT `minimax_h3_image_pruned_int8_convrot.safetensors` 20.97 GB = **19.53 GiB**; alternative `pruned_fp8_scaled` 20.96 GB = 19.52 GiB; `pruned_w6a8` 15.98 GB = **14.88 GiB**.
- Text encoder `qwen3vl_32b_minimax_h3_int8_convrot.safetensors` 25.28 GB = **23.54 GiB**.
- VAE `minimax_h3_image_vae_fp16.safetensors` 1.17 GB = 1.09 GiB.
- Lighter prompt expander `qwen3.5_9b_w4a8_gptq.safetensors` 7.34 GB = 6.84 GiB (the official PE is Qwen3.8-27B FP4).
- A [community wiki/forum thread](https://www.reddit.com/r/comfyui/comments/1xfrdh3/minimax_h3_on_1216_gb_the_seven_speedups_compared) recommends int8_convrot on cu130 PyTorch and says "If VRAM is tight, step down a size: CPU offload costs more than precision tradeoffs."

GGUF / block-swap install:
```
git clone https://github.com/city96/ComfyUI-GGUF ComfyUI/custom_nodes/ComfyUI-GGUF
pip install --upgrade gguf
```
ComfyUI VRAM flags from the [startup-flags doc](https://docs.comfy.org/development/comfyui-server/startup-flags):
```
python main.py --lowvram        # runs text encoders on CPU when dynamic VRAM is off
python main.py --novram         # minimal VRAM usage when --lowvram is not enough
python main.py --reserve-vram 1.5
```
Async weight offloading and pinned memory are on by default for NVIDIA ([ComfyUI blog](https://blog.comfy.org/p/new-comfyui-optimizations-for-nvidia)), which specifically helps when "a model's weights cannot fully fit on the VRAM of a card." **Block swapping** (a custom-node technique, e.g. the WAN Block Swap node, and also used in diffusion-pipe) is community/experimental: see [ComfyUI issue #11081](https://github.com/Comfy-Org/ComfyUI/issues/11081) and the [diffusion-pipe #533 forum report](https://github.com/tdrussell/diffusion-pipe/issues/533) where `blocks_to_swap` was tried. A [forum report](https://www.reddit.com/r/StableDiffusion/comments/1wkdnaq/suggestions_for_minimax_for_low_vram_3050_4gb) recommends "comfyui model manager unload nodes to pull the text encoder model, use a smaller TE model, then try a smaller quantization."

sm_75 verdict: **best overall viability.** int8_convrot uses INT8 tensor cores (Turing has them) and GGUF quants dequantize to fp16, both sm75-compatible. FP8 (`fp8_scaled`), NVFP4, MXFP8 and Comfy-Kitchen FP4 kernels are **non-viable on sm75** and must be avoided. With 2x15 GB, the 14.88 GiB W4A8 DiT + a heavily quantized text encoder + `--lowvram`/block swapping is the only combination that plausibly fits. Official engine, community quant ecosystem.

---

## Part B: Low-VRAM techniques (what / source / command / saving / cost / sm75)

### B1. CPU offload / sequential offload / model offload scheduling
- What: move components (or individual blocks) between GPU and host RAM/disk on demand.
- Sources: [diffusers ComponentsManager](https://huggingface.co/docs/diffusers/main/en/api/pipelines/minimax_h3_image), [SGLang layerwise offload](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3-Image), [DiffSynth VRAM management](https://diffsynth-studio-doc.readthedocs.io/en/latest/Pipeline_Usage/VRAM_management.html), [ComfyUI flags](https://docs.comfy.org/development/comfyui-server/startup-flags), [LightX2V offload](https://lightx2v-en.readthedocs.io/en/latest/method_tutorials/offload.html).
- Commands: `manager.enable_auto_cpu_offload(device="cuda")`; diffusers `pipe.enable_sequential_cpu_offload()` / `pipe.enable_model_cpu_offload()`; SGLang layerwise offload + `--minimax-h3-adaln-online true` (Precompute) and `--warmup-mode off`; DiffSynth `vram_limit=20` + `offload_vram_config` with `"offload_device":"disk"`; ComfyUI `--lowvram --novram`.
- Saving: SGLang layerwise offload validated with an 8 GiB allocator limit / 10.01 GiB whole-GPU peak; vLLM DLO 12.0-14.7 GiB/GPU; DiffSynth 38 GiB peak for 4K T2I+edit. Speed cost is large: DiffSynth reports about 4.5 min for 4K T2I+edit including loading; vLLM DLO 8.3 s vs 3.2 s resident.
- sm75: **yes** (host RAM movement is arch-agnostic; compute stays fp16). Quality: lossless (same weights/precision). Official everywhere.

### B2. Block swapping / block swap
- What: keep only a subset of transformer blocks resident, swapping the rest to CPU RAM; the ComfyUI custom-node equivalent of sequential offload.
- Sources: [ComfyUI issue #11081](https://github.com/Comfy-Org/ComfyUI/issues/11081), [diffusion-pipe #533](https://github.com/tdrussell/diffusion-pipe/issues/533), [awesome index GGUF/quant nodes](https://github.com/MiniMax-AI/awesome-minimax-h3-integration).
- Command/flag: no stock ComfyUI flag; community nodes expose a `blocks_to_swap` / block-swap parameter. The [diffusion-pipe forum report](https://github.com/tdrussell/diffusion-pipe/issues/533) found `blocks_to_swap = 48` failed with WSL DXG/GPADL errors and the working config used `activation_checkpointing = true` with swapping disabled; that was a training context, so inference block swap remains community/experimental.
- Saving: proportional to blocks swapped; 50-block DiT means large savings. Cost: PCIe transfer overhead and potential WSL/driver issues.
- sm75: **yes in principle** (pure weight movement), but not officially supported for H3-Image. Community/experimental.

### B3. Quantized text encoder (biggest single lever: 62.1 GiB -> ~7-24 GiB)
- What: replace the BF16 Qwen3-VL-32B encoder (66.7 GB = 62.1 GiB) with an int8/FP4/GGUF/projected encoder.
- Sources: [ComfyUI tutorial](https://docs.comfy.org/tutorials/image/minimax/minimax-h3-image), [Woovee LowVRAM repo](https://huggingface.co/Woovee/MiniMax-H3-Image-LowVRAM), [awesome index](https://github.com/MiniMax-AI/awesome-minimax-h3-integration).
- Concrete options: Comfy-Org `qwen3vl_32b_minimax_h3_int8_convrot.safetensors` 25.28 GB = **23.54 GiB**; Woovee `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` 15.69 GB = **14.61 GiB** (the [medium guide](https://medium.com/@hyperai/no-gpu-no-problem-a-complete-minimax-h3-deployment-guide-09ec61624ca8) notes "it does NOT require a Blackwell GPU - it is an AWQ-quantized weight, not FP4 hardware compute", but FP4 compute kernels are still Blackwell-only, so treat as sm75-risky); GGUF Q2_K encoder **7.91 GiB** ([realrebelai](https://huggingface.co/realrebelai/MiniMax-H3-GGUFs)); `ComfyUI-ClipProj` swaps the 32B encoder for Qwen3-VL 4B/8B "down to 4.5 GB" = 4.19 GiB; DiffSynth `text_encoder_int8_convrot.safetensors` and `text_encoder_3bpp.safetensors` with disk offload.
- Cost: quantization changes text conditioning; NVFP4/FP4 and 3bpp can noticeably degrade prompt adherence / reference identity. The 4B/8B projection is explicitly a different, weaker encoder ([forum discussion](https://www.reddit.com/r/StableDiffusion/comments/1vkk500/minimax_h3_with_a_4b_or_8b_text_encoder_instead)).
- sm75: int8_convrot / GGUF / NF4 / 3bpp **yes**; NVFP4/FP8/MXFP8 **non-viable** (no FP4/FP8 tensor cores). Mix: official weights + community nodes.

### B4. Loading only needed encoder layers / "DiT layer 50 hidden states"
- What: does the pipeline need all 50 DiT/encoder blocks resident?
- Source: [SGLang cookbook](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3-Image) says "The pipeline loads only the encoder layers needed by this release" and that AdaLN precomputation "releases their weights"; [akhaliq 2-step card](https://huggingface.co/akhaliq/minimax-h3-image-pdmd-2step) describes its LoRA as rank 128 "over attention + FFN of all 50 blocks."
- Verdict: no engine exposes a "load only layer-50 hidden states" flag. All 50 blocks must be *computed* sequentially, but they do not need to be *simultaneously resident*: layerwise offload, sequential CPU offload, block swapping and SGLang's AdaLN-weight release are the supported ways to avoid holding all of them in VRAM. Any claim of skipping layers is unsupported by the sources fetched. Official mechanisms exist; the specific "layer 50 only" shortcut is unverified/non-existent.

### B5. GGUF Q4/Q5/K-quants with ComfyUI-GGUF
- What: llama.cpp-style variable-bitrate weight quants for DiT and text encoder.
- Source: [ComfyUI-GGUF GitHub](https://github.com/city96/ComfyUI-GGUF): "transformer/DiT models such as flux seem less affected by quantization. This allows running it in much lower bits per weight variable bitrate quants on low-end GPUs. For further VRAM savings, a node to load a quantized version of the T5 text encoder is also included."
- Command: `git clone https://github.com/city96/ComfyUI-GGUF ComfyUI/custom_nodes/ComfyUI-GGUF` then `pip install --upgrade gguf`; use "Unet Loader (GGUF)" and "*CLIPLoader (gguf)" nodes. Available H3 GGUFs: `unsloth/MiniMax-H3-GGUF` Q2_K 6.26 GiB to Q8_0, `Abiray/MiniMax-H3-GGUF` Q3_K_S to Q8_0, `realrebelai` Q4_K_M, `leejet` Q2_K/Q4_K_M ([awesome index](https://github.com/MiniMax-AI/awesome-minimax-h3-integration)).
- Saving: Q4/Q5 roughly 4-5x weight reduction vs BF16; cost: quality loss and dequant-to-fp16 compute overhead. sm75: **yes** (dequantizes to fp16; no FP8/FP4 tensor core needed). Community/experimental (README says "very much WIP").

### B6. torchao / bitsandbytes NF4 / int8 weight-only
- What: weight-only low-bit formats dequantized to fp16 at GEMM time.
- Sources: [diffusers quantization blog](https://huggingface.co/blog/diffusers-quantization), [bnb diffusers doc](https://huggingface.co/docs/diffusers/en/quantization/bitsandbytes), [bnb hardware table](https://github.com/bitsandbytes-foundation/bitsandbytes), [quant benchmark](https://virtuslab.com/blog/ai/diffusion-models-quantization-benchmark).
- Commands:
```
pip install bitsandbytes
pip install torchao
```
```python
from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig
from transformers import BitsAndBytesConfig as TransformersBitsAndBytesConfig
# bnb 4-bit NF4, compute dtype fp16 on Turing:
# bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16
# torchao: DiffusersTorchAoConfig("int8_weight_only"), TransformersTorchAoConfig("int8_weight_only")
```
- Saving: benchmark table shows int8 ~0.55x VRAM vs fp16, NF4 ~0.30x, int4 ~0.27x; "slower" than fp16 in that benchmark. float8_weight_only is fp8 and **non-viable on sm75**.
- sm75: bnb NF4 supported from Pascal, `LLM.int8()` from Turing; torchao int4/int8 weight-only uses dequant-to-fp16 and is sm75-compatible. Official backends; exact H3-Image combination unmeasured.

### B7. SDNQ uint4 with hadamard (SVD + Hadamard)
- What: 4-bit SDNQ quantization with SVD compression and Hadamard transform, applied to both DiT and text encoder.
- Sources: [SD-Next MiniMax-H3-Image-SDNQ-uint4-svd-hadamard-dynamic](https://huggingface.co/SD-Next/MiniMax-H3-Image-SDNQ-uint4-svd-hadamard-dynamic), [SDNQ dev plan / GitHub](https://github.com/EnragedAntelope/comfyui-sdnq/blob/main/SDNQ_ComfyUI_Development_Plan.md), [comfyui-sdnq extension](https://comfy.icu/extension/EnragedAntelope__comfyui-sdnq). Loads with `ModularPipeline.from_pretrained` in diffusers "once `sdnq` is imported"; SDNQ "registers into diffusers and transformers via import side-effects", supports int8/int6/int4/uint4 with optional SVD, CUDA/ROCm/Intel/CPU, "50-75% VRAM savings."
- Command: `pip install git+<sdnq repo>` (per extension page); import `from sdnq import SDNQConfig` then `AutoModel.from_pretrained(path)`.
- Saving: 50-75% VRAM savings claimed; uint4 is maximum. Cost: quality loss, and the `comfyui-sdnq` node is **deprecated/archived** per its GitHub README. sm75: uint4 dequantizes to fp16, so **yes**; community/experimental.

### B8. min_generation_area / smaller canvas + LANCZOS resize
- What: generate at a smaller pixel canvas then resize up; activation memory scales with canvas area.
- Sources: [SGLang](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3-Image) (range 1024-16777216, default 2048^2), [vLLM recipe](https://recipes.vllm.ai/MiniMaxAI/MiniMax-H3-Image) (`extra_args.min_generation_area`, 32^2 to 4096^2), [diffusers](https://huggingface.co/docs/diffusers/main/en/api/pipelines/minimax_h3_image) (pass 1024).
- Commands: request `min_generation_area: 1024` (SGLang/vLLM) or `pipe(..., min_generation_area=1024)`; `extra_args.min_generation_area`. Canvas sides must be multiples of 32.
- Saving: 1024^2 is 1/4 the pixels of 2048^2, so roughly 4x less attention/activation memory and compute. SGLang warns "Reducing it changes the generation workload and potentially image quality; it is not a lossless acceleration of the default recipe." Official, sm75-agnostic: **yes**.

### B9. Sequence parallelism across 2 GPUs / Ulysses
- What: split the packed sequence across GPUs instead of replicating; Ulysses uses all-to-all, TP shards projections.
- Sources: [SGLang](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3-Image) (`--ulysses-degree 4`, "Choose degrees compatible with the 56 attention heads"; Ulysses2 measured on 2x H200), [vLLM recipe](https://recipes.vllm.ai/MiniMaxAI/MiniMax-H3-Image) (`--usp 4`, 2-GPU Ulysses + DLO 12.0 GiB/GPU), [LightX2V](https://github.com/ModelTC/LightX2V) (SP/TP).
- Commands: SGLang `--num-gpus 2 --ulysses-degree 2` (degree must divide 56); vLLM `--num-gpus 2 --usp 2 --text-encoder-tp-size 2` plus DLO config.
- Saving: roughly halves per-GPU activations and can halve weight memory with TP; Ulysses still replicates weights. Cost: all-to-all/AllGather over PCIe on non-NVLink T4 pair is slow; SGLang's multi-GPU recipes assume NVLink. Official, but sm75 2x T4 performance is unverified and likely poor. Functional: **yes**; efficient: no.

### B10. Cold sequential load of components
- What: run the text encoder first, free it, then load DiT, then VAE, so peak is one component at a time.
- Sources: diffusers `ComponentsManager` moves "each component onto the accelerator when a block needs it"; DiffSynth two-stage training "at no point are the transformer, the text encoder and the VAE resident together" ([doc](https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3-Image.md)); [forum report](https://www.reddit.com/r/StableDiffusion/comments/1wkdnaq/suggestions_for_minimax_for_low_vram_3050_4gb) suggests ComfyUI model-manager unload nodes; LightX2V hierarchical disk/CPU/GPU offload.
- Command: DiffSynth `offload_models` / `offload_vram_config` with disk staging, or manual `del pipe.text_encoder; torch.cuda.empty_cache()` between phases in diffusers. No single official "cold load" flag for inference; it emerges from offload configs. sm75: **yes**, arch-agnostic. Official mechanisms + forum practice.

### B11. 2-step / 6-step distilled variants
- What: reduce denoising evaluations. Stock is fixed at 6 steps (one PDD output head per step, no CFG).
- Sources: [akhaliq pDMD 2-step card](https://huggingface.co/akhaliq/minimax-h3-image-pdmd-2step), [2-step Space](https://huggingface.co/akhaliq/minimax-h3-image-2step), [LightX2V Turbo](https://huggingface.co/lightx2v/Minimax-h3-Turbo), [awesome index adapters](https://github.com/MiniMax-AI/awesome-minimax-h3-integration).
- Command: use the merged one-file ComfyUI checkpoint or load the rank-128 LoRA over all 50 blocks, then run 2/3/4 steps with scheduler `simple`, CFG 1. The Space gives "~1 MP previews... a 2-step frame lands in ~1-1.5 s."
- Saving: ~3x fewer denoising steps (compute/activation time), but **does not shrink the 125.7 GiB weight footprint** - the DiT and encoder still need quantization/offload. Cost: 2-step can look "soft, low-contrast and unfinished" without the LoRA; with it, quality at 4 steps is near the 8-step baseline. Community/experimental, sm75: **yes** (LoRA is just weights; compute is fp16).

---

## Install commands reference (literal)

```
# SGLang
git clone https://github.com/sgl-project/sglang.git && cd sglang && pip install -e "python[diffusion]"

# vLLM-Omni
pip install vllm==0.33.0
git clone https://github.com/vllm-project/vllm-omni.git && cd vllm-omni && pip install -e .

# diffusers + quant backends
pip install -U diffusers && pip install bitsandbytes && pip install torchao

# DiffSynth-Studio
git clone https://github.com/modelscope/DiffSynth-Studio.git && cd DiffSynth-Studio && pip install -e .
pip install "diffsynth[quant]" && pip install diffsynth==2.2.2 && pip install cupy-cuda13x

# LightX2V
git clone https://github.com/ModelTC/LightX2V.git && cd LightX2V && pip install -r requirements.txt

# ComfyUI GGUF nodes
git clone https://github.com/city96/ComfyUI-GGUF ComfyUI/custom_nodes/ComfyUI-GGUF && pip install --upgrade gguf
```

---

## Ranked viability table (exact server: 2x T4 15 GB, sm_75, 31 GiB RAM)

| Rank | Engine / method | Peak/footprint on this server | sm_75 status | Official vs community | Why |
|---|---|---|---|---|---|
| 1 | DiffSynth-Studio + EntroPack INT8/3bpp + disk/CPU VRAM manager | DiT 7.14 GiB (3bpp) or int8 ~19 GiB; text encoder int8/3bpp disk-offloaded; NF4 floor 8 GB VRAM | Works (fp16 compute; avoid sm90 attention) | Official flags + official weights | Only engine with explicit, documented low-VRAM flags and 3-bit quants for this exact model; fits 15 GB |
| 2 | ComfyUI + Comfy-Org W4A8 (14.88 GiB) / GGUF Q4 + quantized text encoder + `--lowvram` / block swapping | W4A8 DiT 14.88 GiB + ~7-23 GiB encoder offloaded; 4 MP canvas | Works for int8/GGUF; FP8/NVFP4 non-viable | Official engine, community quants | Largest ecosystem; 8 GB VRAM reports on forum; block swapping helps but is community |
| 3 | diffusers ModularPipeline + sequential CPU offload + bnb NF4 / torchao int8 | ~65 GB stock auto-offload; NF4 ~0.30x weights; needs sequential offload to hit 15 GB | Works with fp16 + weight-only NF4/int8 | Official lib/backends | Clean API but no H3-Image-on-T4 measurement; must assemble quant+offload yourself |
| 4 | LightX2V INT8 W8A8 + hierarchical CPU/disk offload | Model-level/block-level offload; NVFP4 path non-viable | Works for INT8; NVFP4 non-viable | Official engine | TP/SP/CPU offload supported for H3-Image; sm75 unmeasured |
| 5 | vLLM-Omni DLO layerwise offload | 12.0-14.7 GiB/GPU measured on H200/4090 | Unqualified; Qwen3-VL Turing backend closed as not planned | Official engine, community 4090 report | Peaks look ideal but quantization not qualified and sm75 encoder unsupported |
| 6 | SGLang layerwise offload + `min_generation_area` | 8 GiB allocator / 10.01 GiB peak on B300 (not sm75) | Non-viable in practice | Official, no sm75 recipe | FlashAttention/FP8 and NVLink assumptions exclude T4 |
| Method: min_generation_area 1024 | any engine | ~4x less activation memory at 1024^2 | Yes | Official | Cheap, lossy; combine with ranks 1-4 |
| Method: 2-step pDMD LoRA | any ComfyUI/diffusers path | No weight saving; ~3x fewer steps | Yes | Community | Speeds preview; does not solve the 125.7 GiB footprint |

Non-viable on sm_75 (marked per `research/AGENTS.md`): NVFP4 / FP4 tensor-core kernels (Blackwell only), FP8 and MXFP8 / FP8 attention (Hopper/SM120 only), Comfy-Kitchen FP4 attention, SGLang ROCm/AITER and Apple MLX paths (wrong platform), SGLang custom `sageattn_qk_int8_pv_fp8_cuda_sm90` kernel (sm90 only).

## Recommended primary + fallback (leaf-level engine/method verdict)

- **Primary: DiffSynth-Studio** with the EntroPack INT8 ConvRot DiT + int8/3bpp text encoder streamed from disk via `offload_vram_config`, `vram_limit` set from free VRAM, FP16 compute, tiled VAE, and `min_generation_area` lowered to cut activations. Rationale: it is the only engine with documented, model-specific low-VRAM flags and 3-bit weights that fit 15 GB, and its weight formats dequantize to fp16 which Turing supports.
- **Fallback: ComfyUI** with `minimax_h3_image_pruned_int8_convrot` (19.53 GiB) or the W4A8 build (14.88 GiB), a GGUF/int8 quantized text encoder, T2I template at 4 MP, `--lowvram` and block swapping / model unload nodes. Rationale: biggest forum and GitHub evidence base for low-VRAM H3-Image, and int8/GGUF are sm75-safe where FP8/NVFP4 are not. Use the 2-step pDMD LoRA only for previews, never as the memory solution.
- Avoid SGLang and vLLM-Omni as primaries on this server: no sm75 recipe (SGLang) or unqualified sm75 encoder backend (vLLM-Omni).

Note on DOX: this is the evidence-based engine/method verdict required by the leaf task; the consolidated benchmark plan and final sign-off remain in `docs/` per `research/AGENTS.md`.

---

Skipped: I did not benchmark any command on the T4 pair (this is paper research only), and I did not verify the `--text-encoder-path` SGLang flag or measure int8_convrot throughput on sm_75. Risk: all "fits in 15 GB" claims are extrapolated from H20/4090/3090 measurements, so a real OOM on first run is likely and `vram_limit`/block-swap counts must be tuned empirically.
