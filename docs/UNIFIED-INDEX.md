# Unified benchmark index

This directory consolidates three completed benchmark projects on the same Kaggle
2x Tesla T4 machine (sm_75, 15 GiB per card, 31 GiB RAM, CUDA 13). Original
folders remain untouched; this is a sorted, read-mostly copy.

## Source projects and authoritative data

| Project | Authoritative results | Raw data |
|---|---|---|
| Image models | `benchmarks/image-models/docs/BENCHMARK-RESULTS.md` | `benchmarks/image-models/benchmark/results.csv`, `optimization-results.csv`, `server-archive/` |
| Video generation | `benchmarks/video-generation/docs/BENCHMARK-RESULTS.md` | `benchmarks/video-generation/benchmark/results.csv`, `server-archive/` |
| LLM / agents / training | `benchmarks/llm-and-training/README.md` | `benchmarks/llm-and-training/extracted.json`, `sources/` |
| MiniMax-H3-Image | `benchmarks/minimax-h3-image/docs/BENCHMARK-RESULTS.md` | `benchmarks/minimax-h3-image/benchmark/results-summary.csv`, `server-archive/` |
| Inkling-2-Mini | `benchmarks/inkling-2-mini/docs/BENCHMARK-RESULTS.md` | `benchmarks/inkling-2-mini/results/inkling_results.csv`, `results/logs/` |

## Cross-project verdicts

The metric differs by task, so the winner is stated per task rather than merged
into one score.

| Task | Winner | Measured result | Protocol |
|---|---|---|---|
| Chat, fastest | LFM2.5-8B-A1B | 119 tokens/second | warm Ollama, Q4_K_M, 32K context |
| Agent, best small | Spark 4B | 3/3 agent tasks passed | native tool protocol, one T4 each |
| Fine-tuning, leanest | Unsloth NF4 | 7.1 GB vs 14.9 GB stock | 8B QLoRA, same data and seed |
| Image, best of both | FLUX.2 klein 4B | 374 images/hour, CLIP 0.3924 | 1024x1024, batch 4 per GPU on both T4s, fixed prompt/seeds |
| Image, highest alignment runner-up | SDXL 1.0 base | CLIP 0.3894, 107 images/hour | same engine and resolution |
| Video, best of both | LTX-Video 2B 0.9.8 distilled | 27 s per warm 49-frame clip at 4 steps, ~11 GiB VRAM, CLIP 0.215-0.234 | 768x512, warm process, fixed prompt |
| Video, highest alignment | CogVideoX-2b | CLIP 0.2645, 1053 s per 49 frames | 720x480, 50 steps |
| Multimodal chat, uncensored | Inkling-2-Mini AD-IQ2_M (AtomicChat) | 26.1 tok/s, vision works at 37.3 s per image chat | llama.cpp b12633, llama-bench -p 512 -n 256 -r 3, one T4 |
| Multimodal chat, quality ceiling | Inkling-2-Mini UD-Q3_K_XL | 24.3 tok/s at 13.9 GiB, highest-bpw quant that fits one T4 | same protocol; no cross-GPU split exists for larger quants |

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

Source notes: personal research and benchmarking documents published at https://blog.sdad.pro/.
