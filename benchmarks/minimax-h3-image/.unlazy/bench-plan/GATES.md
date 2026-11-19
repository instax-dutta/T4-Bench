# Gates: bench-plan root

OWNS: .unlazy/bench-plan/**

Scope: the user's full request is met: quant and engine research including low-VRAM methods, a server-specific feasibility matrix, a DOX tree, and a perfected benchmark plan ready to run on the measured Kaggle 2x T4 session.

- [x] G1: all required artifacts exist and are substantial
  CHECK: node scripts/verify-doc.mjs research/SYNTHESIS.md 2000 2 shortlist low-VRAM
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=677c633bef406335238c08bb7f2bcee896c3ac62a920561982864e389e7843d2; exit=0; EXPECT=matched; output-sha256=57aa5279167417ddfb362ec22d8ac5b7c2fb084bc304cf87a3e0fa1678c2ad64; output-bytes=56; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G2: root memory math recomputed and present in final plan
  CHECK: node scripts/verify-math.mjs docs/BENCHMARK-PLAN.md
  EXPECT: MATH OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=78d3a1855c7ad5579fd528bf6368af3a2bc3f3a1b675ed11300ec40a4cd78680; exit=0; EXPECT=matched; output-sha256=d40008b9d8da6e9f45825dc307180db83ca6748d35ff2285b3aa2ce543caa087; output-bytes=89; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G3: final plan cross-references feasibility matrix, dox tree, and results template
  CHECK: node scripts/verify-doc.mjs docs/BENCHMARK-PLAN.md 7000 5 feasibility-matrix.md AGENTS.md results-template.md acceptance
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=c60f6aa31c0f2d77dae2b9f130456759f35778d3ea14aa0cfe8a44daf6f9c489; exit=0; EXPECT=matched; output-sha256=60c9a4a0550970cae5b89383cdc0e360222418c8f8f36758a368677ab9ce0a9f; output-bytes=63; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G4: final human audit against the user request and amendment
  EVIDENCE: 2026-11-18 audit reconciled all 13 contract rows (C1-C13) against the
  request and its GitHub/forum amendment. Evidence seen: live SSH probes in
  research/model-hardware.md; 32-repo quant catalogue in research/quants.md;
  48-source engine/low-VRAM research in research/engines-lowvram.md; ranked
  reconciliation in research/SYNTHESIS.md; server matrix in docs/feasibility-matrix.md;
  DOX OK for root + 4 child contracts; docs/BENCHMARK-PLAN.md with matrix,
  methodology, runbook, risks, acceptance, and results-template.md. All leaf,
  branch and root runnable gates reverified green. Not executed: the benchmark
  itself; this deliverable is the plan, not measured results.
