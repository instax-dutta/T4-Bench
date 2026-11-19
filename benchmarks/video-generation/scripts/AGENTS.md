## Purpose
Helper oracles for the video benchmark.

## Ownership
- `scripts/verify-doc.mjs` - artifact and source checks used by the unlazy ledger

## Local Contracts
- Node ESM, standard library only, no writes, success-only marker on exit 0.

## Work Guidance
- Keep checks portable; avoid assumptions about non-default tools.

## Verification
- `node scripts/verify-doc.mjs docs/BENCHMARK-RESULTS.md 3000 5 measured latency VRAM models`

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
