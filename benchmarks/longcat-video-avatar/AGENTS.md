# DOX framework

- DOX is highly performant AGENTS.md hierarchy installed here
- Agent must follow DOX instructions across any edits

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it

## Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Purpose

Pending benchmark of `meituan-longcat/LongCat-Video-Avatar-1.6` on the Kaggle
2x Tesla T4 machine. Paused 2026-11-21 on VM storage: the writable overlay
quota (~96 GB) is smaller than a full both-repo download (~112 GB) and the
overlay flipped read-only mid-download. No generation has been run and no
measured result exists yet.

## Ownership

- `tooling/` - staged, uploadable-at-once scripts for the resume session
  - `prepare.sh` - selective downloads (phase0 INT8-only 15.9 GB, phase1 rest,
    phase2 fp16) plus the four T4 patches; idempotent and resumable
  - `int8_load_test.py` - phase0 verdict: loads the INT8 DiT, moves it to one
    T4, records OOM/peak VRAM to `int8_load_test.json`
  - `benchmark_avatar.py` - sweep driver (CSV schema per the original plan,
    1 Hz nvidia-smi sampling, ffprobe validation)
  - `vmssh` - multiplexed SSH helper (one ControlMaster connection) so the
    tunnel and notebook are not stressed
- Root `handoff.md` - the session record and resume playbook

## Local Contracts

- Status is PENDING. Never present this folder's arithmetic as a measured
  T4-Bench result; the expected-infeasible claim (INT8 DiT 14.78 GiB vs a
  15360 MiB card, weights replicated per rank by context parallelism) must be
  confirmed by `tooling/int8_load_test.py` before any verdict is recorded.
- Full both-repo downloads are banned on quota'd VMs; use the selective file
  lists in `tooling/prepare.sh` (whisper ships ~15 GB of fp32/bin/flax
  duplicates; base `dit/` 27 GB and `lora/` 5.4 GB are unused by the avatar
  pipeline). Explicit file lists, not `--include` (ignored by HF CLI 1.33).
- Any future results land here as a report plus raw data, never merged into
  another project's CSV.

## Work Guidance

- Resume playbook: root `handoff.md` sections "VM access", "Code audit
  findings", "What to do next". Run `prepare.sh phase0` first; only continue
  to phase1/phase2 and the sweep if the INT8 DiT fits one T4.
- The four T4 patches (bf16 to fp16, whisper fp16, text encoder on CPU,
  flash-attn2 to xformers) are applied by `prepare.sh`; document them in the
  final report.

## Verification

- `python3 -m py_compile tooling/int8_load_test.py tooling/benchmark_avatar.py`
- `node ../scripts/verify-dox.mjs ..` from this folder after structural changes.

## Style

- Keep docs concise, current, and operational
- Document stable contracts, not diary entries
- Delete stale notes instead of explaining history

## Child DOX Index

- No child AGENTS.md. `tooling/` is a plain folder; scripts there are
  self-describing and referenced from the sections above.
