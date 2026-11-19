# T4-Bench

Benchmarks of image and video generation models on a Kaggle 2× Tesla T4 notebook, plus a lightweight website that visualises the results.

**Website:** https://instax-dutta.github.io/T4-Bench/

## Contents

- `benchmarks/minimax-h3-image/` — MiniMax-H3-Image quant/engine research, plan, measured results and server logs.
- `benchmarks/llm-and-training/` — chat, agents, long context and fine-tuning campaigns extracted from the original research notes.
- `benchmarks/image-models/` — FLUX.2 klein 4B, Qwen-Image 2.1 Viggle 4-step, Z-Image-Turbo and SDXL, including throughput optimization.
- `benchmarks/video-generation/` — CogVideoX-2b, LTX-Video 2B distilled and the abandoned LTX 13B attempt.
- `website/` — static site: HTML, CSS, vanilla JS, generated `data.js` and small pre-rendered clips.
- `scripts/` — shared verification oracles.
- `docs/` — cross-project index.

Each benchmark directory keeps its own measured tables, reports and archived server logs. Generated media and archives were removed from this repository to keep it small; the source measurements remain.

## Reproduce the website

```bash
cd website
python3 -m http.server 8000
# open http://127.0.0.1:8000/
```

To regenerate the extracted LLM tables and `data.js`:

```bash
python3 scripts/extract_ruffbench.py
cd website
python3 scripts/build_data.py
python3 scripts/check_data.py
```

GitHub Pages deploys `website/` on every push to `main` via `.github/workflows/pages.yml`.

## Hardware

2× NVIDIA Tesla T4 (15 GB each, sm_75/Turing, no native BF16 or FP8), 31 GB host RAM, CUDA 13, PyTorch 2.11. GPU access was provided by Kaggle.
