# Inkling-2-Mini T4 sweep - issue log and measured numbers

Working log for the 2026-11-22 session on the Kaggle 2x T4 VM. Every issue
below was hit during the run; each fix is what actually unblocked it. The
final report cites this file.

## Issues and fixes

1. **SSH tunnel resets under load.** nvcc at load 9 on 4 vCPUs made sshd
   refuse/drop connections (the handoff warned about this). Fix: one
   ControlMaster multiplexed connection (`vmssh`), every long job under
   `nohup` on the VM, short polls, back-off after a drop. The tunnel itself
   died twice (connection refused at the port) and recovered after ~90 s -
   the notebook-side supervisor restarts it; nothing to do but wait.

2. **Kaggle writable-layer quota (~96 GB).** Known from 2026-11-21. Mitigations
   all held: one quant file on disk at a time, `disk_guard` before every big
   write, CSV mirrored to `/kaggle/working` after every row. Peak disk during
   this sweep never exceeded ~35 GB.

3. **Source build too slow.** cmake defaulted to a multi-arch CUDA build on
   4 vCPUs (~1 h in, 48/200+ template kernels, hours remaining). Fix:
   abandoned the source build for the official b12633 nightly prebuilt.

4. **CUDA 13.5 prebuilt flavor broken on T4.** `CUDA error: the provided PTX
   was compiled with an unsupported toolchain` - the 13.5 build lacks sm_75
   SASS and its PTX is too new for the VM's CUDA 13.0 driver (580.178.04) to
   JIT. Fix: the CUDA 12.8 flavor plus its bundled `cudart` tarball works
   (verified: loads and generates).

5. **unsloth repo-root GGUFs are the obsolete layout.** `check_tensor_dims:
   tensor 'blk.24.attn_q.weight' not found` - the root files are the old
   PR #32695 layout; llama.cpp b12600+ implements the merged PR #32694
   layout. Fix: unsloth's `Mainline_Support/*.gguf_file` files. The
   AtomicChat AD-* files are merged-layout already (verified working).

6. **llama-bench v1.0.0 CLI changed.** Old-style flags (`-c 8192`) abort
   with a usage dump - and the first sweep pass burned 9 CSV rows in 8
   minutes with exit 1 before this was caught. v1.0.0 has no `-c` (context
   is auto-sized), `-ts` takes `/`-separated values, `-ngl` default -1.

7. **v1.0.0 layer handling vs. earlier assumptions.** First pass was
   re-interpreted: rows were single-GPU all along; the ~5 GiB seen on GPU1
   was Ollama's idle residue, not a model split. Ollama serve was killed and
   all single-GPU rows re-measured on a clean box (tg rose from 14-17 to
   22-26 t/s once the box was clean).

8. **Dual-GPU split: `-ts` does not split, `-ngl 12` offloads to GPU0 + CPU.**
   `-ts 1/1` and `-ts 1.0/1.0` pile the whole model onto device 0
   (allocation failure); `-sm row` errors "device CUDA0 does not support
   split buffers" for this MoE. `-ngl 12` loads and runs but puts 12 of 24
   weight layers on GPU0 (~8.1 GiB) and the rest on CPU (GPU1 holds ~1.4
   GiB of buffers) - so those rows measure a GPU+CPU hybrid at ~2.4 t/s,
   not a 2-GPU split. A true both-cards split via `-sm tensor` is untested;
   candidate for a post-sweep manual row.

9. **Vision pass crashed on `Argument list too long`.** The driver passed
   the base64 image inline as a curl argument. Fixed: JSON body written to
   a file, `curl --data @file`; also replaced the fixed 30 s wait with a
   log-readiness poll.

12. **Attempt rows never wrote.** `attempt()` was given the whole command
    as one string and exec'd it as a filename (FileNotFoundError, no CSV
    row). Fixed with `shlex.split` for one-string commands.

10. **Ollama is a measured negative on both routes.** Official
    `inkling-2-mini` tag: "requires MLX support" (Apple Silicon only).
    Local GGUF import: `unknown model architecture: 'inkling2_loop'` in
    Ollama's bundled llama.cpp. Both recorded as attempt rows.

11. **Minor:** Ollama install script needs `zstd` (not preinstalled, fixed
    with apt); Ollama's bundled runner leaves ~5 GiB on GPU1 while idle,
    which inflated the GPU1 column of early single-GPU rows (GPU0 peaks
    unaffected).

## Measured numbers (clean pass, 2026-11-22)

llama.cpp b12633 prebuilt (CUDA 12.8), `llama-bench -p 512 -n 256 -r 3`,
auto context, clean box (Ollama killed). pp = prompt-processing t/s,
tg = generation t/s, VRAM = per-GPU peak MiB.

| Quant | Size | Config | pp512 | tg256 | GPU0/GPU1 peak MiB |
|---|---|---|---|---|---|
| UD-IQ1_M (1.75 bpw) | 7.46 GiB | 1 GPU | 312.50 ± 0.73 | 26.47 ± 0.24 | 8635 / 105 |
| AD-IQ2_M uncensored (2.06 bpw) | 8.06 GiB | 1 GPU | 341.83 ± 1.81 | 26.11 ± 0.35 | 9233 / 105 |
| UD-Q2_K_XL | 8.51 GiB | 1 GPU | 314.62 ± 1.27 | 25.10 ± 0.24 | 9699 / 105 |
| UD-IQ3_XXS | 10.86 GiB | 1 GPU | 310.32 ± 2.06 | 22.97 ± 0.32 | 12091 / 105 |
| AD-IQ3_S uncensored | 12.43 GiB | 1 GPU | 319.94 ± 2.45 | 22.28 ± 0.18 | 13471 / 105 |
| UD-Q3_K_XL | 12.69 GiB | 1 GPU | 312.34 ± 1.99 | 24.30 ± 0.24 | 13913 / 105 |
| AD-Q4_K uncensored | 15.46 GiB | -ngl 12: GPU0+CPU hybrid | 131.41 ± 5.04 | 2.38 ± 0.01 | 8099 / 1409 |

Reading so far: single-T4 generation sits at 23-26 t/s for 1-3 bpw and
24.3 t/s for Q3_K_XL (K-quant matmuls beat IQ dequant on sm_75); the 12.7
GiB Q3_K_XL fits one 15 GiB T4 with ~1.4 GiB headroom at auto ctx. The
Q4-class files exceed one card, and the `-ngl 12` hybrid (half the layers
on CPU) drops generation to 1.9-2.4 t/s - the 4-bit tier is not practical
on this box. There is no true two-GPU split: `-sm row` is unsupported for
this MoE, `-sm tensor` returns `LLAMA_SPLIT_MODE_TENSOR not implemented
for architecture 'inkling2_loop'` (measured on AD-Q4_K), and full offload
piles everything onto device 0.

Contaminated first pass (box shared with an abandoned nvcc build and
Ollama's idle 5 GiB on GPU1; superseded by the clean rows above):
tg 16-17 t/s for the 1-3 bpw quants - a cautionary note on measuring with
a noisy box.

## Final numbers (sweep2 + wrap-up rows, 2026-11-22)

Engine verdicts:

- **llama.cpp b12633 prebuilt (CUDA 12.8 flavor): the only engine that
  runs Inkling-2-Mini on T4.** Single-card tg 22-26 t/s on quants up to
  12.7 GiB; working vision at 37.3 s per image chat.
- **Ollama: negative both ways** - official tag is MLX-only, local GGUF
  import hits unknown architecture in its bundled runner.
- **vLLM: fails on the GGUF** (pydantic config validation, 70 s).
- **SGLang: does not install** on this VM (Python 3.13 / CUDA 13).
- **transformers-native: unknown model type** - this transformers build
  predates inkling2_loop support, fails in 11 s before any memory issue.

Full matrix (pp512/tg256 t/s, per-GPU peak MiB; raw CSV:
`results/inkling_results.csv`):

| Quant | Size GiB | Config | pp512 | tg256 | GPU0/GPU1 |
|---|---|---|---|---|---|
| UD-IQ1_M | 7.46 | 1 GPU | 312.50 | 26.47 | 8635 / 105 |
| AD-IQ2_M (uncens.) | 8.06 | 1 GPU | 341.83 | 26.11 | 9233 / 105 |
| UD-Q2_K_XL | 8.51 | 1 GPU | 314.62 | 25.10 | 9699 / 105 |
| UD-IQ3_XXS | 10.86 | 1 GPU | 310.32 | 22.97 | 12091 / 105 |
| AD-IQ3_S (uncens.) | 12.43 | 1 GPU | 319.94 | 22.28 | 13471 / 105 |
| UD-Q3_K_XL | 12.69 | 1 GPU | 312.34 | 24.30 | 13913 / 105 |
| AD-Q4_K (uncens.) | 15.46 | hybrid (GPU0+CPU) | 131.41 | 2.38 | 8099 / 1409 |
| UD-Q4_K_M | 15.46 | hybrid | 120.31 | 2.12 | 7701 / 1409 |
| UD-Q4_K_XL | 16.42 | hybrid | 116.37 | 2.12 | 7701 / 1409 |
| UD-Q8_K_XL | 21.30 | hybrid | 90.90 | 1.87 | 8001 / 1815 |

Vision:

| Config | Result |
|---|---|
| AD-IQ2_M + mmproj-F16, 1 GPU | **works: 37.3 s per image chat, GPU0 14533 MiB, correct description with visible loop reasoning** |
| AD-IQ3_S + mmproj, 1 GPU | OOM during image encode (14.2 GiB loaded, no encode headroom) |
| UD-Q4_K_XL hybrid + mmproj | context creation OOM, server exits |

Practical verdict for Kaggle-T4 users: run the uncensored build at
**AD-IQ2_M (26.1 t/s, vision-capable) or AD-IQ3_S (22.3 t/s, no vision
headroom) on a single T4**; the 4-bit tiers are unusable here and no
cross-card split exists. Q3_K_XL is the quality-throughput sweet spot at
24.3 t/s if the censored base is acceptable.
