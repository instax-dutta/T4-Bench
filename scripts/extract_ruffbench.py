#!/usr/bin/env python3
"""Extract measured T4 benchmark tables from the copied research reports."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "benchmarks/llm-and-training/sources"
OUT = ROOT / "benchmarks/llm-and-training/extracted.json"


def cells(line):
    if not line.strip().startswith("|"):
        return None
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    if all(re.fullmatch(r":?-{2,}:?", p) for p in parts):
        return "sep"
    return parts


def tables(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    out, cur = [], []
    for line in lines:
        c = cells(line)
        if c is None:
            if len(cur) >= 2:
                out.append(cur)
            cur = []
            continue
        if c == "sep":
            continue
        cur.append(c)
    if len(cur) >= 2:
        out.append(cur)
    return out


def by_header(tabs, *needles):
    for t in tabs:
        h = " ".join(t[0]).lower()
        if all(n.lower() in h for n in needles):
            return t
    raise KeyError(needles)


def rows(t):
    return [dict(zip(t[0], r)) for r in t[1:]]


def num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", str(s).replace(",", ""))
    return float(m.group()) if m else None


def load(name):
    return tables(SRC / name)


llm = load("2x Tesla T4 Kaggle Benchmarks.md")
soup = load("Soup vs Unsloth Fine-Tuning Benchmark Tesla T4 2026.md")
spark = load("Spark X2.5 Agentic Benchmark Report.md")
bonsai = load("Ternary Bonsai 2 27B Benchmark Report.md")

scoreboard = []
for r in rows(by_header(llm, "model", "decode warm", "prefill warm")):
    scoreboard.append({
        "model": r["Model"],
        "sizeGB": num(r.get("File", "")),
        "vramGB": num(r.get("VRAM", "")),
        "decodeTokS": num(r.get("Decode warm", "")),
        "prefillTokS": num(r.get("Prefill warm", "")),
        "gpus": r.get("GPUs used", ""),
    })

concurrency = []
for r in rows(by_header(llm, "agents", "aggregate wall")):
    concurrency.append({"agents": num(r["Agents"]), "perAgent": r["Per-agent"],
                        "aggregate": r["Aggregate wall"]})

tool_eval = [{"metric": r["Metric"], "score": r["Score"]}
             for r in rows(by_header(llm, "metric", "score"))]

soup_results = []
for r in rows(by_header(soup, "arm", "peak vram", "final loss")):
    soup_results.append({"arm": r["Arm"], "result": r["Result"],
                         "peakMiB": num(r["Peak VRAM"]), "loss": num(r["Final loss"])})
soup_quality = [{"adapter": r["Adapter"], "loss": num(r["Held-out loss"])}
                for r in rows(by_header(soup, "adapter", "held-out loss"))]
soup_steps = [{"arm": r["Arm"], "step": r["Median step"], "note": r["Note"]}
              for r in rows(by_header(soup, "arm", "median step"))]

spark_infer = []
for t in tables(SRC / "Spark X2.5 Agentic Benchmark Report.md"):
    if t[0][:2] == ["Metric", "1.7B"]:
        for r in rows(t):
            spark_infer.append({"metric": r["Metric"], "small": r["1.7B"], "large": r["4B"]})
        break
spark_tasks = [{"task": r["Task"], "small": r["1.7B"], "large": r["4B"]}
               for r in rows(by_header(spark, "task", "1.7b", "4b"))]

bonsai_single = []
bonsai_dual = []
for t in tables(SRC / "Ternary Bonsai 2 27B Benchmark Report.md"):
    h = " ".join(t[0])
    if "pp512" in h and "tg128" in h:
        target = bonsai_dual if "vs single" in h else bonsai_single
        for r in rows(t):
            target.append({"packing": r.get("Packing", r.get("packing")),
                           "pp512": num(list(r.values())[1]),
                           "tg128": num(list(r.values())[2])})
bonsai_ctx = []
for t in tables(SRC / "Ternary Bonsai 2 27B Benchmark Report.md"):
    if t[0][:2] == ["Context", "VRAM total"]:
        for r in rows(t):
            bonsai_ctx.append({"context": r["Context"], "vram": r["VRAM total"], "notes": r["Notes"]})
        break

data = {
    "sourceFiles": [p.name for p in sorted(SRC.glob("*.md"))],
    "hardware": "2x NVIDIA Tesla T4 15 GB, 31 GB RAM, 4 vCPU, Kaggle",
    "llmScoreboard": scoreboard,
    "agentConcurrency": concurrency,
    "toolEval": tool_eval,
    "fineTuning": {"results": soup_results, "quality": soup_quality, "steps": soup_steps},
    "spark": {"inference": spark_infer, "tasks": spark_tasks},
    "ternary": {"singleT4": bonsai_single, "dualT4": bonsai_dual, "context": bonsai_ctx},
}
OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
print("scoreboard", len(scoreboard), "concurrency", len(concurrency), "toolEval", len(tool_eval))
print("soup", len(soup_results), len(soup_quality), len(soup_steps),
      "spark", len(spark_infer), len(spark_tasks), "bonsai", len(bonsai_single), len(bonsai_dual), len(bonsai_ctx))
