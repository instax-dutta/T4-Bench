# Unified benchmark index

This directory consolidates three completed benchmark projects on the same Kaggle
2x Tesla T4 machine (sm_75, 15 GiB per card, 31 GiB RAM, CUDA 13). Original
folders remain untouched; this is a sorted, read-mostly copy.

## Source projects and authoritative data

| Project | Authoritative results | Raw data |
|---|---|---|
| Image models | `benchmarks/image-models/docs/BENCHMARK-RESULTS.md` | `benchmarks/image-models/benchmark/results.csv`, `optimization-results.csv`, `server-archive/` |
| Video generation | `benchmarks/video-generation/docs/BENCHMARK-RESULTS.md` | `benchmarks/video-generation/benchmark/results.csv`, `server-archive/` |
| MiniMax-H3-Image | `benchmarks/minimax-h3-image/docs/BENCHMARK-RESULTS.md` | `benchmarks/minimax-h3-image/benchmark/results-summary.csv`, `server-archive/` |

## Cross-project verdicts

The metric differs by task, so the winner is stated per task rather than merged
into one score.

| Task | Winner | Measured result | Protocol |
|---|---|---|---|
| Image, best of both | FLUX.2 klein 4B | 374 images/hour, CLIP 0.3924 | 1024x1024, batch 4 per GPU on both T4s, fixed prompt/seeds |
| Image, highest alignment runner-up | SDXL 1.0 base | CLIP 0.3894, 107 images/hour | same engine and resolution |
| Video, best of both | LTX-Video 2B 0.9.8 distilled | 27 s per warm 49-frame clip at 4 steps, ~11 GiB VRAM, CLIP 0.215-0.234 | 768x512, warm process, fixed prompt |
| Video, highest alignment | CogVideoX-2b | CLIP 0.2645, 1053 s per 49 frames | 720x480, 50 steps |

MiniMax-H3-Image is the outlier: it reaches native 4096x4096 but at about
660 s per image (5.5 images/hour), so it is not a throughput winner despite its
resolution advantage.

## Not completed
- LTX-Video 13B NF4: abandoned at 57/93 GB when the container hit its writable-layer quota.
- WanGP: interactive Gradio launcher, no headless reproducible benchmark call.
- Local audio generation: out of scope.

## Sources
- https://huggingface.co/black-forest-labs/FLUX.2-klein-4B
- https://huggingface.co/jbilcke-hf/LTX-Video-2b-0-9-8-distilled-HFIE
- https://huggingface.co/THUDM/CogVideoX-2b
- https://huggingface.co/MiniMaxAI/MiniMax-H3-Image
