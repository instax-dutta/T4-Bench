# Gates: node-1.1 research integration

OWNS: research/SYNTHESIS.md

Scope: synthesize the three research leaves into one ranked evidence base for the feasibility matrix.

- [x] N1: synthesis cites all three leaf artifacts and gives a ranked shortlist
  CHECK: node scripts/verify-doc.mjs research/SYNTHESIS.md 2000 2 model-hardware.md quants.md engines-lowvram.md shortlist
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=1e04d1b003ef5f3a7ac0431c45f388fe446b84df2dd78b646e4b97f6dfeacedc; exit=0; EXPECT=matched; output-sha256=b0bca7b160542fda2ec2c0f1aa2b800aba3e15cef36bd8b6bebec62d24dda8d0; output-bytes=56; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] N2: synthesis covers user amendment on low-VRAM methods
  CHECK: node scripts/verify-doc.mjs research/SYNTHESIS.md 2000 2 low-VRAM GitHub forums
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=72eee153a82a2ebc6d3ba04838f8a3fe22a01c407ca05f09a5ddd62aa89f3847; exit=0; EXPECT=matched; output-sha256=14ec49980901d99255383a2f3b5d1c9854d5e1c9ed173adc88a1647026eb0cdf; output-bytes=56; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries
