# Gates: leaf-1.2.1 feasibility matrix

OWNS: docs/feasibility-matrix.md

Scope: turn research into a server-specific feasibility matrix of quant x engine combinations with memory math.

- [x] G1: feasibility matrix with memory math
  CHECK: node scripts/verify-doc.mjs docs/feasibility-matrix.md 2500 2 33.1 GiB 30.9 GiB VRAM
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=d9a6a4861ff7c8f2d6d13bf345809ab9b3a1022ef8029dd7e7c110e2b79c7107; exit=0; EXPECT=matched; output-sha256=5b93bab4aa9b0246daf06583e2c5076f0cd84cc0e1e8ef05cf7a970234c12867; output-bytes=65; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G2: selected viable stack stated
  CHECK: node scripts/verify-doc.mjs docs/feasibility-matrix.md 2500 2 FP8 DiT 4-bit text encoder GGUF
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=9e5ea0f64d952ff2f48fad0889eb955b61b31e0a2d22e6c69d0e4d09679c5397; exit=0; EXPECT=matched; output-sha256=ccdb86e5a930c195361e51415d63505e754b47224fc640956314f2b7d5ee6c35; output-bytes=65; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries
