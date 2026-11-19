# PLAN: MiniMax-H3-Image benchmark plan on 2x Kaggle T4

Scope id: `bench-plan`
Contract revision: 2
Server facts (measured 2026-11-18 over zrok SSH): 2x Tesla T4 15360 MiB (sm_75,
Turing, FP16 yes / BF16 no), 4 vCPU Xeon @2.0GHz, 31 GiB RAM no swap,
CUDA 13.0 / driver 580.178.04, torch 2.11.0+cu130, Ubuntu 24.04.

## Contract inventory

Every independently omittable required outcome from the user request and its
amendments has a stable id, an owner, and an observing gate or manual review.

| Id | Required outcome | Owner | Observation | Disposition | Rev |
|---|---|---|---|---|---|
| C1 | Measured server capability is recorded | leaf-1.1.1 | G1 in leaf-1.1.1 (file markers) | required | 1 |
| C2 | Model architecture + weight-memory math documented | leaf-1.1.1 | G2, G3 in leaf-1.1.1 | required | 1 |
| C3 | Compute-capability / BF16 constraint on T4 analyzed | leaf-1.1.1 | G4 in leaf-1.1.1 | required | 1 |
| C4 | All available quant variants enumerated with sizes/format | leaf-1.1.2 | G1, G2 in leaf-1.1.2 | required | 1 |
| C5 | Quants ranked for viability on 2x T4 | leaf-1.1.2 | G3 in leaf-1.1.2 | required | 1 |
| C6 | Inference engines surveyed with sources | leaf-1.1.3 | G1, G2 in leaf-1.1.3 | required | 2 |
| C7 | Low-VRAM methods from GitHub + forums researched | leaf-1.1.3 | G3, G4 in leaf-1.1.3 | required | 2 |
| C8 | Research synthesis produced | node-1.1 | N1 in node-1.1 | required | 1 |
| C9 | Feasibility + benchmark matrix built from research | leaf-1.2.1 | G1, G2 in leaf-1.2.1 | required | 1 |
| C10 | DOX tree implemented in repo root | leaf-1.2.2 | G1, G2 in leaf-1.2.2 | required | 1 |
| C11 | Perfected benchmark plan document written | leaf-1.2.3 | G1, G2, G3 in leaf-1.2.3 | required | 1 |
| C12 | Results template + acceptance criteria included | leaf-1.2.3 | G4 in leaf-1.2.3 | required | 1 |
| C13 | Artifacts integrate and all gates re-verified | node-1.2, root | N1, root G1-G3 | required | 1 |

Revision 2 adds C6/C7 after the user asked for GitHub/forum research on
low-VRAM inference methods. No owner changed; leaf-1.1.3 absorbs the addition.

## Ownership (exact, disjoint)

- leaf-1.1.1: `research/model-hardware.md`
- leaf-1.1.2: `research/quants.md`
- leaf-1.1.3: `research/engines-lowvram.md`
- node-1.1: `research/SYNTHESIS.md`
- leaf-1.2.1: `docs/feasibility-matrix.md`
- leaf-1.2.2: `AGENTS.md`, `docs/AGENTS.md`, `research/AGENTS.md`, `benchmark/AGENTS.md`, `scripts/AGENTS.md`
- leaf-1.2.3: `docs/BENCHMARK-PLAN.md`, `benchmark/results-template.md`
- node-1.2: no new artifacts, integration gates only
- root: `.unlazy/bench-plan/**`

## Shared contracts

- All measurements and claims carry a source URL or a command output.
- Bit-width math uses decimal GB from the official model card converted to GiB
  by 1e9/2^30; `scripts/verify-math.mjs` recomputes it independently.
- Docs are UTF-8 Markdown; gates use `scripts/verify-doc.mjs`.
- Only quant/engine variants available or installable on CUDA sm_75 count as
  viable; NVFP4, MLX, and modern-Marlin-only kernels are marked non-viable.
- Toolchain: Node v26.8.1, `/bin/sh`-compatible shell, repo root CWD.

## Dependency order

Wave 1: leaf-1.1.1, leaf-1.1.2, leaf-1.1.3 (independent).
Then node-1.1 (needs all three).
Wave 2: leaf-1.2.1 (needs node-1.1), leaf-1.2.2 (independent of research).
Then leaf-1.2.3 (needs leaf-1.2.1 + leaf-1.2.2), then node-1.2, then root.

## Dispatch table

| Leaf | Needs | Tier | Planned wave | State |
|---|---|---|---|---|
| leaf-1.1.1 | - | judgment | 1 | READY |
| leaf-1.1.2 | - | judgment | 1 | READY |
| leaf-1.1.3 | - | judgment | 1 | READY |
| node-1.1 | 1.1.1,1.1.2,1.1.3 | judgment | 2 | WAITING |
| leaf-1.2.1 | node-1.1 | judgment | 3 | WAITING |
| leaf-1.2.2 | - | mechanical | 1 | READY |
| leaf-1.2.3 | 1.2.1,1.2.2 | judgment | 4 | WAITING |
| node-1.2 | 1.2.1,1.2.2,1.2.3 | judgment | 5 | WAITING |
