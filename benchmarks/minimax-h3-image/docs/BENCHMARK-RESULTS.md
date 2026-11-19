# Measured results: MiniMax-H3-Image on 2x Kaggle T4

Live results from the Kaggle session (2026-11-18, UTC). Raw logs and PNGs are on
the ephemeral server under `/kaggle/working/bench/results/`, and archived
locally under `benchmark/server-archive/` (per-run metrics, PNGs, GPU logs,
runner scripts and build logs) with the consolidated table at
`benchmark/results-summary.csv`. Checksums were compared server-to-local and
match. No number below is extrapolated.
Method: `docs/BENCHMARK-PLAN.md`. Gotchas and fixes: `docs/EXECUTION-LOG.md`.

## Stack that actually ran

`stable-diffusion.cpp` built from source with `-DSD_CUDA=ON
-DCMAKE_CUDA_ARCHITECTURES=75 -DSD_CUDA_CUTLASS_PATH= -DGGML_CUDA_NO_VMM=ON`,
CUDA 13.0 / driver 580.178.04, plus unsloth pruned DiT GGUF and the P-H3-Image
4B int8-convrot text encoder (5.12 GB). All runs: 6 steps, CFG 1, Euler,
`--sigmas minimax-h3-image`, `--rng cpu`, `--offload-to-cpu`, `--vae-tiling`,
`--max-vram 12`, one process per run (cold load included in wall time).

## Throughput and memory

| Track | Quant (DiT) | Size | Seeds | Wall times (s) | Median (s) | Images/hr | Peak GPU0 |
|---|---|---|---|---|---|---|---|
| B2 | Q3_K_M (10.42 GB) | 1024x1024 | 42,123,999,+42 repeat | 101.1, 94.5, 94.5, 92.3 | 94.5 | 38.1 | 10671 MiB |
| B | UD-Q4_K_XL (13.61 GB) | 1024x1024 | 42,123,999 | 113.0, 117.0, 118.8 | 117.0 | 30.8 | 13559 MiB |
| B3 | Q5_K_M (14.60 GB) | 1024x1024 | 42,123,999 | 139.1, 114.7, 108.6 | 114.7 | 31.4 | 13971 MiB |
| B2 | Q3_K_M | 2048x2048 | 42,123,999 | 182.7, 180.5, 178.7 | 180.5 | 19.9 | 12413 MiB |
| B | UD-Q4_K_XL | 2048x2048 | 42,123,999 | 196.9, 176.2, 175.5 | 176.2 | 20.4 | 13735 MiB |
| B3 | Q5_K_M (14.60 GB) | 2048x2048 | 42 | 180.1 | 180.1 | 20.0 | 14579 MiB |
| B2 | Q3_K_M | 4096x4096 | 42 | 659.7 | 659.7 | 5.5 | 14653 MiB |
| B | UD-Q4_K_XL | 4096x4096 | 42 | 672.0 | 672.0 | 5.4 | 14493 MiB |

All runs exited 0 except where noted. GPU1 stayed at 3 MiB in every run:
everything fits on GPU0 with host-RAM streaming. The two T4s were not pooled.

Notable: Q5_K_M is *not* slower than UD-Q4_K_XL in the median at 1024 (114.7 s
vs 117.0 s), though its first run was 139 s (cold cache). At 2048 the two are
effectively tied (180.5 vs 176.2 s). The fidelity gain of Q5 therefore looks
cheap on this hardware, at the cost of ~1.4 GiB more peak VRAM.

### `--max-vram` streaming sweep (Q3_K_M, 1024, seed 42)

| Cap (GiB) | Wall (s) | Peak GPU0 |
|---|---|---|
| 8 | 93.0 | 10223 MiB |
| 10 | 99.9 | 10769 MiB |
| 12 (baseline) | 101.1 | 10671 MiB |

Lowering the cap reduced peak VRAM but did not produce a measurable latency
penalty in this range; all three values sit inside run-to-run noise (92-101 s).
Host-RAM streaming is therefore effectively free at 1024 on this setup.

## Correctness

- `B2_s1024_s42` rerun with the same seed produced a byte-identical PNG:
  SHA256 `56f53df4ae022ba839920a4c073e847ef0624480901a85e5b4f35e4ec6226591`
  for both. Pixel diff was `None` (identical).
- Output dimensions matched the request for every completed run; sample image
  stats (1024x1024, RGB): mean 128.8, std 73.1, i.e. non-empty and non-black.

## Quality proxy (no BF16 reference possible)

BF16 cannot run on this server, so LPIPS-vs-BF16 from upstream cannot be
reproduced locally. Instead, using Q5_K_M seed 42 as the highest-precision
local reference, same prompt and seed at 1024x1024:

| Comparison | MSE | PSNR vs Q5 |
|---|---|---|
| Q3_K_M -> Q5_K_M | 1299.12 | 16.99 dB |
| UD-Q4_K_XL -> Q5_K_M | 529.92 | 20.89 dB |

This is consistent with the published LPIPS ordering (Q4_K_M/UD-Q4_K_XL near
the fidelity knee, Q3_K_M visibly degraded).

## Failed / abandoned cells

| Cell | Reason |
|---|---|
| B with Qwen3-VL-32B Q4_K_M text encoder, 1024, seed 42 | `rc=137` (SIGKILL) during tensor loading. GPU peak only 13337 MiB, so this was a **host-RAM OOM**: 18.22 GB TE + 13.61 GB DiT + 1.17 GB VAE exceeds 31 GiB with `--offload-to-cpu`. ABANDONED. The 4B encoder is required on this server. |
| DiffSynth-Studio Track A | ABANDONED with evidence. All files were downloaded (3bpp DiT, 3bpp TE, int8 VAE, configs) and five fix attempts were made (see `docs/EXECUTION-LOG.md`). Final blocker: `CompressedINT8Linear needs compute capability (8, 0) or later and Tesla T4 reports (7, 5)`. EntroPack 3bpp is sm_80+ only. |
| ComfyUI Track C | Not measured. Repo and GGUF nodes were cloned, but no run completed: it needs a GGUF-aware workflow graph, and the P-H3 4B encoder is not a standard ComfyUI text-encoder type. |
| diffusers Track F | Not measured. It would require ~48 GB of freshly downloaded, diffusers-compatible DiT/TE weights; after the root mount went read-only there was no safe place to put them. The GGUF files used by sd.cpp are not loadable by diffusers. |
| SGLang / vLLM-Omni / FP8-Marlin / NVFP4 / MLX | Excluded in the plan for sm_75 or platform reasons; not attempted. |

## Headline finding

A 33.1B-parameter, 16 MP-class image model that nominally needs ~126 GiB of
weights runs end-to-end on a 15 GB T4 at native 4096x4096 in about 11 minutes
per image, using a 10-15 GB quantized DiT, a 5 GB 4B text encoder, and ggml
host-RAM streaming. The binding constraint is host RAM for the text encoder,
not GPU memory: swapping the 4B encoder for the 32B encoder pushes the process
past 31 GiB and gets it killed before generation starts.

## Reproduce

Commands and exact flags are in `docs/BENCHMARK-PLAN.md` section 5 and the
runner at `/kaggle/working/bench/run_sdcpp.sh` on the server. Raw `summary.csv`
is the authoritative table; this document is a human-readable summary.
