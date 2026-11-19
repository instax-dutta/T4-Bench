## Purpose
Cross-project documentation: a single index of what was benchmarked, which model won each task, and where the authoritative data lives.

## Ownership
- `docs/UNIFIED-INDEX.md` - master index and cross-project verdicts
- `docs/AGENTS.md` - this contract

## Local Contracts
- Every verdict must point to a report inside `benchmarks/` and state the measurement protocol.
- No new numbers are invented here; this folder summarizes only.

## Work Guidance
- Prefer tables with metric, value, protocol and source row over prose rankings.
- Keep the index short; detailed methodology stays in the owning project.

## Verification
- `node ../scripts/verify-dox.mjs ..` checks the DOX structure.
- Cross-check every quoted figure against the source report before editing.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
