#!/usr/bin/env python3
"""Generate crawller-friendly assets from data.js: benchmarks.html and llms-full.txt."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / "data.js").read_text(encoding="utf-8")
D = json.loads(raw.split("window.BENCH_DATA = ", 1)[1].rsplit(";", 1)[0])
BASE = "https://t4b.sdad.pro"

def clean(v):
    t = str(v).replace("**", "")
    t = t.replace(" — ", ", ").replace("–", "-")
    if t.strip() == "—" or t.strip() == "-":
        return "n/a"
    return t

def table(headers, rows):
    h = "".join(f"<th>{clean(x)}</th>" for x in headers)
    body = "".join("<tr>" + "".join(f"<td>{clean(v)}</td>" for v in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"

def plain(title, headers, rows):
    out = [f"\n## {title}", "| " + " | ".join(clean(x) for x in headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(clean(x) for x in r) + " |")
    return "\n".join(out)

sections = []

sections.append(("Chat and coding models", ["Model", "Reply tok/s", "Prompt tok/s", "VRAM GB", "GPUs"],
    [[m["model"], m["decodeTokS"], (m.get("prefillTokS") if m.get("prefillTokS") is not None else "—"), m["vramGB"], m["gpus"]]
     for m in sorted(D["llm"], key=lambda x: -x["decodeTokS"])]))
sections.append(("Two-agent concurrency", ["Agents", "Per agent", "Aggregate"],
    [[a["agents"], a["perAgent"], a["aggregate"]] for a in D["agentConcurrency"]]))
sections.append(("Tool-use evaluation", ["Metric", "Score"], [[t["metric"], t["score"]] for t in D["toolEval"]]))
sections.append(("Spark agent tasks", ["Task", "1.7B", "4B"], [[t["task"], t["small"], t["large"]] for t in D["spark"]["tasks"]]))
sections.append(("Ternary 27B, one T4", ["Packing", "Prompt tok/s", "Reply tok/s"],
    [[t["packing"], t["pp512"], t["tg128"]] for t in D["ternary"]["singleT4"]]))
sections.append(("Ternary 27B, two T4s", ["Packing", "Prompt tok/s", "Reply tok/s"],
    [[t["packing"], t["pp512"], t["tg128"]] for t in D["ternary"]["dualT4"]]))
sections.append(("Fine-tuning", ["Method", "Result", "Peak GB", "Loss"],
    [[r["arm"].replace("`", ""), r["result"], round(r["peakMiB"] / 1024, 1),
      r["loss"] if r["loss"] is not None else "—"] for r in D["fineTuning"]["results"]]))
sections.append(("Image generation", ["Model", "Seconds/image", "Images/hour", "VRAM GB", "Quality score"],
    [[m["name"], m["coldMedian"], m["bestThroughput"], round(m["peakVramMiB"] / 1024), m["qualityScore"]]
     for m in D["imageModels"]]))
sections.append(("Video generation", ["Configuration", "Frames", "Seconds/clip", "Total seconds", "VRAM GB", "Quality score"],
    [[m["model"], m["frames"], m["perClip"], m["wall"], round(m["peakVramMiB"] / 1024), m["qualityScore"]]
     for m in D["videoModels"]]))
sections.append(("MiniMax-H3 memory", ["Precision", "GB", "Fits one T4"],
    [[w["name"], w["gib"], "yes" if w["gib"] <= 15 else "no"] for w in D["h3"]["weightsGiB"]]))
sections.append(("Inkling-2-Mini, single T4", ["Quant", "File GB", "Reply tok/s", "Prompt tok/s", "VRAM GB"],
    [[m["name"], m["sizeGiB"], m["tg"], m["pp"], round(m["peakVramMiB"] / 1024, 1)]
     for m in D["inkling"]["single"]]))
sections.append(("Inkling-2-Mini vision", ["Configuration", "Seconds per image chat", "VRAM GB", "Result"],
    [[v["config"], v["wallS"] if v["wallS"] != "" else "n/a",
      round(v["peakVramMiB"] / 1024, 1), v["result"]] for v in D["inkling"]["vision"]]))
sections.append(("Inkling-2-Mini engines that fail on T4", ["Engine", "Observed failure"],
    D["inkling"]["negatives"]))

# --- Inkling headline block (generated from data.js so it never drifts) ------
ink = D["inkling"]
fastest = max(ink["single"], key=lambda m: m["tg"])
best = next(m for m in ink["single"] if "AD-IQ2_M" in m["id"])
q3 = next(m for m in ink["single"] if "Q3_K_XL" in m["id"])
vision_ok = next(v for v in ink["vision"] if v["result"] == "works")
tgs = [m["tg"] for m in ink["single"]]
ink_headline = [
    "Inkling-2-Mini (thinkingmachines, 26.4B mixture-of-experts, 3.4B active,",
    "looped transformer, multimodal) runs on ONE Tesla T4 via llama.cpp b12633",
    f"(CUDA 12.8 prebuilt) with GGUF quants up to 12.7 GB:",
    f"- Best all-round (recommended): {best['name']} ({best['sizeGiB']} GB) at {best['tg']} tok/s",
    f"  generation, {best['pp']} tok/s prompt; vision works with the mmproj",
    f"  projector at {vision_ok['wallS']} s per image chat"
    f" ({round(vision_ok['peakVramMiB']/1024)} GB peak).",
    f"- Fastest measured: {fastest['name']} at {fastest['tg']} tok/s, but 1-bit",
    "  quality is far below the recommended tier.",
    f"- Quality ceiling on one card: UD-Q3_K_XL ({q3['sizeGiB']} GB) at {q3['tg']} tok/s.",
    f"- All six single-card quants measure {min(tgs)}-{max(tgs)} tok/s",
    "  (512-token prompt, 256 generated, 3 repetitions).",
    "- 4-bit quants (15.5-21.3 GB) do not fit one T4 and cannot be split across",
    "  both: llama.cpp tensor-split is not implemented for this architecture;",
    "  a GPU+CPU hybrid manages only 1.9-2.4 tok/s.",
    "- Ollama (MLX-only official tag; bundled runner lacks the architecture),",
    "  vLLM, SGLang and transformers all fail on this machine.",
    "Full report: https://github.com/instax-dutta/T4-Bench/blob/main/benchmarks/inkling-2-mini/docs/BENCHMARK-RESULTS.md",
]
ink_html = ("<h2 style='font-family:Georgia,serif;margin-top:38px'>Inkling-2-Mini on Kaggle 2x T4</h2>"
            + "<p style='color:#AAB3AB;line-height:1.7'>" + "<br>".join(ink_headline) + "</p>")
ink_plain = "\n".join(["## Headline: Inkling-2-Mini on Kaggle 2x T4", ""] + ink_headline)

html_parts = ["""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>All benchmark data: T4-Bench</title>
<meta name="description" content="Complete measured benchmark tables for image, video, LLM, agent and fine-tuning workloads on Kaggle 2x Tesla T4, including the Inkling-2-Mini multimodal sweep at 26 tokens/second.">
<link rel="canonical" href="https://t4b.sdad.pro/benchmarks.html">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%230E1110'/%3E%3C/svg%3E">
<link rel="stylesheet" href="styles.css">
<script type="application/ld+json">""" + json.dumps({
  "@context": "https://schema.org", "@type": "Dataset",
  "name": "T4-Bench: Kaggle 2x Tesla T4 benchmark results",
  "description": "Measured image, video, language, agent and fine-tuning benchmarks on two Kaggle Tesla T4 GPUs. Includes the Inkling-2-Mini engine sweep: 22-26 tokens/second single-card with GGUF quants up to 12.7 GB, vision at 37.3 s per image chat, no cross-GPU split for larger quants.",
  "url": BASE + "/benchmarks.html",
  "creator": {"@type": "Organization", "name": "T4-Bench", "url": BASE},
  "datePublished": "2026-11-22",
  "variableMeasured": ["images per hour", "seconds per clip", "tokens per second", "seconds per image chat", "peak graphics memory", "quality score"]
}, indent=2) + """</script></head><body>
<header class="topbar"><a class="brand" href="/">T4<span>-</span>BENCH</a><nav><a href="/">Home</a><a href="llms.txt">llms.txt</a><a href="llms-full.txt">Full text</a></nav></header>
<main style="max-width:1160px;margin:0 auto;padding:40px 20px">
<h1 style="font-family:Georgia,serif;font-size:42px">All benchmark data</h1>
<p style="color:#AAB3AB">Every number below is measured on the same Kaggle notebook: 2x Tesla T4 15 GB, 31 GB RAM, 4 vCPU, CUDA 13. Source notes: <a href="https://blog.sdad.pro/" style="color:#FF6B4A">blog.sdad.pro</a>.</p>
"""]
for title, headers, rows in sections:
    html_parts.append(f"<h2 style='font-family:Georgia,serif;margin-top:38px'>{title}</h2>" + table(headers, rows))
html_parts.append("</main></body></html>")
html_parts.insert(1, ink_html)
(ROOT / "benchmarks.html").write_text("\n".join(html_parts), encoding="utf-8")

plain_parts = [f"# T4-Bench: full benchmark data\n", f"Source: {BASE}/benchmarks.html",
               "Hardware: Kaggle 2x Tesla T4 15 GB, 31 GB RAM, 4 vCPU, CUDA 13.",
               "Source notes: https://blog.sdad.pro/",
               "The figures come from saved runs on the same machine.",
               ink_plain]
for title, headers, rows in sections:
    plain_parts.append(plain(title, headers, rows))
(ROOT / "llms-full.txt").write_text("\n".join(plain_parts) + "\n", encoding="utf-8")
print(f"wrote benchmarks.html ({(ROOT/'benchmarks.html').stat().st_size} bytes) and llms-full.txt ({(ROOT/'llms-full.txt').stat().st_size} bytes)")
