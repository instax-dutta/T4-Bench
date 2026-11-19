# Best Video Generation Models on Kaggle 2x T4 GPU

## TL;DR
On 2x T4 (16 GB each, Turing, no BF16/FP8), the only realistic video models are
distilled/quantized ones. Expect **minutes per clip**, not seconds.

## Ranked options

### 1. LTX-Video 13B Distilled (NF4) — BEST overall
- 13B params compressed to ~8.5 GB VRAM via NF4
- Dual-GPU split: cuda:0 = transformer (~8.5 GB), cuda:1 = T5-XXL encoder + VAE decode
- 4–6 min per 10s clip @ 768×512, 7 steps, CFG 1.0
- 22 swappable LoRA styles, image-to-video, prompt enhancement
- NF4 loses fine detail (text overlays especially)
- Repo: DamnKuldeep/ltxv-13b-distilled-free-gpu-pipeline

### 2. WanGP (multi-model launcher)
- Single notebook exposes Wan 2.2/2.1, LTX, Hunyuan, CogVideoX, Qwen, Z-Image, Kandinsky 5, etc.
- `--profile 4` tuned for T4 15 GB
- ~9–15 min per video on T4
- Repo: kayas881/WanGP-Kaggle
- Best if you want to A/B multiple models without separate setups

### 3. CogVideoX-2b (scene-stitched pipeline)
- 2b params, ~11 GB VRAM with CPU offload + VAE tiling
- Native ~6s (49 frames) @ 720×480 per generation; stitch scenes with ffmpeg crossfade
- Apache 2.0, fully automated multi-scene pipeline available
- ~several min per 6s clip; 10 scenes = 30–60 min
- Repo: alirezayaned/AI-Video-Generation

### 4. LTX-Video 0.9.8 (single T4 friendly)
- Recommended by community for 2x T4 (16 GB, no BF16)
- ~3–6 min per 4s clip @ 768×512
- Use FP16 (not FP8 — T4 has no FP8 HW)

## Avoid on T4
- Wan 2.2 TI2V-5B — wants 24 GB; FP8 bottleneck on Turing
- Any BF16/FP8-native model without quantization
- HunyuanVideo full — too heavy; only the distilled 1.5 variant via WanGP

## Throughput reality check
- T4 = 2018 Turing, ~10× slower than A100 for these models
- 4–6 min/clip is the floor; plan 25 GPU-hr/week budget accordingly
- Kaggle 12-hr session cap → checkpoint intermediate frames

## Recommendation
Start with **LTX-Video 13B Distilled via DamnKuldeep's pipeline** (best quality/throughput on 2x T4).
If you want to explore, use **WanGP** to try Wan 2.2 / Hunyuan 1.5 / CogVideoX in one notebook.
For fully automated long-form (minutes of video), use the **CogVideoX-2b scene-stitcher** pipeline.

## Notes
- T4 has no BF16/FP8 hardware → always use FP16 or NF4 quantized variants
- 2x T4 doesn't double single-clip speed; second GPU is used for text encoder/VAE offload
- Audio: add AudioLDM2 (non-commercial CC-BY-NC-SA) or Kokoro TTS separately
