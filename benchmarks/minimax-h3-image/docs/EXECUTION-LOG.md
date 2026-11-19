# Execution log: gotchas and fixes

Live record of the benchmark run on the Kaggle 2x T4 session. Every entry is
something actually hit, not a hypothetical. Companion to `docs/BENCHMARK-PLAN.md`.

## Environment / access

| # | Gotcha | Fix | Evidence |
|---|---|---|---|
| 1 | `ssh -tt ... <<EOF` with the password on stdin failed: `Permission denied (password)` twice, exit 255. Forced TTY does not feed the password prompt reliably. | Use `sshpass -p 'kaggle' ssh -tt ...` for the initial session. | First two connection attempts, then `MUX_OK`, `hostname=01c4738f38f8` |
| 2 | Every SSH call re-authenticates and is slow. | Opened one `ControlMaster=yes -M -S <socket> -o ControlPersist=12h` connection with `sshpass`, then all later calls reuse `-S <socket>`. Socket lives in the pre-approved temp folder, not `/tmp`. | `MUX_OK` returned instantly on second call without password |
| 3 | The plan assumed the large overlay for `/kaggle/working`, but that path is a separate 20 GB loop mount (`/dev/loop2`). A ~63 GB model set would not fit. | Probed `df -h / /root /tmp /kaggle/working`; moved all models/repos/results to `/root/bench` on the overlay with 967 GB free. | `df`: `/dev/loop2 20G` vs `overlay 8.0T 967G`; `ROOT WRITABLE` |

## Models

| # | Gotcha | Fix | Evidence |
|---|---|---|---|
| 4 | Public "quant" repos are pruned DiT-only releases; the 32B Qwen3-VL text encoder (62.1 GiB at BF16) is not included. | Downloaded three separate components: DiT GGUF from unsloth, a text encoder (`leejet/MiniMax-H3-GGUF` Q4_K_M, and the smaller P-H3 4B int8), and the Comfy-Org fp16 VAE. | `hf download` logs: all six `OK` entries, `DONE downloads`; `du -sh` 36G + 17G + 4.8G + 1.1G |
| 5 | HF unauthenticated downloads warn about rate limits. | Kept downloads resumable with `hf download --local-dir` into persistent cache; six sequential jobs with per-file log lines so a failure can be resumed. | `✓ Downloaded path: ...` lines in `logs/download.log` |

## sd.cpp build

| # | Gotcha | Fix | Evidence |
|---|---|---|---|
| 6 | No Linux CUDA prebuilt in the latest GitHub release (only Windows CUDA, Linux ROCm/Vulkan, macOS). | Build from source with CMake. | Release asset list from GitHub API, tag `master-1106-532d2c1` |
| 7 | Shallow clone lacked submodules: `ggml` had no `CMakeLists.txt`, `add_library` alias error; CUTLASS headers missing. | `git submodule update --init --recursive` from the repo root. | `Submodule 'ggml' ... registered`, then CUDA compiler detection succeeded |
| 8 | CMake: "No CMAKE_CUDA_COMPILER could be found" despite `nvcc` being on PATH. | Set `CUDACXX=/usr/local/cuda/bin/nvcc` and passed `-DCMAKE_CUDA_COMPILER=...` plus `-DCMAKE_CUDA_ARCHITECTURES=75`. | `CUDA compiler identification is NVIDIA 13.0.88` |
| 9 | `CUTLASS headers not found` (tested with 3.9.2), and the submodule is large. | `-DSD_CUDA_CUTLASS_PATH=` to disable CUTLASS (INT8/CuTe attention path not needed for the FP16 ggml path). | Build proceeded past `cmake/cutlass.cmake` |
| 10 | `CUDA::cuda_driver` target not found: CUDA 13.0 toolkit here has no `libcuda.so` stub, so `FindCUDAToolkit` cannot define the target. Error appeared twice: in `ggml/src/ggml-cuda/CMakeLists.txt:188` and `CMakeLists.txt:369`. | For ggml: `-DGGML_CUDA_NO_VMM=ON` (its documented switch to skip the driver link). For the root target: patched the single `target_link_libraries(${SD_LIB} PUBLIC CUDA::cuda_driver)` line to a comment, safe because VMM is off and no driver API is used. | `line 369: # driver stub link removed...`; build then reached `[ 20%] Building CUDA object ...` |
| 11 | Build is slow: many CUDA template instances compiled with `-j4` on 4 vCPU (roughly 1% per minute through the fattn/mmq templates). | Left running under `nohup` with output appended to `logs/build.log`; no restart needed. | Progress observed 20% -> 39% -> 46% -> 55% across successive probes |

## Measurement harness

| # | Gotcha | Fix | Evidence |
|---|---|---|---|
| 12 | Need exact sd.cpp CLI flags, not guessed ones. | Read upstream source: `-o/--output` in `examples/cli/main.cpp:71`, `--max-vram`, `--offload-to-cpu`, `--vae-tiling`, `--seed`, `--sigmas` in `examples/common/common.cpp`. | `grep` output on the server |
| 13 | Benchmark must capture peak VRAM and avoid polluting the result with setup time. | `run_sdcpp.sh` starts a 1 Hz `nvidia-smi` CSV sampler, wraps the CLI in `/usr/bin/time -v`, writes `metrics.txt` with exit code, wall seconds and per-GPU peak MiB. | `RUNNER_READY` |

## First measured run (2026-11-18 ~19:16 UTC)
- `B2_s1024_s42`: unsloth Q3_K_M + P-H3 4B int8 TE, 1024x1024, seed 42.
  `exit_code=0`, `wall_seconds=101.104`, peak VRAM GPU0 **10671 MiB**, GPU1 3 MiB.
  Log: model load 15.2 s, text encode 18.8 s, generate 93.2 s, VAE decode 6.0 s.
  This proves the P-H3 4B encoder is accepted with the MiniMax-H3-Image GGUF DiT.
- Result: `runner` first attempt failed with `rc=127` because `/usr/bin/time` is
  not installed. Fix: removed the `/usr/bin/time` wrapper; wall time comes from
  `date +%s.%N` in the runner.
- Result: bare `nvidia-smi` now fails with "couldn't find libnvidia-ml.so"
  because `/usr/local/nvidia/lib64` is not on the default loader path.
  Fix: export `LD_LIBRARY_PATH=/usr/local/nvidia/lib64` in the runner and in
  every monitoring command.

## Batch 1 results (2026-11-18 19:17-19:40 UTC)
All on 1024x1024 unless noted, 6 steps, seed as shown, `sd-cli` with
`--offload-to-cpu --vae-tiling --max-vram 12`, P-H3 4B int8 text encoder.

| Run | Wall s | Peak GPU0 MiB | Verdict |
|---|---|---|---|
| B2 Q3_K_M seed 42 / 123 / 999 / 42-repeat | 101.1 / 94.5 / 94.5 / 92.3 | 10671 | PASS; repeat SHA256 identical to first, determinism confirmed |
| B UD-Q4_K_XL seed 42 / 123 / 999 | 113.0 / 117.0 / 118.8 | 13559 | PASS; fits 15 GB with ~1.2 GB headroom |
| B3 Q5_K_M seed 42 | 139.1 | 13971 | PASS; tightest fit |
| B with Qwen3-VL-32B Q4_K_M TE | 174.8 | 13337 | **ABANDONED: rc=137 (SIGKILL) during tensor loading** |

The 32B encoder failure is a host-RAM OOM, not a VRAM OOM: the log ends
midway through repeated tensor loads, GPU peak was only 13.3 GiB, and the
combined offloaded weights (18.22 GB TE + 13.61 GB DiT + 1.17 GB VAE) exceed
the 31 GiB host. Conclusion: on this server the 4B P-H3 text encoder is not
optional, it is required. This is a measured correction to the plan's Track B
quality-reference variant.

At 2048x2048 (seed 42): Q3_K_M 182.7 s / 12413 MiB and UD-Q4_K_XL 196.9 s /
13735 MiB, both PASS.

## Storage wall (2026-11-18 ~19:48 UTC)
- Symptom: `touch /root/bench/...` -> `Read-only file system`. `mount -o remount,rw /`
  fails with `permission denied`. The overlay has 873 GB reported free but the
  container's writable upper layer hit its own quota after ~90 GB of models,
  build artifacts and a 17.9 GB partial ModelScope download.
- Tested writable targets: `/kaggle/working` (20 GB loop, writable),
  `/dev/shm` (14 GB, writable), `/tmp` and `/root` (read-only).
- Fix: keep reading model weights from `/root/bench/models` (still readable),
  but write all results, logs, runners and new downloads under
  `/kaggle/working/bench`. Copied prior results there (54 MB). Recreated the
  runner at `/kaggle/working/bench/run_sdcpp.sh`; `batch3.sh` continues the
  interrupted runs.
- Track A (DiffSynth) adjustment: its 3bpp DiT and int8 VAE were already on the
  read-only layer, but the 3bpp text encoder is ModelScope-only (11.02 GB) and
  a package-manager download would need ~2x temporary space. Used a direct
  ranged `curl -L -C -` to the writable 20 GB area instead. Estimated >1 h at
  the observed 2-3 MB/s; it is not worth risking the 20 GB mount by staging a
  second copy. If that mount fills, Track A is ABANDONED with this evidence.

## Track A abandoned with evidence (2026-11-18 ~20:55 UTC)
After downloading the 3bpp DiT, 3bpp TE, int8 VAE and configs (11.02 GB TE via
direct ranged curl), four attempts were made:
1. `vram_limit=13`, FP16 compute -> CUDA OOM at 14.19 GiB during load.
2. `vram_limit=10`, `expandable_segments:True` -> still OOM at 14.25 GiB.
3. Official low-VRAM pattern with JSON sidecar registration and disk offload ->
   CuPy failed to create `/root/.cupy` (read-only); fixed with `CUPY_CACHE_DIR`.
4. FP16 compute -> `RuntimeError: self and mat2 must have the same dtype, got
   BFloat16 and Half`; switched to BF16.
5. BF16 compute -> definitive blocker:
   `RuntimeError: CompressedINT8Linear needs compute capability (8, 0) or later
   and Tesla T4 reports (7, 5). This format has no path on older hardware.`

Verdict: ABANDONED, not a tuning failure. This independently confirms the
plan's kernel-wall analysis: EntroPack's 3bpp path is sm_80+ only. The 11 GB
text-encoder download was therefore not useful for this server.

## Previously open items, now resolved
- P-H3 4B encoder with the GGUF DiT: **verified** on the first run (loaded,
  encoded in 18.8 s, generated a valid image).
- Q4_K_XL with the 32B encoder: **resolved negatively**, SIGKILL during load
  (host-RAM OOM), see Batch 1 results.
- Actual latency numbers: **measured**, 21 successful runs; see
  `docs/BENCHMARK-RESULTS.md` and `benchmark/results-summary.csv`.

## Remaining Python-only gotcha (Track A debugging)
- After the root mount went read-only, `import torch` failed with
  `FileNotFoundError: No usable temporary directory found in ['/tmp', ...]`,
  because `dill` calls `tempfile.gettempdir()`. Fix: exported
  `TMPDIR=/kaggle/working/bench/tmp` and created that directory. This only
  affected the Python engines; the C++ `sd-cli` runs were unaffected.

## DOX note
This file is owned by `docs/AGENTS.md`. Its contract was updated when this file
was added, and the parent/root index still points at `docs/` as the owner of
decision documents and execution records.
