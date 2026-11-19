#!/usr/bin/env node
// DOX tree oracle: root contract present, child index filled, and every child
// AGENTS.md carries the six standard sections.
// Usage: node scripts/verify-dox.mjs <repo-root>
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const root = process.argv[2] || '.';
const failures = [];
const rootPath = join(root, 'AGENTS.md');
if (!existsSync(rootPath)) {
  console.error('DOX FAIL: missing root AGENTS.md');
  process.exit(1);
}
const rootText = readFileSync(rootPath, 'utf8');
if (!rootText.includes('# DOX framework')) failures.push('root missing # DOX framework');
if (/not yet indexed/.test(rootText)) failures.push('root Child DOX Index still placeholder');

const required = ['## Purpose', '## Ownership', '## Local Contracts', '## Work Guidance', '## Verification', '## Child DOX Index'];
const children = [];
function walk(dir) {
  for (const entry of readdirSync(dir)) {
    if (['node_modules', '.git', '.unlazy', '__pycache__', '.venv'].includes(entry)) continue;
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) walk(p);
    else if (entry === 'AGENTS.md' && p !== rootPath) children.push(p);
  }
}
walk(root);
let rails = 0, contracts = 0;
for (const child of children) {
  const t = readFileSync(child, 'utf8');
  const rel = relative(root, child);
  // A nested project root is a DOX rail, not a leaf contract: it must carry the
  // framework header and a filled child index, not the six leaf sections.
  const isProjectRail = /^benchmarks\/[^/]+\/AGENTS\.md$/.test(rel);
  if (isProjectRail) {
    rails++;
    if (!t.includes('# DOX framework')) failures.push(`${rel} missing # DOX framework`);
    if (/not yet indexed/.test(t)) failures.push(`${rel} Child DOX Index still placeholder`);
    continue;
  }
  contracts++;
  for (const h of required) {
    if (!t.includes(h)) failures.push(`${rel} missing ${h}`);
  }
}
if (children.length < 3) failures.push(`only ${children.length} AGENTS.md found`);
if (rails !== 3) failures.push(`expected 3 nested project rails, found ${rails}`);

if (failures.length) {
  console.error(`DOX FAIL:\n  - ${failures.join('\n  - ')}`);
  process.exit(1);
}
console.log(`DOX OK: root contract + ${rails} project rails + ${contracts} child contracts with all sections`);
