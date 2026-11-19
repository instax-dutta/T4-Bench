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
for (const child of children) {
  const t = readFileSync(child, 'utf8');
  for (const h of required) {
    if (!t.includes(h)) failures.push(`${relative(root, child)} missing ${h}`);
  }
}
if (children.length < 3) failures.push(`only ${children.length} child AGENTS.md found`);

if (failures.length) {
  console.error(`DOX FAIL:\n  - ${failures.join('\n  - ')}`);
  process.exit(1);
}
console.log(`DOX OK: root contract + ${children.length} child AGENTS.md with all sections`);
