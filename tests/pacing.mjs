// 1337Boy frame pacing check (Kehai Interim, 2026-11-04).
//   node tests/pacing.mjs [cartridge.1337.html]
//
// Fakes 60/90/120/144 Hz displays (requestAnimationFrame driven by a fake clock) and counts how
// many GBA frames the page runs per second of display time. A real GBA draws 59.73 frames a
// second (280896 cycles at 16.78 MHz), whatever screen it is shown on. Then, at 120 Hz, checks
// every speed setting and the Tab fast-forward.
import { chromium } from 'playwright';
import path from 'node:path';

const here = path.dirname(new URL(import.meta.url).pathname);
const page = path.resolve(process.argv[2] || path.join(here, '..', 'cartridges', 'wrongfully-accused.1337.html'));
const GBA_FPS = 16777216 / 280896;

async function measure(br, hz, setup) {
  const p = await br.newPage();
  await p.addInitScript(hz => { const iv = 1000 / hz; window.__fakeT = 0;
    window.requestAnimationFrame = cb => setTimeout(() => { window.__fakeT += iv; cb(window.__fakeT); }, 0); }, hz);
  await p.goto('file://' + page); await p.waitForTimeout(1500);
  if (setup) await setup(p);
  const r = await p.evaluate(async () => { const g = window.B1337.gba; let n = 0; const o = g.runFrame.bind(g);
    g.runFrame = () => { n++; return o(); };
    const t0 = window.__fakeT; await new Promise(r => setTimeout(r, 3000)); return { n, s: (window.__fakeT - t0) / 1000 }; });
  await p.close();
  return r.n / r.s;
}

const br = await chromium.launch();
let bad = 0;
const check = (label, got, want) => { const ok = Math.abs(got - want) <= want * 0.02 + 0.3; if (!ok) bad++;
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${label}: ${got.toFixed(1)} GBA frames/s (want ${want.toFixed(1)})`); };
for (const hz of [60, 90, 120, 144]) check(`${hz} Hz display`, await measure(br, hz), GBA_FPS);
for (const sp of [0.25, 0.5, 2, 4, 8])
  check(`speed ${sp}x @ 120 Hz`, await measure(br, 120, p => p.evaluate(v => { const s = document.getElementById('sel-speed');
    s.value = String(v); s.dispatchEvent(new Event('change')); }, sp)), GBA_FPS * sp);
check('Tab fast-forward @ 120 Hz', await measure(br, 120, p => p.keyboard.down('Tab')), GBA_FPS * 4);
await br.close();
console.log(bad ? 'PACING WRONG' : 'ALL OK');
process.exit(bad ? 1 : 0);
