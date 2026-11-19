# MiniMax-H3-Image benchmark results template

Copy this block per measured run. Leave fields blank until a real run fills them;
never estimate a number. All runs use the published 6 NFEs and guidance_scale 1.

```text
Run ID:            <config-id>_<size>_<seed>          e.g. A_s2048_s42
Date (UTC):
Server:            Kaggle 2x Tesla T4 15360 MiB, sm_75, 31 GiB RAM, CUDA 13.0
Driver / torch:    580.178.04 / 2.11.0+cu130

Config
  Config id:        <A|B|C|D|E>  (see docs/BENCHMARK-PLAN.md Benchmark Matrix)
  Quant artifact:   <repo @ file, e.g. unsloth/MiniMax-H3-Image-GGUF UD-Q4_K_XL>
  Engine:           <stable-diffusion.cpp | ComfyUI-GGUF | diffusers-offload | ...>
  Engine version / git sha:
  Text encoder:     <repo @ file or "streamed from RAM" | "on GPU1">
  Loaders/flags:    <exact command line>
  GPU placement:    <GPU0 DiT / GPU1 TE / RAM streamed>

Workload
  Task:             <t2i | edit>
  Prompt id:        <P1..P5 from the plan prompt set>
  Prompt SHA256:    <sha256 of the exact prompt text>
  Size (WxH):       <e.g. 2048x2048>
  min_generation_area: <1024 to disable, or default 4194304>
  Seed:             <integer>
  generator_device: cpu
  Steps / guidance: 6 / 1
  Warmup runs:      <1 discarded generation after load>

Measurements
  Load time (s):
  Run 1..N latency (s):   <comma separated, N >= 5>
  Median latency (s):
  Mean latency (s):
  p95 latency (s):
  Per-step latency (s):   <median end-to-end / 6>
  Throughput (images/hour): <3600 / median latency>
  Peak GPU0 VRAM (peak VRAM on device 0, GiB):   <nvidia-smi polling + torch.cuda.max_memory_allocated>
  Peak GPU1 VRAM (GiB):
  Peak host RAM (GiB):
  First-token/first-step latency (s): <if measureable>

Correctness
  Output file:      <path in benchmark/results/>
  Output SHA256:
  Dimensions match request:  <yes/no>
  Non-empty / non-black:     <yes/no>
  Deterministic rerun hash equal: <yes/no>   (same seed twice)
  Visual spot-check notes:   <short text>

Quality (when a reference is available)
  LPIPS vs bf16 reference:  <or "no bf16 reference on this server">
  CLIP score:               <optional>
  Failure notes:            <artifacts, NaN, OOM, degraded output>

Acceptance verdict
  PASS / FAIL / ABANDONED:
  Reason:
```

## Per-config summary table (fill after all seeds and sizes complete)

| Config | Quant | Engine | Size | Median latency (s) | Images/hr | Peak VRAM (GiB) | LPIPS | Verdict |
|---|---|---|---|---|---|---|---|---|
| A | unsloth UD-Q4_K_XL | sd.cpp | 2048x2048 |  |  |  |  |  |
| B | unsloth Q3_K_M | sd.cpp | 2048x2048 |  |  |  |  |  |
| C | unsloth Q4_K_M | ComfyUI-GGUF | 2048x2048 |  |  |  |  |  |
| D | unsloth FP8-INT8-ConvRot | ComfyUI | 2048x2048 |  |  |  |  |  |
| E | Abiray Q4_K_M | sd.cpp | 2048x2048 |  |  |  |  |  |

## Provenance rules
- Keep the raw `nvidia-smi` log next to the run file when it was collected.
- Record any process restarts, OOMs, or engine fallbacks in `Failure notes`.
- Never overwrite a prior run; append a new Run ID.
- The acceptance thresholds are defined in `docs/BENCHMARK-PLAN.md` under Acceptance Criteria.
