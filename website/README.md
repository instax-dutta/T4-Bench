# Benchmark Atlas website

A static, dependency-free site that visualises the three unified benchmark
campaigns on the Kaggle 2x T4 machine.

## Open it
Open `index.html` directly, or serve the folder with any static server:
```
python3 -m http.server 8000
```
then visit `http://127.0.0.1:8000/`.

## Stack
- HTML + CSS + vanilla JavaScript. No framework, no web fonts, no chart library, no build step.
- One generated `data.js` (~6 KB) read from the unified benchmark CSV/JSON files.
- Eight short pre-rendered diagrams (MP4) with poster frames, wrapped in an `<mx-clip>` web component that lazy-loads, plays in view and pauses offscreen.
- Total deployable size: about 660 KB including posters, clips and storyboards.

## Data pipeline
```
python3 ../scripts/extract_ruffbench.py
python3 scripts/build_data.py
python3 scripts/check_data.py   # asserts headline numbers match the rows
```
reads:
- `../benchmarks/image-models/benchmark/results.csv`
- `../benchmarks/image-models/benchmark/optimization-results.csv`
- `../benchmarks/image-models/benchmark/server-archive/results/clip_by_prompt.json`
- `../benchmarks/video-generation/benchmark/results.csv`
- `../benchmarks/video-generation/benchmark/server-archive/results/clip_scores.json`
- `../benchmarks/minimax-h3-image/benchmark/results-summary.csv`

and writes `data.js`. Re-run it if the source data changes.

## Animations
Source scenes are in `manim/scenes.py` (eight diagrams covering every chart category). Render with the local virtual environment:
```
cd manim
../.venv/bin/manimgx render scenes.py ImageRace -r 960x540 -o ../assets/image-race.mp4
../.venv/bin/manimgx render scenes.py VideoRace -r 960x540 -o ../assets/video-race.mp4
../.venv/bin/manimgx render scenes.py MemoryWall -r 960x540 -o ../assets/memory-wall.mp4
```
Posters are extracted from the final frame with ffmpeg.

## Interaction and accessibility
- Metric tabs switch between throughput, CLIP alignment and peak VRAM; `?metric=clip` and `?state=vram` deep-link a metric.
- All three basic motions are implemented: one-time bar growth, a shared moving tab indicator, and clips that play only in view.
- `prefers-reduced-motion` disables transitions and autoplay; posters carry the same information.
- Tables mirror every chart so the data is readable without animation.

## Evidence
Screenshots and recordings are in `shots/`, `shots-chart/`, `shots-mobile/` and `shots-motion/`.
Design decisions are in `docs/DESIGN.md`.