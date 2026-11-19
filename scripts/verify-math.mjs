#!/usr/bin/env node
// Recompute weight-memory figures from the model card's decimal-GB component
// sizes and bit widths, then assert the plan quotes them. Prevents copied
// numbers from being their own proof.
// Usage: node scripts/verify-math.mjs PLAN.md
import { readFileSync } from 'node:fs';

const file = process.argv[2];
if (!file) { console.error('usage: verify-math.mjs FILE'); process.exit(2); }
const text = readFileSync(file, 'utf8');

const G = 1000 ** 3;
const GiB = 1024 ** 3;
// Component sizes in decimal GB, from the official model card.
const ditBF16 = 66.28, textEncBF16 = 66.7, vaeBF16 = 2.34;
const scale = (gb, bits) => (gb * (bits / 16) * G) / GiB;

const vals = {
  ditBF16: scale(ditBF16, 16),
  ditFP8: scale(ditBF16, 8),
  dit4bit: scale(ditBF16, 4),
  teBF16: scale(textEncBF16, 16),
  teFP8: scale(textEncBF16, 8),
  te4bit: scale(textEncBF16, 4),
  vae: scale(vaeBF16, 16),
};
vals.totalBF16 = vals.ditBF16 + vals.teBF16 + vals.vae;
vals.totalFP8 = vals.ditFP8 + vals.teFP8 + vals.vae;
vals.total4bit = vals.dit4bit + vals.te4bit + vals.vae;
vals.totalMixed = vals.ditFP8 + vals.te4bit + vals.vae; // FP8 DiT + 4-bit text encoder

const expected = [
  ['DiT BF16', vals.ditBF16, 61.5, 62.0],
  ['DiT FP8', vals.ditFP8, 30.7, 31.0],
  ['DiT 4-bit', vals.dit4bit, 15.3, 15.6],
  ['TextEnc BF16', vals.teBF16, 61.9, 62.3],
  ['TextEnc 4-bit', vals.te4bit, 15.4, 15.7],
  ['Total BF16', vals.totalBF16, 125.5, 126.5],
  ['Total FP8', vals.totalFP8, 63.8, 64.3],
  ['Total 4-bit', vals.total4bit, 32.9, 33.4],
  ['Total mixed FP8/4bit', vals.totalMixed, 48.4, 48.8],
];

const failures = [];
for (const [label, value, lo, hi] of expected) {
  if (!(value >= lo && value <= hi)) failures.push(`${label}=${value.toFixed(2)} GiB outside [${lo},${hi}]`);
  const rounded = value.toFixed(1);
  if (!text.includes(rounded)) failures.push(`plan missing recomputed value ${rounded} GiB for ${label}`);
}
if (failures.length) {
  console.error(`MATH FAIL:\n  - ${failures.join('\n  - ')}`);
  process.exit(1);
}
console.log(`MATH OK: ${expected.length} memory figures recomputed from model-card component sizes and present in plan`);
