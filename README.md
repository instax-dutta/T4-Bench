# T4-Bench

Measured benchmarks of image, video, language, agent and fine-tuning workloads on a Kaggle notebook with **2x Tesla T4 GPUs**.

**Live site:** https://t4b.sdad.pro
**Source notes:** https://blog.sdad.pro

## Why this exists

Most model comparisons assume large GPUs. T4-Bench asks a narrower question: what actually works well on two free Kaggle T4s (15 GB each, Turing/sm_75, no BF16 or FP8)? Every result here comes from a real run on that machine, with the prompt, seed, quant, resolution and timing method recorded in the source reports.

## Headline results

| Task | Winner | Measured result |
|---|---|---|
| Chat / coding | LFM2.5-8B-A1B | 119 tokens/second |
| Multimodal chat / vision | Inkling-2-Mini AD-IQ2_M | 26 tokens/second, 37 s per image chat |
| Small agent | Spark 4B | 3/3 agent tasks passed |
| Fine-tuning | Unsloth NF4 | 7.1 GB vs 14.9 GB stock |
| Image generation | FLUX.2 klein 4B | 374 images/hour at 1024×1024 |
| Short video | LTX-Video 2B distilled | 27.6 s per warm 49-frame clip |
| Long context | Ternary 27B on 2 GPUs | 22.9 tokens/second |

## Hardware

- 2x NVIDIA Tesla T4, 15360 MiB each, no NVLink
- 31 GiB host RAM, 4 vCPU, CUDA 13, PyTorch 2.11
- Compute capability 7.5 (Turing): FP16/INT8 only, no native BF16 or FP8

## Repository layout

```
benchmarks/
  llm-and-training/    chat, agents, long context, fine-tuning
  image-models/        Z-Image, Qwen-Image, SDXL, FLUX.2
  video-generation/    CogVideoX, LTX 2B, abandoned LTX 13B
  minimax-h3-image/    quant/engine research and native-resolution test
  longcat-video-avatar/  pending: staged tooling for a benchmark not yet run
  inkling-2-mini/       Inkling-2-Mini engine-x-quant sweep, measured
  kromoss/              queued: staged image-model sweep, not yet run
  media/               generated images and videos from the original runs
website/               static site, data module, ManimGX diagrams, GEO assets
scripts/               extraction and verification tools
docs/                  cross-project index
GEO-AUDIT-REPORT.md    generative-engine-optimization audit
```

Each benchmark folder keeps its authoritative CSV/JSON tables, reports and archived server logs. Generated media lives in `benchmarks/media/benchmark-media.tar.gz.*`: two parts totaling 116 MiB, with 112 logical files deduplicated to 63 unique payloads and lossless WebP stills preserving original decoded pixels. Extract only when needed with `python3 benchmarks/media/extract.py`. See `DATA-INVENTORY.md` and `benchmarks/media/MANIFEST.json`.

## Run the site locally

```bash
cd website
python3 -m http.server 8000
# open http://127.0.0.1:8000/
```

No build step, framework, web fonts or chart library. Charts are HTML/CSS/JS; animations are pre-rendered diagrams wrapped in an `<mx-clip>` web component.

## Regenerate data

```bash
python3 scripts/extract_ruffbench.py
cd website
python3 scripts/build_data.py
python3 scripts/build_geo_assets.py
python3 scripts/check_data.py
```

`build_geo_assets.py` regenerates `benchmarks.html` and `llms-full.txt` from `data.js`, so the AI-crawlable tables never drift from the visual charts.

## GEO and agent access

The site is designed to be readable by people and AI agents:

- `llms.txt`: curated entry point with key facts and links
- `llms-full.txt`: every measurement as plain text
- `benchmarks.html`: all tables as static HTML
- `robots.txt`: explicit access for AI crawlers
- `sitemap.xml`: site map
- JSON-LD `Dataset` and `FAQPage` structured data on the homepage and data page

See `GEO-AUDIT-REPORT.md` for the baseline audit and the fixes applied.

## Limitations

- CLIP-style quality scores measure prompt alignment, not aesthetics or human preference.
- Image results are 1024×1024; video results are short clips at each model's usual preset.
- Results are specific to this machine, these quantizations and these prompts.
- The larger 13B video model was abandoned at 57/93 GB when the writable layer hit its quota.

## Cite

T4-Bench, "Kaggle 2x Tesla T4 benchmark results", 2026. https://t4b.sdad.pro/
