# Gates: image-sweep root

OWNS: benchmark/results.csv, docs/BENCHMARK-RESULTS.md

Scope: four candidate models benchmarked one by one on the measured 2x T4 server, with a sourced comparative report.

- [x] G1: every model has at least 3 successful measured runs and the report cites all four
  CHECK: node scripts/verify-sweep.mjs 3
  EXPECT: SWEEP OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=94c916b425afaa7de3fff85ed6ece6af7656359e6e9128cbe9a56fd01604cbf3; exit=0; EXPECT=matched; output-sha256=bedb7d3fa1208df7d89ff34a9dd663f7fd2891306c9f53987e065a2dc00be294; output-bytes=57; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/image-model-bench; path=b93c3fbfaca3/30 entries

- [x] G2: report contains a claims-vs-measured table for the user's original list
  CHECK: node scripts/verify-doc.mjs docs/BENCHMARK-RESULTS.md 3000 4 Claims vs measured latency VRAM
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=1c7f7221acdefe1c2ff4359c7f4b7b60da00259ea705e71cf1617da7cb67b78d; exit=0; EXPECT=matched; output-sha256=a80542e29d5fb340adb004451c727064c0950f48ebdc10729beb6649246d47f7; output-bytes=65; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/image-model-bench; path=b93c3fbfaca3/30 entries

- [x] G4: throughput optimization and best-of-both winner are documented
  CHECK: node scripts/verify-doc.mjs docs/BENCHMARK-RESULTS.md 5000 8 Throughput optimization winner dual CLIP
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=ba00b04e84acf51ee6ea34b3b21b2be05ee8a20e243795b351b4b670aef46a1d; exit=0; EXPECT=matched; output-sha256=a80542e29d5fb340adb004451c727064c0950f48ebdc10729beb6649246d47f7; output-bytes=65; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/image-model-bench; path=b93c3fbfaca3/30 entries

- [x] G3: final audit against the user's four-model request
  EVIDENCE: 2026-11-18 audit. S1-S4: results.csv has 3 successful runs per model
  plus determinism repeats for three of them (15 successful rows total). S5:
  one engine (sd.cpp CUDA sm_75), one prompt, 1024x1024, seeds 42/123/999,
  one cold process per run, documented in docs/BENCHMARK-RESULTS.md. S6: sourced
  comparative report with 10 URLs. S7: claims-vs-measured table checks every
  numeric/licence claim from the user's shortlist. H3 data untouched: this
  project lives in image-model-bench locally and /kaggle/working/quadbench on
  the server; the H3 tree remains /kaggle/working/bench. Second pass audited
  2026-11-18: all four models got batch and dual-GPU optimization runs (15 rows
  in benchmark/optimization-results.csv), CLIP quality scoring used the exact
  prompt per image across three prompts, and docs/BENCHMARK-RESULTS.md declares
  FLUX.2 klein 4B the winner (374 img/hr, CLIP 0.3924). Raw data re-archived
  locally with checksums matching the server.
