// 1337Boy independent verification (Kehai Interim, 2026-11-04).
//   npm i playwright   (or use a global install)
//   node tests/verify.mjs
//
// Checks, for the blank console and every polyglot cartridge in the repo:
//  1. Polyglot structure: GBA ROM bytes at offset 0 (valid header complement),
//     then the reset sequence, then the HTML. The embedded base64 copy of the
//     ROM equals the file's own first bytes.
//  2. Opened as a web page in Chromium: boots with no page errors, makes no
//     network requests, enforces its CSP (a test fetch is refused), passes all
//     built-in self-tests, and auto-boots its own cartridge (CRC matches).
//  3. The browser's 1337IFY! builder and tools/1337ify.py produce the same
//     bytes, and re-1337ifying a finished cartridge changes nothing.
//  4. Phones: on Pixel 7, Galaxy S8 and iPhone SE layouts nothing sticks out
//     past the right edge of the screen, and the GBA screen keeps its 3:2 shape.
import { chromium, devices } from 'playwright';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import zlib from 'node:zlib';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
let fails = 0; const check = (ok, msg) => { console.log((ok ? 'ok   ' : 'FAIL ') + msg); if (!ok) fails++; };
const RESET = Buffer.from('\n"\'>-->*/</script></style></title></textarea></xmp></iframe></noscript></noembed></noframes>]]></svg></math><!--1337BOY-POLYGLOT-START-->\n', 'latin1');
const crc = b => (zlib.crc32 ? zlib.crc32(b) : 0) >>> 0;

const carts = [path.join(root, '1337boot.1337.gba'), ...fs.readdirSync(path.join(root, 'cartridges')).filter(f => f.endsWith('.1337.gba')).map(f => path.join(root, 'cartridges', f))];
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), '1337boy-'));

// 1 + 3 (Python side)
const roms = {};
for (const c of carts) {
  const d = fs.readFileSync(c), i = d.indexOf(RESET), rom = d.subarray(0, i), name = path.basename(c);
  let chk = 0; for (let k = 0xA0; k < 0xBD; k++) chk = (chk - rom[k]) & 0xFF;
  const b64 = d.toString('latin1').match(/<script id="b1337-rom-b64" type="text\/plain">([^<]*)<\/script>/)[1];
  check(i > 0 && ((chk - 0x19) & 0xFF) === rom[0xBD] && Buffer.from(b64, 'base64').equals(rom),
    `${name}: ROM at offset 0 (${i} bytes, header complement ok), then reset sequence; embedded copy equals the ROM`);
  const html = c.replace(/\.gba$/, '.html');
  check(fs.existsSync(html) && fs.readFileSync(html).equals(d), `${name}: the .html copy is the same bytes`);
  const re = path.join(tmp, 're.gba');
  execFileSync('python3', ['-I', path.join(root, 'tools/1337ify.py'), c, '-o', re, '--template', path.join(root, '1337boy.html')]);
  check(fs.readFileSync(re).equals(d), `${name}: re-1337ifying with tools/1337ify.py reproduces it byte for byte`);
  roms[name] = rom;
}

// 2 + 3 (browser side)
const br = await chromium.launch();
for (const f of [path.join(root, '1337boy.html'), ...carts.map(c => c.replace(/\.gba$/, '.html'))]) {
  const name = path.basename(f);
  const p = await br.newPage({ viewport: { width: 1100, height: 900 } });
  const errs = [], net = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('request', r => { if (!/^(file|data|blob):/.test(r.url())) net.push(r.url()); });
  await p.goto('file://' + f); await p.waitForTimeout(2500);
  const st = await p.evaluate(async () => { const r = await window.B1337.selftest(); return { passed: r.passed, failed: r.failed }; });
  const blocked = await p.evaluate(async () => { try { await fetch('https://example.com/'); return false; } catch { return true; } });
  check(errs.length === 0 && st.failed === 0 && st.passed > 0, `${name}: self-test ${st.passed}/${st.passed + st.failed}, no page errors`);
  check(blocked && net.length === 0, `${name}: CSP refuses a test fetch; no network requests`);
  const romName = name.replace(/\.html$/, '.gba');
  if (roms[romName]) {
    const c = await p.evaluate(() => window.B1337.crc32() >>> 0);
    check(c === crc(roms[romName]), `${name}: auto-booted its own cartridge (CRC32 ${c.toString(16).toUpperCase()})`);
    const built = Buffer.from(await p.evaluate(r => Array.from(window.B1337.buildPolyglot(new Uint8Array(r))), [...roms[romName]]));
    check(built.equals(fs.readFileSync(f)), `${name}: the in-browser 1337IFY! builder produces the same bytes as the file`);
  }
  await p.close();
}

// 4
for (const d of ['Pixel 7', 'Galaxy S8', 'iPhone SE']) {
  const ctx = await br.newContext({ ...devices[d] }); const p = await ctx.newPage();
  await p.goto('file://' + carts[0].replace(/\.gba$/, '.html')); await p.waitForTimeout(2000);
  const r = await p.evaluate(() => { const W = innerWidth; let over = 0;
    for (const el of document.querySelectorAll('body *')) { const b = el.getBoundingClientRect(); if (b.width && b.right > W + 1) over++; }
    const c = document.querySelector('#b1337-canvas').getBoundingClientRect(); return { W, over, ratio: c.width / c.height }; });
  check(r.over === 0 && Math.abs(r.ratio - 1.5) < 0.02, `${d} (${r.W}px): nothing past the right edge (${r.over}); screen ratio ${r.ratio.toFixed(3)}`);
  await ctx.close();
}
await br.close();
console.log(fails ? `${fails} FAILED` : 'ALL OK');
process.exit(fails ? 1 : 0);
