## Purpose
Preserve user-created ZIP archives of the original projects. These are historical snapshots, not active data.

## Ownership
- `archive/minimax-h3-image-Archive.zip` - snapshot of the original H3 benchmark project
- `archive/image-models-Archive.zip` - snapshot of the original four-image-model project

## Local Contracts
- Archives are read-only evidence. Do not extract over live files or modify their contents.
- If a file is needed from an archive, copy it into the owning `benchmarks/` project first.

## Work Guidance
- Keep filenames tied to the project they came from.

## Verification
- `unzip -t <file>` confirms integrity before relying on a snapshot.

## Child DOX Index
No child AGENTS.md. This folder is a leaf.
