#!/usr/bin/env python3
"""Build website/data.js from the unified benchmark CSV/JSON artifacts."""
import csv, json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent  # ai-benchmarks
EXTRA = json.load(open(BASE / "benchmarks/llm-and-training/extracted.json", encoding="utf-8"))
OUT = ROOT / "data.js"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# --- image models -----------------------------------------------------------
img_rows = read_csv(BASE / "benchmarks/image-models/benchmark/results.csv")
opt_rows = read_csv(BASE / "benchmarks/image-models/benchmark/optimization-results.csv")
clip_img = json.load(open(BASE / "benchmarks/image-models/benchmark/server-archive/results/clip_by_prompt.json"))

image_names = {
    "flux2-klein-4b": "FLUX.2 klein 4B",
    "qwen-image-2.1-viggle-4step": "Qwen-Image 2.1 Viggle 4-step",
    "z-image-turbo": "Z-Image-Turbo",
    "sdxl": "SDXL 1.0",
}
image_models = []
for mid, label in image_names.items():
    runs = [r for r in img_rows if r["model_id"] == mid and r["exit_code"] == "0"]
    # primary three seeds only (exclude explicit repeat rows)
    primary = [r for r in runs if "repeat" not in r["run_id"]] if "run_id" in runs[0] else runs[:3]
    walls = [num(r["wall_s"]) for r in primary]
    best_opt = max((r for r in opt_rows if r["model"] == mid), key=lambda r: num(r["images_per_hour"]))
    scores = [v for k, vs in clip_img.items() if k.startswith(mid.split("-")[0]) or
              (mid == "qwen-image-2.1-viggle-4step" and k.startswith("qwen_")) or
              (mid == "z-image-turbo" and k.startswith("zimage_")) or
              (mid == "sdxl" and k.startswith("sdxl_")) or
              (mid == "flux2-klein-4b" and k.startswith("flux_"))
              for v in vs]
    image_models.append({
        "id": mid, "name": label,
        "steps": int(num(primary[0]["steps"])) if primary else 0,
        "coldMedian": round(statistics.median(walls), 1),
        "coldMin": round(min(walls), 1),
        "coldMax": round(max(walls), 1),
        "peakVramMiB": int(num(primary[0]["peak_gpu0_mib"])) if primary else 0,
        "bestThroughput": int(num(best_opt["images_per_hour"])),
        "bestMode": best_opt["mode"],
        "clip": round(statistics.mean(scores), 4) if scores else 0,
        "qualityScore": round(statistics.mean(scores) * 100) if scores else 0,
        "clipN": len(scores),
    })
image_models.sort(key=lambda m: m["bestThroughput"], reverse=True)
image_optimization = [
    {"model": r["model"], "mode": r["mode"], "imagesPerHour": int(num(r["images_per_hour"])),
     "wall": num(r["wall_s"]), "images": int(num(r["images"])), "peak": int(num(r["peak_gpu0_mib"]))}
    for r in opt_rows
]

# --- video ------------------------------------------------------------------
vid_rows = read_csv(BASE / "benchmarks/video-generation/benchmark/results.csv")
clip_vid = json.load(open(BASE / "benchmarks/video-generation/benchmark/server-archive/results/clip_scores.json"))
video_models = []
for r in vid_rows:
    if r["exit_code"] != "0":
        continue
    frames = int(num(r["frames"]))
    wall = num(r["wall_s"])
    key = r["model_id"]
    scores = [v for k, v in clip_vid.items() if k.startswith(key + "/")]
    clips = 3 if "/" in r["seed"] else 1
    metrics_path = (BASE / "benchmarks/video-generation/benchmark/server-archive/results"
                    / key / "metrics.json")
    per_clip = None
    if metrics_path.exists():
        extra = json.load(open(metrics_path))
        if extra.get("per_clip_seconds"):
            per_clip = [float(x) for x in extra["per_clip_seconds"]]
    steady = round(statistics.median(per_clip), 1) if per_clip else round(wall / clips, 1)
    video_models.append({
        "id": key, "model": r["model"], "steps": int(num(r["steps"])),
        "frames": frames, "size": r["size"], "wall": round(wall, 1),
        "clips": clips, "perClip": steady,
        "perClipAll": per_clip or [],
        "fpsGenerated": round(frames / steady, 4),
        "peakVramMiB": int(num(r["peak_vram_mib"])),
        "clip": round(statistics.mean(scores), 4) if scores else 0,
        "qualityScore": round(statistics.mean(scores) * 100) if scores else 0,
    })

# --- h3 ---------------------------------------------------------------------
h3_rows = read_csv(BASE / "benchmarks/minimax-h3-image/benchmark/results-summary.csv")
h3_ok = [r for r in h3_rows if r["exit_code"] == "0"]
h3_q = {}
for r in h3_ok:
    if "Q3_K_M" in r["diffusion"]:
        h3_q.setdefault("Q3_K_M", []).append(num(r["wall_s"]))
    elif "UD-Q4_K_XL" in r["diffusion"]:
        h3_q.setdefault("UD-Q4_K_XL", []).append(num(r["wall_s"]))
    elif "Q5_K_M" in r["diffusion"]:
        h3_q.setdefault("Q5_K_M", []).append(num(r["wall_s"]))
h3 = [
    {"quant": k, "median": round(statistics.median(v), 1), "runs": len(v)}
    for k, v in h3_q.items()
]
h3_4096 = [r for r in h3_ok if r["w"] == "4096"]

# --- inkling -----------------------------------------------------------------
ink_rows = read_csv(BASE / "benchmarks/inkling-2-mini/results/inkling_results.csv")
ink_names = {
    "Inkling-2-Mini-UD-IQ1_M": "UD-IQ1_M (1-bit)",
    "Inkling-2-Mini-Uncensored-AD-IQ2_M": "AD-IQ2_M (uncens.)",
    "Inkling-2-Mini-UD-Q2_K_XL": "UD-Q2_K_XL",
    "Inkling-2-Mini-UD-IQ3_XXS": "UD-IQ3_XXS",
    "Inkling-2-Mini-Uncensored-AD-IQ3_S": "AD-IQ3_S (uncens.)",
    "Inkling-2-Mini-UD-Q3_K_XL": "UD-Q3_K_XL",
}
inkling_single = []
for r in ink_rows:
    if r["engine"] != "llama.cpp" or r["gpus"] != "1":
        continue
    tg = float(r["tg_tok_s"].split(" ")[0])
    pp = float(r["pp_tok_s"].split(" ")[0])
    inkling_single.append({
        "id": r["quant"], "name": ink_names.get(r["quant"], r["quant"]),
        "sizeGiB": {"Inkling-2-Mini-UD-IQ1_M": 7.46,
                    "Inkling-2-Mini-Uncensored-AD-IQ2_M": 8.06,
                    "Inkling-2-Mini-UD-Q2_K_XL": 8.51,
                    "Inkling-2-Mini-UD-IQ3_XXS": 10.86,
                    "Inkling-2-Mini-Uncensored-AD-IQ3_S": 12.43,
                    "Inkling-2-Mini-UD-Q3_K_XL": 12.69}[r["quant"]],
        "pp": round(pp, 1), "tg": round(tg, 1),
        "peakVramMiB": int(num(r["gpu0_peak_mib"])),
    })
inkling_single.sort(key=lambda m: -m["tg"])
inkling_negatives = [
    [r["engine"], r["note"]] for r in ink_rows
    if r["engine"] in ("ollama", "vllm", "sglang", "transformers-native")
    and r["exit_code"] not in ("", "0")
]
inkling_vision = [
    {"config": "AD-IQ2_M + vision, one T4", "wallS": 37.3,
     "peakVramMiB": 14533, "result": "works"},
    {"config": "AD-IQ3_S + vision, one T4", "wallS": "",
     "peakVramMiB": 14565, "result": "out of memory during image encode"},
    {"config": "UD-Q4_K_XL hybrid + vision", "wallS": "",
     "peakVramMiB": 513, "result": "context creation out of memory"},
]

data = {
    "generated": "2026-11-22",
    "server": {"gpus": 2, "gpu": "Tesla T4 15360 MiB", "arch": "sm_75 Turing",
               "ramGiB": 31, "cuda": "13.0", "torch": "2.11.0+cu130"},
    "imageModels": image_models,
    "imageOptimization": image_optimization,
    "videoModels": video_models,
    "h3": {"quants": sorted(h3, key=lambda x: x["median"]),
           "weightsGiB": [{"name": "All BF16", "gib": 126.0}, {"name": "All FP8", "gib": 64.1},
                          {"name": "All 4-bit", "gib": 33.1}, {"name": "One T4 VRAM", "gib": 15.0}],
           "native4096": [{"quant": "Q3_K_M", "wall": 659.7, "peak": 14653},
                          {"quant": "UD-Q4_K_XL", "wall": 672.0, "peak": 14493}]},
    "winners": {"image": "FLUX.2 klein 4B", "imageThroughput": 374, "imageClip": 0.3924,
                "video": "LTX-Video 2B 0.9.8 distilled", "videoClipBest": 0.2645,
                "videoClipName": "CogVideoX-2b",
                "steadyClipSeconds": next((m["perClip"] for m in video_models
                    if m["id"] == "ltx_multi3_s4_f49"), 27.4),
                "cogSeconds": next((m["wall"] for m in video_models
                    if m["id"] == "cog_s50_f49"), 1053.0)},
    "llm": EXTRA["llmScoreboard"],
    "inkling": {
        "single": inkling_single,
        "hybridNote": ("4-bit quants (15.5-21.3 GiB) do not fit one T4 and "
                       "have no cross-GPU split; a GPU+CPU hybrid manages "
                       "only 1.9-2.4 tok/s."),
        "vision": inkling_vision,
        "negatives": inkling_negatives,
        "engine": "llama.cpp b12633 (CUDA 12.8 prebuilt) is the only engine "
                  "that runs Inkling-2-Mini on T4",
    },
    "agentConcurrency": EXTRA["agentConcurrency"],
    "toolEval": EXTRA["toolEval"],
    "fineTuning": EXTRA["fineTuning"],
    "spark": EXTRA["spark"],
    "ternary": EXTRA["ternary"],
    "sourceFiles": EXTRA["sourceFiles"],
    "limitations": [
        "These notes describe how we measured. They are not limits of the T4 GPUs themselves.",
        "Our 0 to 100 quality score is a similarity check against the prompt. It tells you whether the output followed the words, not whether people like it.",
        "Images were tested at 1024x1024. Video clips were kept short and used each model's normal preset.",
        "We stopped the 13B video run halfway through its download. The Kaggle session ran out of writable space at 57 of 93 GB, so this says nothing about the model itself.",
        "Most timings include a fresh model load. Rows marked warm or batched reuse a model that is already loaded.",
        "Inkling speeds are token generation with a 512-token prompt and 256 generated tokens. The looped model cannot fully disable its reasoning, so per-answer time is longer than tokens-per-second suggests.",
        "Inkling 4-bit quants were only measured in a GPU-plus-CPU hybrid at 1.9-2.4 tokens per second, because llama.cpp has no way to split this architecture across both T4s.",
    ],
}

OUT.write_text("window.BENCH_DATA = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
print("image models:", [(m["name"], m["bestThroughput"], m["clip"]) for m in image_models])
print("video rows:", len(video_models), "h3 quants:", len(h3))
