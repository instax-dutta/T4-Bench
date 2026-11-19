---
title: "Soup vs Unsloth Fine-Tuning Benchmark Tesla T4 2026"
aliases:
  - "Soup vs Unsloth QLoRA Head-to-Head"
  - "Soup CLI Unsloth Benchmark"
  - "Soup CLI Backend Defects and Silent Failures"
date: 2026-10-02
tags:
  - ai/benchmark
  - ai/fine-tuning
  - hardware/accelerator
status: verified
---

# Soup vs Unsloth Fine-Tuning Benchmark Tesla T4 2026

> [!info] Metadata
> **Hardware:** 2x NVIDIA Tesla T4 (sm_75, Turing, 15.6 GB each), 31 GB RAM, 4 vCPU, driver 580.178.04
> **Model:** `NousResearch/Meta-Llama-3.1-8B-Instruct` (rev `d10aef79`), NF4 4-bit QLoRA, fp16
> **Data:** `yahma/alpaca-cleaned`, seed 3407, 400 rows chat-templated to 73,657 tokens
> **Stack:** torch 2.10.0+cu128, transformers 5.17.0, trl 0.29.1, peft 0.21.2, bitsandbytes 0.50.2, unsloth 2026.9.14, soup-cli 0.75.0
> **Related:** [[2x Tesla T4 Kaggle Benchmarks]]

---

## Verdict

| Question | Winner | Margin |
| :--- | :--- | :--- |
| GPU compute cost (VRAM) | **Unsloth, decisively** | 7.1 GB vs 14.9 GB - **2.09x** |
| Fine-tune quality | **Tie** | held-out loss 1.0373 vs 1.0405 (0.3% apart) |
| Ease of use | **Soup, decisively** | 1 config file, zero code; Unsloth needed a custom script and hit 4 API/library failures |

Headline finding: **Soup's speed and memory come almost entirely from Unsloth.** `soup` with `backend: unsloth` and native Unsloth used the same VRAM - 7,109 vs 7,111 MiB, a 2 MiB difference. Whatever "2-5x faster" means in Unsloth's marketing, it is Unsloth's number, not Soup's.

## Results

All four arms used the same model, same 400 rows, same LoRA (r=16, alpha=32, 7 target modules, 41,943,040 trainable params in every arm), same optimizer, LR, schedule, seed, and batch 1 x accum 8 x 50 steps.

| Arm | Result | Peak VRAM | Final loss |
| :--- | :--- | ---: | ---: |
| `unsloth_native` | completed | 7,111 MiB | 0.8290 |
| `soup` `backend: unsloth` | completed | 7,109 MiB | 0.8044 |
| `soup` `backend: transformers` (unsloth installed) | completed | 14,867 MiB | 0.8058 |
| `soup` `backend: transformers` (unsloth blocked) | **OOM** | 14,817 MiB (died) | - |

### Quality: a tie, verified independently

Held-out loss (200 rows, 26,897 supervised tokens) was computed by running both adapters through **one neutral loader** - no Soup, no Unsloth in the eval path, so neither trainer gets an advantage.

| Adapter | Held-out loss |
| :--- | ---: |
| unsloth | **1.03731** |
| soup transformers | 1.04050 |

Adapter health was identical too: both saved 448 tensors, all 448 non-zero, 41,943,040 params, Frobenius norms within 0.1% (588.81 vs 588.23). Training loss curves overlay almost exactly. **The two frameworks are interchangeable on quality.**

### Compute cost: Unsloth wins by 2.09x

The gap is entirely *where* memory goes. Unsloth fuses the LM head and cross-entropy so the `[1, 1024, 128256]` logits are never materialized; stock TRL materializes them in fp32 - about 1 GB per copy. Soup's transformers path has no equivalent optimization on by default.

Measured FLOPs confirm both arms did the same work (3.3353e15 vs 3.2628e15, within 2.2%), so the memory gap is not "one arm did less" - it is the same computation with a different memory plan.

### Throughput: not cleanly measurable

| Arm | Median step | Note |
| :--- | ---: | :--- |
| `unsloth_native` | **8.65 s** | precise, via TrainerCallback |
| `soup` arms | ~9-10 s (upper bound) | whole-process span / 50, includes ~36 s model load |

Soup's timing artifacts do not record per-step wall time, and `soup bench train` explicitly refuses to measure an unsloth-backend run. The upper bound overstates training time, so per-step speed is recorded as a measurement gap, not a claim. The VRAM result already settles the compute-cost question.

## Honest Limitations

1. **T4 is not the hardware either project targets.** sm_75 has no bf16 tensor cores; both ran fp16. Unsloth's published 2-5x is measured on Ampere+. These numbers do not transfer to A100/H100.
2. **One seed, 50 steps, 400 rows.** Enough to separate 2x memory from noise; not enough to separate a 0.3% quality difference. Treat quality as a tie.
3. **`soup_hf_plain` was not truly stock HF** (see Defect 1 below). Only the import-blocked arm was genuine stock HF, and it OOM'd.
4. **No held-out eval of the soup-unsloth adapter** - same training loss (0.8044) but not run through the neutral evaluator.
5. **Per-step timing is single-arm** (unsloth only).

## Recommendation

**Use Unsloth as the engine, Soup as the interface.**

- **Pick Unsloth** if VRAM is the binding constraint (2x is the difference between fitting 8B on a 15 GB card and not fitting it), or if you already have a training script. It is the engine; everything fast about Soup's numbers is Unsloth's.
- **Pick Soup** if you want a config file instead of a script, one-command reproducibility, config validation that catches typos, built-in eval/merge/export/GGUF, and a Web UI. Those ergonomics are real and genuinely better.
- **Best of both today:** `soup train --config soup.yaml` with `backend: unsloth` in the config. That measured at Unsloth's 7.1 GB - Soup's ergonomics on Unsloth's engine. Caveat: the install-time dependency conflict in the gotchas section below.

Do **not** choose on quality - there is no measurable difference.

## Soup CLI Defects Found

Two silent defects found in soup-cli 0.75.0 during the benchmark - both let the run complete and look valid while doing something other than what the config asked for.

### Defect 1: `backend: transformers` is silently Unsloth-backed

The most consequential finding. `src/soup_cli/commands/train.py:1517` calls `is_unsloth_available()` **even when the config says `backend: transformers`** - purely to print a "try unsloth" tip. That function does `import unsloth` (`utils/unsloth.py:9`), and Unsloth patches the entire HF/TRL stack at import time.

**Consequence: you cannot get a stock-HF Soup run on a machine where Unsloth is installed.**

Verified directly:

- With the import blocked, `is_unsloth_available()` returns `False`; without the block, `True`.
- The blocked run's OOM traceback goes through `transformers/trainer.py:2088` -> `accelerate/utils/operations.py:811` - a clean stock HF path.
- Earlier *unblocked* runs showed `unsloth/trainer.py` -> `UnslothSFTTrainer.py` frames **while the config said `backend: transformers`**.

This makes Soup's README comparison table misleading: the "transformers" column on an Unsloth-equipped machine is not the transformers backend.

### Defect 2: `train_on_responses_only: true` silently did nothing

Soup logged:

```text
[transformers] return_assistant_tokens_mask==True but chat template
does not contain `{% generation %}` keyword.
```

It is a **warning, not an error**. The run proceeds training on prompt tokens too. The flag was set on both arms and assistant-only masking applied to neither - the quality comparison stayed fair, but the flag did not do what it said.

### Smaller Gotchas

- **Dependency conflict on install.** `pip install "soup-cli[train,fast]"` resolved unsloth 2025.9.5 against transformers 5.17.0 and `import unsloth` failed with `NameError: name 'auto_docstring' is not defined`. Forcing unsloth 2026.9.14 *downgrades* transformers to <=5.5.0 and trl to <=0.24.0 - below Soup's own declared floors (`transformers>=5.16.1`, `trl>=0.29.0`). The benchmark ran on transformers 5.17.0 + trl 0.29.1, where Unsloth imports and works outside its declared range.
- **`TrainingArguments` lost `warmup_ratio`.** Gone in transformers 5.x from both `TrainingArguments` and trl's `SFTConfig`. Soup still exposes `warmup_ratio` and converts it to `warmup_steps` internally.
- **Soup has no `max_steps` and requires integer `epochs`.** Step count is only controllable via dataset size - the benchmark capped the dataset to 400 rows to hit exactly 50 steps.
- **Unsloth's `formatting_func` is internally inconsistent** in 2026.9.14: its validator requires a list (`UnslothSFTTrainer.py:1331`) but its `.map` concatenates the result as a `str`, so a correct list raises `TypeError: can only concatenate str (not "list") to str`.
- **No custom kernels in Soup.** Grep of `src/` found no Triton/CUDA kernels. Its documented speed features (Liger, cut-CE, FlashAttention) are all **off by default** and self-measured small in its own docstrings: Liger "5.1% throughput / 12.9% memory" on H100, FlashAttention "1.015x, no memory saving".
- **`soup bench train` refuses unsloth-backend runs** (`bench/train_run.py:37`), so Soup's own benchmarking cannot produce a like-for-like per-step comparison against Unsloth.

## Reproducing

```bash
# data (identical for all arms)
python prep_data.py        # 4000 train / 200 val, seed 3407
python prep_pc.py          # chat-template render + token ids
python prep_shared.py      # chatml.jsonl (soup) + text.jsonl (unsloth)
python cap_rows.py         # 400 rows => 50 steps at bs1 x accum8

# arms, one per GPU
PYTHONPATH=./no_unsloth soup train --config soup_cfg_hf_pure.yaml --yes
CUDA_VISIBLE_DEVICES=1 python run_unsloth.py --model <model> \
  --data data/text_50.jsonl --out out/unsloth_native.json --steps 50

# neutral eval of both adapters
python eval_adapter.py
```

> [!warning] Stock-HF arm requires blocking Unsloth
> `no_unsloth/sitecustomize.py` blocks `import unsloth` for the stock-HF arm. Without it, Soup silently routes through Unsloth even when the config says `backend: transformers` - see Defect 1 above.
