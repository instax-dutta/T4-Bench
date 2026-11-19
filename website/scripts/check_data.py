#!/usr/bin/env python3
"""Assert site headline figures agree with the underlying rows."""
import json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / "data.js").read_text(encoding="utf-8")
data = json.loads(raw.split("window.BENCH_DATA = ", 1)[1].rsplit(";", 1)[0])

errs = []
w = data["winners"]
best_img = max(data["imageModels"], key=lambda m: m["bestThroughput"])
best_clip = max(data["imageModels"], key=lambda m: m["clip"])
steady = next(m for m in data["videoModels"] if m["id"] == "ltx_multi3_s4_f49")
cog = next(m for m in data["videoModels"] if m["id"] == "cog_s50_f49")
ratio = round(cog["wall"] / w["steadyClipSeconds"])

if w["imageThroughput"] != best_img["bestThroughput"]:
    errs.append("image winner throughput mismatch")
if abs(w["imageClip"] - best_clip["clip"]) > 0.0001:
    errs.append("image CLIP winner mismatch")
if abs(w["steadyClipSeconds"] - steady["perClip"]) > 0.15:
    errs.append("steady clip seconds mismatch")
if w["cogSeconds"] != cog["wall"]:
    errs.append("cog baseline mismatch")
if ratio != 38:
    errs.append(f"ratio should be 38x, computed {ratio}")
if not all(m["wall"] >= m["perClip"] * m["clips"] * 0.9 for m in data["videoModels"]):
    errs.append("per-clip time exceeds total wall time")

if errs:
    raise SystemExit("DATA FAIL: " + "; ".join(errs))
print(f"DATA OK: {best_img['name']} {best_img['bestThroughput']} img/h; "
      f"LTX {w['steadyClipSeconds']} s/clip; CogVideoX {cog['wall']} s; ratio {ratio}x")
