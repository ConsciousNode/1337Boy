// Run jsmolka's GBA test ROMs through 1337Boy and save what each one shows
// (Kehai Interim, 2026-11-04). Each test ROM prints "All tests passed" or
// "Failed test N" on screen.
//   git clone --depth 1 https://github.com/jsmolka/gba-tests
//   node tests/gba-tests.mjs path/to/gba-tests [outdir]
// It also runs any other .gba you pass as path/to/file.gba.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = process.argv[2]; const out = process.argv[3] || 'gba-test-results';
if (!src) { console.log('usage: node tests/gba-tests.mjs path/to/gba-tests [outdir]'); process.exit(1); }
const roms = src.endsWith('.gba') ? [src] : ['arm/arm.gba', 'thumb/thumb.gba', 'memory/memory.gba', 'bios/bios.gba', 'nes/nes.gba', 'ppu/hello.gba', 'ppu/shades.gba', 'ppu/stripes.gba'].map(r => path.join(src, r)).filter(fs.existsSync);
fs.mkdirSync(out, { recursive: true });
const br = await chromium.launch(); const p = await br.newPage();
await p.addInitScript(() => { window.requestAnimationFrame = () => 0; }); // only runFrames() advances the console
await p.goto('file://' + path.join(root, '1337boy.html')); await p.waitForTimeout(1500);
for (const r of roms) {
  const png = await p.evaluate(async rom => {
    window.B1337.loadRom(new Uint8Array(rom)); const fb = window.B1337.runFrames(240);
    const c = new OffscreenCanvas(240, 160); c.getContext('2d').putImageData(new ImageData(new Uint8ClampedArray(fb), 240, 160), 0, 0);
    const b = await c.convertToBlob({ type: 'image/png' }); return Array.from(new Uint8Array(await b.arrayBuffer()));
  }, [...fs.readFileSync(r)]);
  const name = path.basename(r, '.gba');
  fs.writeFileSync(path.join(out, name + '.png'), Buffer.from(png));
  console.log(`${name}: ${path.join(out, name + '.png')}`);
}
await br.close();
