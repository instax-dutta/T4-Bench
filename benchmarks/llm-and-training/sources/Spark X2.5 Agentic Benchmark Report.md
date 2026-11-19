---
title: "Spark X2.5 Agentic Benchmark Report"
aliases:
  - "Spark-X2.5 Benchmark 4B vs 1.7B"
  - "XHToken Spark X2.5 Agentic Coding Eval"
date: 2026-09-22
tags:
  - ai/benchmark
  - hardware/accelerator
status: complete
---

# Spark X2.5 Agentic Benchmark Report

> [!info] Metadata
> **Models:** XHToken/Spark-X2.5-4B vs Spark-X2.5-1.7B
> **Goal:** Verify every model-card claim for both models and measure agentic, long-horizon coding quality
> **Test rig:** Kaggle VM over SSH (`127.0.0.1:9191`) — 2x Tesla T4 15GB, 4x Intel Xeon @ 2.0GHz, 31GB RAM
> **Software:** transformers **4.57.1** (exact version pinned by the model card), torch 2.10 + CUDA, BF16, card-recommended sampling (`temperature=1.0, top_p=0.95, top_k=-1`), thinking mode ON (default)
> **Related:** [[2x Tesla T4 Kaggle Benchmarks]] (GGUF long-context slice on same rig) · [[Kaggle Accelerator Specs]] · [[Best Local Coding AI by VRAM Tier Cloud Codes Sep 2026]]

---

## TL;DR

- Architecture, context-length, tool protocol, and software-compat claims check out against `config.json`, `chat_template.jinja`, and the llama.cpp tree.
- **4B is a genuinely usable small coding agent** (3/3 agentic tasks pass, clean native tool calls). **1.7B is a mixed bag** (2/3 tasks, fails the from-scratch feature task, weak instruction following).
- Both models suffer from **thinking-verbosity**: long `<think>` traces that crowd out answers, break sentence-count constraints, and duplicate code blocks (which breaks naive output parsers — use the LAST code block, not the first).
- 4B in full BF16 **does not fit a T4 15GB for long agentic sessions** (eager-attention transients OOM); it needs CPU offload or shorter windows. 1.7B fits comfortably (~4.5GB).
- The card's headline benchmark numbers (SWE-Bench Pro 44.4, AIME 90.7, etc.) were **not reproduced** — that requires H100-class hardware and the full eval harnesses. Our tests are smaller but run end-to-end on the actual models.

> [!warning] Environment Pin
> The VM image ships transformers 5.0.0, which is **incompatible** with the model's custom `modeling_spark.py` (crashes in `get_expanded_tied_weights_keys`). All results below use transformers 4.57.1 per the card.

---

## Model-Card Claims Vs Verification

| # | Card claim | Evidence | Verdict |
| :--- | :--- | :--- | :--- |
| 1 | Hybrid attention: 1 full + 3 sliding-window layers | `config.json` `layer_types` = repeating `SSSF` pattern. 4B: 36 layers (9 full / 27 SWA). 1.7B: 28 layers (7 full / 21 SWA). `sliding_window: 512` | VERIFIED |
| :--- | :--- | :--- | :--- |
| 2 | Native 1M-token context | `max_position_embeddings: 1048576`, full-attention RoPE theta 5,000,000 (long-context scaling), SWA RoPE theta 10,000 | VERIFIED structurally; functionally tested to 5.6k (NIAH PASS, 1.7B). 1M needs H100-class VRAM, not testable on T4 |
| 3 | 4B dims: hidden 2560, 16Q/4KV heads, head_dim 256, 131k vocab | Exact match in `config.json` | VERIFIED |
| 4 | 1.7B dims: hidden 2048, 8Q/2KV heads, 28 layers, 131k vocab | Exact match in `config.json` | VERIFIED |
| 5 | Pretrained on ~20T tokens + 100s of billions long-context stage | No public artifact to check | NOT VERIFIABLE (taken on trust) |
| 6 | Trained on Huawei Ascend, RL + MOPD post-training | No public artifact to check | NOT VERIFIABLE (taken on trust) |
| 7 | Tool/agent integration (Codex, Claude Code, OpenClaw, Hermes) | Native protocol confirmed: `<tool_call>name<arg_key>k</arg_key><arg_value>v</arg_value></tool_call>` out, `<tool_response>` in, OpenAI-style `tools=` schema, `<think>` reasoning blocks. M1 tool-format test: PASS on both models | VERIFIED (protocol); harness-integration quality not tested |
| 8 | vLLM / SGLang / llama.cpp / MLX / Ollama / LM Studio compat | llama.cpp master contains `src/models/spark2-5.cpp` (native support, consistent with "b10828+" claim). transformers path tested working (4.57.1). vLLM/SGLang/Ollama binaries not exercised | PARTIALLY VERIFIED |
| 9 | 200+ languages | 131,072-token vocab; lossless tokenize round-trip verified on EN/ZH/FR/AR/HI/JA + code; ZH smoke answers correct (Hefei) | PLAUSIBLE, count not enumerated |
| 10 | Superior TTFT/TOPT/efficiency vs same-size models | Measured: 1.7B 16 tok/s @ 3.4GB, 4B 12 tok/s @ 8.2GB on T4 (BF16, thinking on). No side-by-side rival run, so "superior" is unconfirmed | MEASURED (no baseline) |
| 11 | Headline scores (SWE-Pro 44.4, SWE-Verified 41.6, AIME 90.7, tau3 30.4, BrowseComp 40.9, ...) | Full harnesses out of scope for 2xT4; our directional coding/agent tests below | NOT REPRODUCED (see Agentic results for our numbers) |
| 12 | Thinking mode default, temp 1.0 / top_p 0.95 / top_k -1 | `generation_config.json` matches exactly; `<think>` on by default in template | VERIFIED |

---

## Inference Stats (Measured)

| Metric | 1.7B | 4B |
| :--- | :--- | :--- |
| Load time (safetensors → CUDA) | 20s | 8.5s |
| VRAM, BF16, idle | 3.4GB | 8.2GB |
| VRAM under agentic load | ~4.8GB, stable | ~10-12GB, OOMs in long sessions |
| Throughput (thinking on, T4) | ~16 tok/s | ~12 tok/s |
| Trivial-Q thinking length | 179 tokens (verbose) | 54 tokens (decisive) |

---

## Agentic Long-Horizon Coding Results

Harness: the model's **native** `<tool_call>` protocol (parsed from real generations), tools = read/list/write/edit/run_bash, max 20 steps/task, thinking on, card sampling params. Same tasks for both models, each on its own T4.

### Task Scores

| Task | 1.7B | 4B |
| :--- | :--- | :--- |
| **T1** implement `median()` to pass 5 pytest tests | PASS — 5 steps, 1 tool error, ran tests | PASS — 4 steps, 0 errors, ran tests |
| **T2** debug repo (binary-search off-by-one across 2 files), 7 tests | PASS — 3 steps, 5 errors, ran tests | PASS — 14 steps, 9 errors, **never ran the suite itself** (final state correct at step limit — verification gap) |
| **T3** implement LRU cache from spec from scratch, 5 tests | **FAIL** — 3 tool steps + 17 no-call turns, never wrote a working file | PASS — 5 steps, 1 error, ran tests |
| Agentic score | **2/3** | **3/3** |

### Micro-Benchmarks

| Micro | 1.7B | 4B |
| :--- | :--- | :--- |
| **M1** single tool call `get_weather(city="Paris")` | PASS (but first emitted a pseudo-call in a fenced block before the real one) | PASS, textbook-clean protocol |
| **M2** "exactly 3 sentences, word 'pivot' in sentence 2, never say 'algorithm'" | FAIL — 29 sentences, also misread the constraint in thinking | FAIL — 23 sentences |
| **M3** 5 mini codegen problems, pass@1 (last-block extraction, 1024-token budget) | **1/5** (is_prime; run variance: reverse_words passed on a repeat run) | **2/5** (fib, is_prime) |
| **NIAH-lite** 5.6k-token needle retrieval | PASS ("84721" retrieved) | not run (same arch family as 1.7B; VRAM better spent on agent tasks) |

### M3 Per-Problem Detail

1024-token budget, last-code-block scoring, temp 1.0.

| Problem | 1.7B | 4B | Note |
| :--- | :--- | :--- | :--- |
| fib | FAIL (truncated fence) | PASS | 1.7B produced correct fib on a separate raw check — truncation, not inability |
| is_prime | PASS | PASS |  |
| reverse_words | FAIL (wrong semantics) | FAIL (SyntaxError — fence fragment) | 1.7B passed this on one repeat run: run-to-run variance is high at temp 1.0 |
| fizzbuzz | FAIL (fence fragment) | FAIL (fence fragment) | Prompt itself is ambiguous (`fizzbuzz(n)` single-value vs sequence); model's thinking shows it dithering between interpretations |
| merge_sorted | FAIL (fence fragment) | FAIL (fence fragment) |  |
| **Total** | **1/5** | **2/5** |  |

> [!warning] Parser Caveat
> "SyntaxError" rows mean the scored block contained prose/fragments inside the fence, not that the model can't code (see T1–T3). Thinking models emit 2+ code blocks (draft in `<think>` + final answer) — naive first-block parsers under-score them badly (our first attempt scored 0/5 and 1/5 for the same outputs).

---

## What This Means For Agentic Long-Horizon Coding

### 4B — Usable Small Agent

It completes implement, debug, and build-from-spec loops, uses file tools correctly, runs tests, and emits clean tool calls. Caveats: (a) slow to converge when diagnosing (T2 took 14 steps and it never verified with the suite — pair it with a harness that auto-runs tests); (b) needs >15GB VRAM for real sessions — deploy with offload or 20B+ GPUs, or use the Q4 GGUF; (c) single-turn instruction following is sloppy (M2), so constrain it with tools and tests rather than prose instructions.

### 1.7B — Assistant, Not Agent

Fine for short implement/debug bursts (T1/T2 in 3–5 steps), but the from-scratch task collapsed into 17 non-action turns: it talks about acting instead of emitting tool calls. Also the weakest instruction-following (M2: 29 sentences vs 3 asked). Use it where latency/memory matter and horizons are short; do not give it open-ended multi-file work.

### Both — Thinking Tax Is Real

Default thinking traces are long (worse on 1.7B), they duplicate code (thinking draft + final answer both in `python` blocks — parsers must take the LAST block), and they crowd fixed length constraints. For agent harnesses: keep per-step budgets >= 1k tokens, parse last-block, and consider `enable_thinking: false` for trivial steps.

> [!tip] GGUF Alternative
> For memory-constrained boxes, use the Q4 GGUF quants measured in [[2x Tesla T4 Kaggle Benchmarks]] (4B ~2.5GB file / 3.7GB VRAM at 32K; 1.7B ~1.1GB file / 1.3GB VRAM) instead of BF16.

---

## Deployment Notes (From Pain Encountered)

1. **Pin transformers to 4.57.1.** Version 5.x crashes on the custom `modeling_spark.py`. The card states 4.57.1 — believe it.
2. **4B + T4 15GB + long context = OOM.** Eager-attention fp32 transients spike 2+GB. Mitigations that worked: per-step history cap (~2k tokens), `torch.cuda.empty_cache()` per step, and CPU offload (`device_map="auto"`, GPU cap 12GB) for longer sessions.
3. **bitsandbytes 8-bit does NOT work** with this architecture (`baddbmm_cuda not implemented for 'Char'` in the custom eager attention). Use GGUF quants for memory-constrained boxes, not bnb.
4. **Password/env:** VM SSH `root@127.0.0.1 -p 9191` (password `kaggle`); GPUs need `LD_LIBRARY_PATH=/usr/local/nvidia/lib64` in non-interactive shells (persisted via `/etc/ld.so.conf.d/nvidia.conf` + `nvidia-smi` symlinked into PATH).

---

## Limitations Of This Benchmark

- Small task set (3 agent tasks + 6 micros), 1 run each, temperature 1.0 sampling — expect run-to-run variance of +/-1 task.
- Card headline numbers (SWE-Bench Pro/Verified, AIME, tau-bench, BrowseComp...) NOT reproduced — wrong hardware class and harness scale for that.
- 1M context verified structurally only; functional test reached 5.6k (T4 ceiling with eager attention).
- No rival-model baseline (no Qwen3.5/Gemma4 runs); "how good" is absolute, not relative.
- M3 single-turn codegen is parser-sensitive for thinking models; agentic file-tool results (T1–T3) are the more reliable signal.

---

## Appendix — Artifact Locations On The VM

- Weights: `/root/models/4B`, `/root/models/1.7B` (safetensors BF16); `/root/models/*.gguf` (Q4_K_M)
- Harness: `/root/bench/agent_bench.py`, results `/root/bench/out17.json`, `/root/bench/out4b.json`
- Probes: `/root/bench/m3probe.py`, `/root/bench/niah.py`, `/root/bench/smoke*.py`
