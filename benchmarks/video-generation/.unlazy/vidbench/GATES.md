# Gates: video-gen benchmark on 2x T4

OWNS: benchmark/results.csv, docs/BENCHMARK-RESULTS.md

Scope: benchmark the video models from the user's plan on the measured Kaggle 2x T4 session, with sourced throughput/quality numbers and a winner.

- [x] G1: at least two video models have successful measured runs and the report cites them with sources
  CHECK: node scripts/verify-doc.mjs docs/BENCHMARK-RESULTS.md 3000 5 measured latency VRAM models
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=df807265f0045baffc84446db5e1c603ce919433b35970b5c67b1779395959fb; exit=0; EXPECT=matched; output-sha256=7e1628fdf9424f667c4bfc7783d3c41c3f48b4170579fc2f9210ac24ced298c1; output-bytes=64; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/video-gen-bench; path=b93c3fbfaca3/30 entries

- [x] G2: results CSV has successful runs for each benchmarked model
  CHECK: node scripts/verify-doc.mjs benchmark/results.csv 200 0 model_id frames wall_s peak_vram
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=6bc5c24f3bfef0763cc727dc38b97d6d035a10bea153c0dddf2165c285270756; exit=0; EXPECT=matched; output-sha256=67e2c64bf4f6ef92037c7cf8e9eddab11dcf36f569cc9e1e7639d062fe6a9b4d; output-bytes=54; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/video-gen-bench; path=b93c3fbfaca3/30 entries

- [x] G3: final audit against the user's video-gen plan
  EVIDENCE: 2026-11-19. Reviewed all four plan entries. CogVideoX-2b and
  LTX-Video 2B 0.9.8 distilled were benchmarked with real MP4 outputs, latency,
  peak VRAM and CLIP quality; throughput was optimized with warm-process
  generation and a 4-step/49-frame variant. LTX 13B NF4 was attempted and
  ABANDONED with log evidence (writable layer read-only at ~97 GB, 57/93 GB
  downloaded). WanGP was reviewed and excluded as an interactive launcher with
  no headless reproducible generation call. Audio out of scope. Separate local
  project; H3 and image-model benches untouched.
