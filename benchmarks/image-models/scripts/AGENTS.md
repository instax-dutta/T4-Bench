## Purpose
Verification oracles for the four-image-model sweep.

## Ownership
- `scripts/verify-doc.mjs` - artifact checks
- `scripts/verify-sweep.mjs` - per-model run-count and source checks

## Local Contracts
- Node ESM, standard library only, no writes, success-only marker on exit 0.

## Work Guidance
- Keep oracles deterministic and portable; avoid non-default shells.

## Verification
- `node scripts/verify-sweep.mjs 3` from the project root.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
