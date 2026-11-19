---
title: "2x Tesla T4 Kaggle Benchmarks"
aliases:
  - "Kaggle T4 x2 LLM Benchmarks"
  - "Dual Tesla T4 Inference Benchmarks"
date: 2026-09-16
tags:
  - ai/benchmark
  - hardware/accelerator
status: verified
---

# 2x Tesla T4 Kaggle Benchmarks

> [!info] Metadata
> **Hardware:** 2x NVIDIA Tesla T4 15GB (30GB pooled, no NVLink), Xeon 4 vCPU @ 2.00GHz, 31GB RAM, Ubuntu 22.04.5 LTS
> **Driver:** 580.159.04, CUDA 12.8 toolkit, SM 7.5, app clocks hypervisor-capped at 585MHz
> **Runner:** Ollama 0.34.1 (bundled CUDA, auto multi-GPU split), `num_ctx` 32768 throughout
> **Method:** Live-measured via `/api/generate` + `/api/chat` (`stream: false`), warm steady-state, Q4_K_M quants throughout
> **Related:** [[Kaggle Accelerator Specs]], [[Run Qwen3.8-27B on Any GPU 8GB-32GB]], [[Best Ways to Get 32GB VRAM for Qwen3.8-27B - Hardware Buyer's Guide]]

---

## Scoreboard

| Model | File | VRAM | Decode warm | Prefill warm | GPUs used |
| :--- | ---: | ---: | ---: | ---: | :--- |
| LiquidAI LFM2.5-8B-A1B | 4.9GB | 5.7GB | ~119 tok/s | ~800 tok/s | 1x T4 |
| XHToken Spark-X2.5-1.7B | 1.1GB | 1.3GB | ~100 tok/s | fast | 1x T4 |
| XHToken Spark-X2.5-4B | 2.5GB | 3.7GB | ~54 tok/s | ~1385 tok/s @124K | 1x T4 |
| Qwen3-Coder-30B-A3B | 18GB | 22GB | ~71 tok/s | ~165 tok/s | 2x T4 split |
| google Gemma 4 12B IT | 6.7GB | 8.1GB | ~21 tok/s | ~144 tok/s | 1x T4 |
| Qwen3.8-27B | 16GB | 17.7GB | ~13 tok/s | 52-87 tok/s | 2x T4 split |

Throughput scales roughly with bytes per forward pass, except MoE models (LFM ~1B active, Qwen-Coder 3B active) break the curve upward. All quality-checked: `17 * 23 = 391` answered correctly; codegen spot-checks (stack class, reverse-string) correct.

> [!warning] Cold-start trap (all models)
> First touch is 5-10x slower (Qwen: 1.9 tok/s + 243s prefill; LFM: 27s prefill on 16 tokens; Gemma: 13s prefill) due to CUDA init + graph capture. Cold loads run 30-190s. Always benchmark warm (second run onward: load ~0.005s).

## Qwen3.8-27B - 13 tok/s, needs both T4s

- **File:** `unsloth/Qwen3.8-27B-GGUF` `Qwen3.8-27B-UD-Q4_K_M.gguf` - 16GB actual, not the ~12GB the quantization tables estimate. Single-T4 hosting is impossible; split (6.8 + 7.9GB, 66/66 layers, 100% GPU) is mandatory.
- **Verdict:** Usable daily driver at 32K context, matching the predicted 12GB-tier band. Full 262K and the NVFP4/DSpark path do not apply (Blackwell-only, T4 is `sm_75`).
- **Skip MTP draft:** +2.6GB for no gain at this VRAM level.

## LFM2.5-8B-A1B - 119 tok/s, single T4

- **File:** `LiquidAI/LFM2.5-8B-A1B-GGUF` `LFM2.5-8B-A1B-Q4_K_M.gguf` (4.9GB, official repo, no third-party quant needed).
- **Verdict:** The speed pick by 9x. Co-residency with Qwen confirmed - both stay loaded (23.6 of 29GB), so the box can serve Qwen for heavy reasoning and LFM for fast drafts with zero extra config.
- Minor: wraps reasoning in `<think>` tags even with a `/no_think` prefix - harmless at 120 tok/s.

## Gemma 4 12B IT - 21 tok/s, single T4

- **File:** `unsloth/gemma-4-12b-it-GGUF` `gemma-4-12b-it-Q4_K_M.gguf` (6.7GB; official QAT and `ggml-org` GGUFs exist as alternatives).
- **Verdict:** Exact middle of the pack, as parameter math predicts.

> [!warning] Thinking-token trap (Gemma-specific)
> Plain `/api/generate` returned `eval_count: 100` with an **empty** response - every token went to the thinking block. Fix: `"think": false` in the request (returned `17 times 23 is **391**.` at 21 tok/s). Any harness must set that flag or parse the `thinking` field, or quality evals score zero on a working model.

## Qwen3-Coder-30B-A3B - 71 tok/s, the agentic pick

- **File:** `unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF` `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` (18GB). Same 2-GPU split recipe as Qwen3.8-27B (~11GB per GPU, 100% GPU).
- **Verdict:** 5x faster than the dense 27B at higher coding quality - 3B-active MoE is the whole story. This is the model to serve for agentic coding on this box. Independently converges with the vault: the [[CPU LLM Benchmark Campaign]] production pick was the same family (Coder checkpoint, abliterated).
- Single-stream codegen: 53-76 tok/s across runs (256-token stack-class generations).

## Multi-Agent Concurrency (Qwen-Coder)

Server restarted with `OLLAMA_NUM_PARALLEL=2`, two parallel codegen agents (256 tokens each):

| Agents | Per-agent | Aggregate wall |
| :--- | ---: | ---: |
| 1 | 71 tok/s | 11 tok/s (load-dominated wall) |
| 2 | 56 + 52 tok/s | **92 tok/s** over 2.3s wall |

True parallel execution (both agents finish in ~2s, not serialized). The box serves 2 concurrent coding agents at ~50+ tok/s each.

> [!warning] Parallel-slot VRAM trap
> `OLLAMA_NUM_PARALLEL=4` at 32K ctx needs 4x KV slots (~31GB shown, 10% spilled to CPU) and single-stream collapsed to 28 tok/s. Rule: KV slots x ctx must fit 29GB pooled - parallel=2 at 32K (25GB, 100% GPU) is the sweet spot. For 4 agents, halve `num_ctx` to 16K per agent.

## tool-eval-bench --short (Qwen-Coder, 15 scenarios, 51.6s)

Harness: `SeraphimSerapis/tool-eval-bench` via `uv tool install`, pointed at Ollama's OpenAI endpoint (`--model qwencoder-32k --backend llamacpp --base-url http://127.0.0.1:11434/v1 --seed 42`).

| Metric | Score |
| :--- | ---: |
| Passed / partial / failed | 9 / 4 / 2 |
| Points | 22/30 |
| Quality | 73/100 |
| Responsiveness | 74/100 (median turn 1.5s) |
| Deployability | 73/100 |
| Weakest category | Multi-Step Chains (33%) |
| Safety | 1 warning (TC-08: batched tools before reading results) |

Credible mid-tier tool-calling on a $0/hr box. Full 69-scenario run and `--trials 8` (Pass@8/Pass^8 ceilings like the MiaAI-Lab comparison) left for a longer session.

## Spark-X2.5 Long Context (4B: 54 tok/s, 1.7B: 100 tok/s)

- **Files:** `XHToken/Spark-X2.5-4B-GGUF` (2.5GB) and `XHToken/Spark-X2.5-1.7B-GGUF` (1.1GB), official repos. Hybrid arch: 36 layers, only 9 full-attention (GQA 4 KV heads), rest sliding-window-512. Advertised max: **1,048,576 tokens**.
- **Why 1M fits 30GB:** 9 full layers x 4KB/token = 36KB/token; sliding layers are window-bounded (~108MB total). KV verified in logs: 4.6GB @128K, 18GB @512K, 36GB @1M (f16).
- **Max-context results (4B):** 128K loads in 8s (12.5GB VRAM), 512K in 10s (25.5GB), 1M in 39s (36GB KV, spills past VRAM, 7 tok/s - loads but degraded).
- **Needle PASS at 124K:** 5,000-line log doc, `BLUE-FALCON-99` planted mid-doc. Prefill 89.5s cold (1385 tok/s), retrieved correctly; repeat run 0.2s via prefix-cache reuse.
- Both Spark sizes ignore "code only" (reasoning chatter precedes code) but the code itself is correct. The 1.7B's earlier 60/40 CPU split was just a full-VRAM artifact, not a fit problem.

## Best Configs

```bash
# Qwen-Coder (18GB, 2-GPU split) - same volume rule as Qwen3.8
FROM /kaggle/working/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf
PARAMETER num_ctx 32768
PARAMETER temperature 0
```

```bash
# Spark-4B long context variants (same blob, cheap creates)
FROM /root/Spark-X2.5-4B-Q4_K_M.gguf
PARAMETER num_ctx 131072    # or 262144 / 524288 / 1048576
PARAMETER temperature 0
```

```bash
# LFM (4.9GB, 1 GPU) / Gemma (6.7GB, 1 GPU) - /root has the free space
FROM /root/LFM2.5-8B-A1B-Q4_K_M.gguf                  # or gemma-4-12b-it-Q4_K_M.gguf
PARAMETER num_ctx 32768
PARAMETER temperature 0
```

```bash
ollama create <name> -f Modelfile
curl localhost:11434/api/chat -d \
  '{"model":"<name>","messages":[{"role":"user","content":"..."}],
    "think":false,"stream":false}'
```

32K context is free at these sizes. Q4_K_M is the quality sweet spot throughout; Q3 would decode faster at a quality cost. For parallel agents: `OLLAMA_NUM_PARALLEL=2` env + server restart (see trap above).

## Box Gotchas

1. `nvidia-smi` is at `/opt/bin`; driver libs at `/usr/local/nvidia/lib64` - export `LD_LIBRARY_PATH` or symlink `libcuda.so*` / `libnvidia-ml.so*` into the system lib dir, else GPU discovery silently fails and models load to CPU.
2. llama.cpp source builds fail on `CUDA::cuda_driver` until step 1 is done; pass `-DCMAKE_CUDA_ARCHITECTURES=75`. Ollama (needs `zstd` first) was faster than compiling.
3. Confirm `/usr/local/lib/ollama/llama-server` exists before starting `ollama serve`.
4. `/kaggle/working` has only ~20GB - one 16GB GGUF at a time. Use `/root` (overlay, ~1TB free) for smaller files.
5. Never `pkill -f` with a pattern in your own remote command string - it kills your own shell. Use `pkill -x`.
