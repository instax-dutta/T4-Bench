# Gates: leaf-1.2.3 benchmark plan and results template

OWNS: docs/BENCHMARK-PLAN.md, benchmark/results-template.md

Scope: write the perfected benchmark plan with matrix, methodology, runbook, risks, acceptance criteria, and a results template.

- [x] G1: plan sections complete
  CHECK: node scripts/verify-doc.mjs docs/BENCHMARK-PLAN.md 7000 5 Executive Summary Benchmark Matrix Methodology Runbook Risks
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=162b59b0882ad99cc98b420df7c20eda72ac438bedeb22768aff697bc482d374; exit=0; EXPECT=matched; output-sha256=e5803c4ae16210dcdfd8c8608e61779c31dcc0da58d88100e190f397ee6f7784; output-bytes=63; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G2: memory math independently recomputed from model card
  CHECK: node scripts/verify-math.mjs docs/BENCHMARK-PLAN.md
  EXPECT: MATH OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=78d3a1855c7ad5579fd528bf6368af3a2bc3f3a1b675ed11300ec40a4cd78680; exit=0; EXPECT=matched; output-sha256=d40008b9d8da6e9f45825dc307180db83ca6748d35ff2285b3aa2ce543caa087; output-bytes=89; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G3: benchmark controls specified
  CHECK: node scripts/verify-doc.mjs docs/BENCHMARK-PLAN.md 7000 5 2x T4 latency peak VRAM seed
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=1f3d3d14ae4f33e207f714d405e4eedd9fdf80d240e340e2481d9ce4dc8828da; exit=0; EXPECT=matched; output-sha256=49e7915c3d521c8a78a209e60f13033e12a3061bf09a0b23cf45ef3ce7a053c9; output-bytes=63; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G4: results template usable
  CHECK: node scripts/verify-doc.mjs benchmark/results-template.md 1200 0 Run ID median peak VRAM acceptance
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=9798468a6ef466404052a1339bef2945edbb9cac0f966c8e06ebc97e9cee0d41; exit=0; EXPECT=matched; output-sha256=d5638b23cafdaa3000b5af14b9848e51b8d50185bc83e45b21674406b7bf5e05; output-bytes=63; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries
