# Gates: leaf-1.1.3 engines and low-VRAM methods research

OWNS: research/engines-lowvram.md

Scope: survey inference engines and low-VRAM methods for MiniMax-H3-Image from GitHub docs, issues, and forums; rank for the T4 server.

- [x] G1: inference engines surveyed with sources
  CHECK: node scripts/verify-doc.mjs research/engines-lowvram.md 3500 5 ComfyUI DiffSynth-Studio SGLang vLLM-Omni diffusers
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=9df289a550428b6a2d19bd7573098245d89b8157558c03626d6c33f2d6da42bb; exit=0; EXPECT=matched; output-sha256=98325ca1973110e67b5270b19b13fb4cb107b615560b31861d690304b9a73a4e; output-bytes=64; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G2: low-VRAM techniques from GitHub and forums
  CHECK: node scripts/verify-doc.mjs research/engines-lowvram.md 3500 5 GitHub block swapping CPU offload quantized text encoder
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=09fd83902f1eab6abee372b31f6dfe88aab8f1aba25d74dd58820b4607989ea8; exit=0; EXPECT=matched; output-sha256=420be357059f0fad04e534df8c80ca7959f8cd5206f7b336badb339d7f8044bc; output-bytes=64; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G3: community evidence and install commands
  CHECK: node scripts/verify-doc.mjs research/engines-lowvram.md 3500 5 forum pip install git clone
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=bbd5808d5cdf16e1d9887e48dc1fb71af398a75c83b5176c9e4c14b4721d8ae9; exit=0; EXPECT=matched; output-sha256=98325ca1973110e67b5270b19b13fb4cb107b615560b31861d690304b9a73a4e; output-bytes=64; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries
