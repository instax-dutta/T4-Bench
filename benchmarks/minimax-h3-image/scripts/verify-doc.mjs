#!/usr/bin/env node
// Artifact gate oracle: prove a research/plan document exists, is substantial,
// contains the required markers, and cites the required number of sources.
// Usage: node scripts/verify-doc.mjs FILE MIN_BYTES MIN_LINKS MARKER...
import { readFileSync } from 'node:fs';

const [file, minBytesRaw, minLinksRaw, ...markers] = process.argv.slice(2);
if (!file || minBytesRaw === undefined || minLinksRaw === undefined) {
  console.error('usage: verify-doc.mjs FILE MIN_BYTES MIN_LINKS MARKER...');
  process.exit(2);
}
const minBytes = Number(minBytesRaw);
const minLinks = Number(minLinksRaw);
if (!Number.isFinite(minBytes) || !Number.isFinite(minLinks)) {
  console.error('MIN_BYTES and MIN_LINKS must be numbers');
  process.exit(2);
}

let text;
try {
  text = readFileSync(file, 'utf8');
} catch (err) {
  console.error(`FAIL: cannot read ${file}: ${err.message}`);
  process.exit(1);
}

const failures = [];
const bytes = Buffer.byteLength(text, 'utf8');
if (bytes < minBytes) failures.push(`size ${bytes} < ${minBytes} bytes`);
for (const m of markers) {
  if (!text.includes(m)) failures.push(`missing marker: ${m}`);
}
const links = new Set(text.match(/https?:\/\/[^\s)>\]]+/g) || []).size;
if (links < minLinks) failures.push(`unique URLs ${links} < ${minLinks}`);

if (failures.length) {
  console.error(`DOC FAIL: ${file}\n  - ${failures.join('\n  - ')}`);
  process.exit(1);
}
console.log(`DOC OK: ${file.split('/').pop()} (${bytes} bytes, ${links} sources, ${markers.length} markers)`);
