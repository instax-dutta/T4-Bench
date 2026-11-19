## Purpose
Decision documents that turn research into a server-specific feasibility matrix and the final benchmark plan.

## Ownership
- `docs/feasibility-matrix.md` - quant x engine feasibility and memory math for 2x T4
- `docs/BENCHMARK-PLAN.md` - the perfected benchmark plan
- `docs/EXECUTION-LOG.md` - live gotchas and fixes encountered while running the plan
- `docs/BENCHMARK-RESULTS.md` - measured numbers, correctness checks and abandoned cells

## Local Contracts
- Every recommendation traces back to a research artifact in `research/` and states its source.
- Memory figures must match the independent recomputation in `scripts/verify-math.mjs`.
- The plan is written for the measured hardware: 2x Tesla T4 15 GB, 31 GiB RAM, 4 vCPU, CUDA 13, sm_75.
- Distinguish official support from community/experimental methods and mark the risk.

## Work Guidance
- Keep the plan executable: concrete commands, exact flags, fixed seeds, warmup policy, and metric definitions.
- No results are fabricated; the plan defines how results will be captured in `benchmark/`.

## Verification
- `node scripts/verify-math.mjs docs/BENCHMARK-PLAN.md`
- `node scripts/verify-doc.mjs docs/BENCHMARK-PLAN.md 7000 5 <section markers>`
- Gates live in `.unlazy/bench-plan/gates/leaf-1.2.*.md`.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
