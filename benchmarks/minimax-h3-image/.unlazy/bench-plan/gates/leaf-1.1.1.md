# Gates: leaf-1.1.1 model and hardware research

OWNS: research/model-hardware.md

Scope: document measured server capability, model architecture, weight-memory math, and sm_75 constraints with sources.

- [x] G1: measured server capability with sources
  CHECK: node scripts/verify-doc.mjs research/model-hardware.md 2500 3 Tesla T4 nvidia-smi 580.178.04
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=c1797c746368240386ad09c790b8b8e0b9daa7fdccce20589e74afd0265aa0c7; exit=0; EXPECT=matched; output-sha256=fd0f80eb9df0b0a76cc7927e81d8b45de7b6ae572b2a5df3a33b653077352e45; output-bytes=62; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G2: model architecture facts recorded
  CHECK: node scripts/verify-doc.mjs research/model-hardware.md 2500 3 33.1B Qwen3-VL 6 NFEs
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=e46c731d70f5acf87f93a28f1f1a8ce14d0ba5ffc1040e47a2277fa4595719d7; exit=0; EXPECT=matched; output-sha256=fd0f80eb9df0b0a76cc7927e81d8b45de7b6ae572b2a5df3a33b653077352e45; output-bytes=62; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G3: weight-memory math recorded
  CHECK: node scripts/verify-doc.mjs research/model-hardware.md 2500 3 61.7 GiB 126.0 GiB
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=7b2566abd420a97cdcf0a9857f5dbaa4d8979f6826c5234a878fd1477141be81; exit=0; EXPECT=matched; output-sha256=fd0f80eb9df0b0a76cc7927e81d8b45de7b6ae572b2a5df3a33b653077352e45; output-bytes=62; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G4: compute capability constraint analyzed
  CHECK: node scripts/verify-doc.mjs research/model-hardware.md 2500 3 sm_75 BF16 compute capability
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=a3a816bca4f80e29d9309d40e5ad875e52d66d80c2982aa793ac93169aa6926d; exit=0; EXPECT=matched; output-sha256=fd0f80eb9df0b0a76cc7927e81d8b45de7b6ae572b2a5df3a33b653077352e45; output-bytes=62; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries
