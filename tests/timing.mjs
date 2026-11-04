// 1337Boy CPU timing check against mGBA (Kehai Interim, 2026-11-04).
//   node tests/timing.mjs [page.html]
//
// tests/timing/probe1..6.gba are small homebrew ROMs (sources alongside: probeN.c + loops*.s,
// built with devkitARM + libtonc). Each times short instruction loops with cascaded timers
// TM2/TM3 and prints cycles x100 per loop iteration, once with WAITCNT 0000 (the power-on
// setting, no prefetch) and once with 4317 (the setting most commercial games use, prefetch on).
// tests/timing/mgba/probeN.png is what mGBA 0.10.2 prints. This script runs each probe in
// 1337Boy and compares the printed rows pixel for pixel.
//
// Expected result: every row identical, except the rows that read cartridge data with LDM
// (T LDMROM, T LDM4ROM, T LDM1ROM), where 1337Boy is 4 cycles slower on purpose. mGBA's
// GBALoadMultiple starts its wait count at S-N instead of N-S, which makes a one-register LDM
// from ROM cheaper than a plain LDR from the same address; 1337Boy follows GBATEK
// (nS + 1N + 1I) there. See TESTING.md.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const here = path.dirname(new URL(import.meta.url).pathname);
const page = path.resolve(process.argv[2] || path.join(here, '..', '1337boy.html'));
const LDM_FROM_ROM = new Set(['T LDMROM', 'T LDM4ROM', 'T LDM1ROM']);

function readPng(file) {           // minimal PNG decoder: 8-bit RGB/RGBA, non-interlaced
  const b = fs.readFileSync(file); let i = 8, w = 0, h = 0, ct = 0; const idat = [];
  while (i < b.length) {
    const len = b.readUInt32BE(i), type = b.toString('ascii', i + 4, i + 8), d = b.subarray(i + 8, i + 8 + len);
    if (type === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; }
    if (type === 'IDAT') idat.push(d);
    i += 12 + len;
  }
  const bpp = ct === 6 ? 4 : 3, raw = zlib.inflateSync(Buffer.concat(idat)), out = new Uint8Array(w * h * 3), stride = w * bpp;
  let prev = new Uint8Array(stride);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)], line = raw.subarray(y * (stride + 1) + 1, (y + 1) * (stride + 1)), cur = new Uint8Array(stride);
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? cur[x - bpp] : 0, up = prev[x], c = x >= bpp ? prev[x - bpp] : 0;
      let v = line[x];
      if (f === 1) v += a; else if (f === 2) v += up; else if (f === 3) v += (a + up) >> 1;
      else if (f === 4) { const p = a + up - c, pa = Math.abs(p - a), pb = Math.abs(p - up), pc = Math.abs(p - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? up : c; }
      cur[x] = v & 255;
    }
    for (let x = 0; x < w; x++) for (let k = 0; k < 3; k++) out[(y * w + x) * 3 + k] = cur[x * bpp + k];
    prev = cur;
  }
  return out;
}

// Row labels, in print order, from probeN.c (a heading row precedes each WAITCNT block).
function labels(n) {
  const src = fs.readFileSync(path.join(here, 'timing', `probe${n}.c`), 'utf8');
  const names = [...src.matchAll(/\{"([^"]+)"\s*,/g)].map(m => m[1].trim());
  const both = /for \(int w = 0; w < 2/.test(src);
  const rows = [];
  for (const w of both ? ['0000', '4317'] : ['4317']) { rows.push(`WAITCNT ${w}`); for (const nm of names) rows.push(`${nm} @${w}`); }
  return rows;
}

const br = await chromium.launch();
let bad = 0;
for (let n = 1; n <= 6; n++) {
  const p = await br.newPage();
  await p.addInitScript(() => { window.requestAnimationFrame = () => 0; });
  await p.goto('file://' + page); await p.waitForTimeout(1200);
  const rom = [...fs.readFileSync(path.join(here, 'timing', `probe${n}.gba`))];
  const fb = await p.evaluate(r => { window.B1337.loadRom(new Uint8Array(r)); return Array.from(window.B1337.runFrames(180)); }, rom);
  await p.close();
  const ref = readPng(path.join(here, 'timing', 'mgba', `probe${n}.png`));
  // The font's glyphs for text line r occupy y = 8r+2 .. 8r+9, one pixel into the next 8px cell.
  const rows = labels(n), hit = new Set();
  for (let y = 0; y < 160; y++) for (let x = 0; x < 240; x++) {
    const i = y * 240 + x;
    for (let k = 0; k < 3; k++) if (Math.abs(fb[i * 4 + k] - ref[i * 3 + k]) > 24) { hit.add(Math.max(0, (y - 2) >> 3)); break; }
  }
  // probe5 prints 20 lines; the font wraps the last one onto line 0, so read line 0 as the last row there.
  const differ = [...hit].sort((a, b) => a - b).map(r => (r === 0 && rows.length >= 20) ? rows[rows.length - 1] : (rows[r] || `line ${r}`));
  const unexpected = differ.filter(r => !LDM_FROM_ROM.has(r.split(' @')[0]));
  const known = differ.length - unexpected.length;
  if (unexpected.length) bad++;
  const values = rows.filter(r => !r.startsWith('WAITCNT'));
  console.log(`${unexpected.length ? 'FAIL' : 'ok  '} probe${n}: ${values.filter(r => !differ.includes(r)).length} of ${values.length} rows identical to mGBA` +
    (known ? `, ${known} known LDM-from-ROM rows differ` : '') + (unexpected.length ? `; UNEXPECTED: ${unexpected.join(', ')}` : ''));
}
await br.close();
console.log(bad ? 'TIMING DIFFERS' : 'ALL OK');
process.exit(bad ? 1 : 0);
