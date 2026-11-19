#!/usr/bin/env node
// Sweep gate oracle: prove each of the four candidate models has at least
// MIN_RUNS successful measurements in the results CSV, and that the report
// cites all four models with sources.
// Usage: node scripts/verify-sweep.mjs MIN_RUNS
import { readFileSync } from 'node:fs';

const minRuns = Number(process.argv[2] || 3);
const models = ['z-image-turbo', 'qwen-image-2.1-viggle-4step', 'sdxl', 'flux2-klein-4b'];
const csvPath = 'benchmark/results.csv';
const docPath = 'docs/BENCHMARK-RESULTS.md';
let csv, doc;
try { csv = readFileSync(csvPath, 'utf8'); } catch (e) { console.error(`FAIL: missing ${csvPath}`); process.exit(1); }
try { doc = readFileSync(docPath, 'utf8'); } catch (e) { console.error(`FAIL: missing ${docPath}`); process.exit(1); }

const failures = [];
const lines = csv.trim().split('\n').filter(Boolean);
const header = lines.shift() || '';
if (!/model_id/.test(header)) failures.push('CSV header missing model_id');
for (const m of models) {
  const ok = lines.filter(l => l.split(',').includes(m) && /(^|,)0(,|$)/.test(l)).length;
  if (ok < minRuns) failures.push(`${m}: ${ok} successful runs < ${minRuns}`);
  if (!doc.includes(m)) failures.push(`report missing model ${m}`);
}
const urls = new Set(doc.match(/https?:\/\/[^\s)>]+/g) || []).size;
if (urls < 4) failures.push(`report has ${urls} URLs < 4`);
if (failures.length) { console.error('SWEEP FAIL:\n  - ' + failures.join('\n  - ')); process.exit(1); }
console.log(`SWEEP OK: ${models.length} models, >=${minRuns} successful runs each, ${urls} sources`);
