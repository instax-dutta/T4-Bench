# Inkling-2-Mini on Kaggle 2x T4

Date: 2026-11-22 UTC. Engine sweep and full quant matrix for
`thinkingmachines/Inkling-2-Mini` (26.4B MoE, 3.4B active, looped
transformer: the middle 12 of 24 layers run three times, ~5.4B effective
active per token; multimodal with a ViT vision tower). Raw data:
`../results/inkling_results.csv`, logs in `../results/logs/`. Session
issue log with every failure and fix: `../tooling/ISSUES.md`.

## Server and method

Same machine as the other projects: 2x Tesla T4 (15360 MiB each, sm_75
Turing, no BF16/FP8/FP4 hardware), 31 GiB RAM, 4 vCPU, CUDA 13, driver
580.178.04.

Protocol: `llama-bench -p 512 -n 256 -r 3` (auto context, ~8K), engine
llama.cpp b12633 official nightly prebuilt, CUDA 12.8 flavor with the
bundled cudart (the CUDA 13.5 flavor hard-fails on this driver: its PTX
is too new and it lacks sm_75 SASS). Single-GPU runs use `-sm none`;
VRAM peaks sampled at 1 Hz via nvidia-smi. Quants: unsloth
`Mainline_Support` GGUFs and AtomicChat baked-GGUF files (merged
PR #32694 layout; the unsloth repo-root files are the obsolete PR #32695
layout and do not load). Licenses: base model Apache-2.0 (card-declared);
unsloth and AtomicChat GGUF repos Apache-2.0, AtomicChat carries the
LICENSE file.

## Measured throughput

| Quant | Size GiB | Card use | pp512 t/s | tg256 t/s | Peak VRAM |
|---|---|---|---|---|---|
| UD-IQ1_M (1.75 bpw) | 7.46 | 1 GPU | 312.50 | **26.47** | 8635 MiB |
| AD-IQ2_M, uncensored (2.06 bpw) | 8.06 | 1 GPU | 341.83 | **26.11** | 9233 MiB |
| UD-Q2_K_XL | 8.51 | 1 GPU | 314.62 | 25.10 | 9699 MiB |
| UD-IQ3_XXS | 10.86 | 1 GPU | 310.32 | 22.97 | 12091 MiB |
| AD-IQ3_S, uncensored | 12.43 | 1 GPU | 319.94 | 22.28 | 13471 MiB |
| UD-Q3_K_XL | 12.69 | 1 GPU | 312.34 | **24.30** | 13913 MiB |
| AD-Q4_K, uncensored | 15.46 | GPU0 + CPU | 131.41 | 2.38 | hybrid |
| UD-Q4_K_M | 15.46 | GPU0 + CPU | 120.31 | 2.12 | hybrid |
| UD-Q4_K_XL | 16.42 | GPU0 + CPU | 116.37 | 2.12 | hybrid |
| UD-Q8_K_XL | 21.30 | GPU0 + CPU | 90.90 | 1.87 | hybrid |

Every 4-bit-or-larger file exceeds one card and has no cross-card split:
`-sm tensor` is not implemented for `inkling2_loop` (measured error),
`-sm row` is unsupported for this MoE, `-ts` does not split in v1.0.0,
and full offload piles the model onto device 0 and OOMs. The `-ngl 12`
fallback puts half the layers on CPU and generation drops to 1.9-2.4 t/s
- recorded for completeness, not recommended.

## Vision (image + text to text)

| Config | Result |
|---|---|
| AD-IQ2_M + mmproj-F16, one T4 | works: **37.3 s** per image chat, GPU peak 14533 MiB, correct image description, loop reasoning visible in the output |
| AD-IQ3_S + mmproj, one T4 | OOM during the image-encode pass (13.9 GiB of weights leave no encode headroom) |
| UD-Q4_K_XL hybrid + mmproj | context creation OOM, server exits |

## Engines that do not run it on this box

- **Ollama**: the official `inkling-2-mini` tag is MLX-only (Apple
  Silicon); importing any GGUF fails with `unknown model architecture:
  'inkling2_loop'` in Ollama's bundled runner.
- **vLLM**: rejects the GGUF at config validation (pydantic error).
- **SGLang**: does not install on this VM (Python 3.13 / CUDA 13).
- **transformers-native**: fails in 11 s with unknown model type
  (`inkling2_loop` postdates this transformers build); the arithmetic
  memory wall (dequant ~53 GB bf16) never even gets reached.
- **NVFP4/MXFP8 native checkpoint**: arithmetic-infeasible on T4 - no
  FP4/FP8 units, dequantized bf16 exceeds the box's combined VRAM and
  RAM. The model card itself recommends 32 GB+ VRAM.

## Verdict

llama.cpp b12633 (CUDA 12.8 flavor) is the only engine that runs
Inkling-2-Mini on T4s. On one card the practical tier is everything up
to ~12.7 GiB: 22-26 t/s generation, with Q3_K_XL the quality-throughput
sweet spot (24.3 t/s) and the uncensored AD-IQ2_M the best all-rounder
(26.1 t/s plus working vision at 37.3 s per image chat). There is no way
to reach the 4-bit quality tiers on this machine. Compared with the
repository's chat winner LFM2.5-8B-A1B (119 t/s), the looped 26B pays its
48-layer-per-token compute: roughly a quarter of the speed, bought back
with frontier-adjacent coding and agentic scores (see the model card).

## Sources

- https://huggingface.co/thinkingmachines/Inkling-2-Mini
- https://huggingface.co/unsloth/Inkling-2-Mini-GGUF (Mainline_Support)
- https://huggingface.co/AtomicChat/Inkling-2-Mini-Uncensored-GGUF
- https://github.com/ggml-org/llama.cpp (b12633 nightly)
- https://github.com/ggml-org/llama.cpp/releases/tag/b12633
