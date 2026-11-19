## Purpose
Repository-owned verification oracles used by the unlazy gate ledgers to prove artifacts are complete.

## Ownership
- `scripts/verify-doc.mjs` - artifact existence, size, source count and marker checks
- `scripts/verify-math.mjs` - independent recomputation of weight-memory figures from model-card sizes
- `scripts/verify-dox.mjs` - DOX tree structural check
- Future verification scripts under `scripts/`

## Local Contracts
- Node ESM, standard library only, no network, no writes.
- Exit 0 only when every assertion passes; print a success-only marker (`DOC OK`, `MATH OK`, `DOX OK`) last.
- Exit 2 for usage errors, 1 for failed assertions; diagnostics go to stderr.
- Oracles measure the artifact directly and never echo a supplied number as proof.

## Work Guidance
- Keep oracles small, deterministic and portable; avoid non-default shells and external binaries.
- When a gate changes, lint and re-approve the ledger before trusting new evidence.

## Verification
- `node scripts/verify-math.mjs /dev/null` must exit 1 (negative control).
- `node scripts/gate-lint.mjs <ledger>` from the unlazy skill must report `LINT OK`.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
