# Gates: leaf-1.1.2 quantization landscape research

OWNS: research/quants.md

Scope: enumerate all available MiniMax-H3-Image quant variants, their formats and sizes, and rank viability on 2x T4.

- [x] G1: quant format families enumerated
  CHECK: node scripts/verify-doc.mjs research/quants.md 3000 4 GGUF FP8 NVFP4 SDNQ
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=d121980a2e1e1f8d94ea6b26245f495f0714e0b24a31706e6b559b6a55c65754; exit=0; EXPECT=matched; output-sha256=f7b42e61ff0bbc8ca2ebd908fefed62f7e48a46c570e47fcff484dcbfc65b062; output-bytes=55; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G2: concrete quant repos enumerated with sources
  CHECK: node scripts/verify-doc.mjs research/quants.md 3000 4 unsloth/MiniMax-H3-Image-GGUF Abiray/MiniMax-H3-Image-GGUF LSDJesus/MiniMax-H3-Image-fp8-nvfp4
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=0fafeede17ef2e5292b20039db395cf024ed34a4ee68d7cefd09a26028bb11fe; exit=0; EXPECT=matched; output-sha256=eb04ec0b542b62feb4b9cea78a353fc6a394d445b8dc07a2b0f0f2b440ba22e3; output-bytes=55; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries

- [x] G3: viability ranking for 2x T4 stated
  CHECK: node scripts/verify-doc.mjs research/quants.md 3000 4 viability 2x T4 non-viable
  EXPECT: DOC OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=f89e320a99b12dfd0bf8d6c2024e625ec1d5c8b9c6bde6a13b3e5f7d6e0730ab; exit=0; EXPECT=matched; output-sha256=f7b42e61ff0bbc8ca2ebd908fefed62f7e48a46c570e47fcff484dcbfc65b062; output-bytes=55; shell=/bin/sh; cwd=/Users/saiduttaabhishekdash/minimax-h3-bench; path=b93c3fbfaca3/30 entries
