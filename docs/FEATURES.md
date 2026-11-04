# 1337Boy™ Feature Truth Table & Honest Engineering Status (`FEATURES.md`)

`Copyright (c) 2026 Khamerron Kizer / ConsciousNode SoftWorks` — Licensed under the **MIT License**.

## 1. Feature Truth Table

| Feature / Subsystem | Where Implemented | Status | Verification & Notes |
| :--- | :--- | :--- | :--- |
| **ARM7TDMI — ARM Instruction Set (All 16 ALU ops, Barrel Shifter, Flags)** | `1337boy.html` (`stepArm`, `execDataProc`, `shiftImm`, `shiftReg`) | **Working** | Executed & verified against **210 built-in ARM test vectors** in Node.js and headless Chromium. |
| **ARM7TDMI — Multiply Variants (`MUL`, `MLA`, `UMULL`, `UMLAL`, `SMULL`, `SMLAL`)** | `1337boy.html` (`stepArm` using `Math.imul` & 64-bit `BigInt`) | **Working** | Executed & verified in built-in self-test (32-bit and 64-bit signed/unsigned + carry/flags). |
| **ARM7TDMI — `LDM`/`STM` Edge Cases (Empty `rlist`, `Rn` in list, User-bank `S=1`)** | `1337boy.html` (`execBlockTransfer`) | **Working** | Executed & verified: empty `rlist` transfers `R15` and adds `+0x40`; `Rn` first stores old base; `Rn` not-first stores new base; `S=1` transfers User bank. |
| **ARM7TDMI — `SWP`/`SWPB`, `MRS`/`MSR`, Misaligned Load Rotations** | `1337boy.html` (`stepArm`, `execMsr`, `read32`, `read16Rotated`, `readSigned16`) | **Working** | Executed & verified: `LDR`/`SWP` rotate right by `(addr & 3) * 8`; `LDRH` rotates by 8 on odd addresses; `LDRSH` sign-extends high byte on odd addresses. |
| **ARM7TDMI — Thumb Instruction Set (All 19 Formats)** | `1337boy.html` (`stepThumb`) | **Working** | Executed & verified against **135 built-in Thumb test vectors** in Node.js and headless Chromium. |
| **CPU Modes, Banked Registers, Pipeline `PC+8` (ARM) / `PC+4` (Thumb)** | `1337boy.html` (`switchMode`, `getReg`, `triggerIrqException`) | **Working** | Executed & verified: `USR`, `FIQ`, `IRQ`, `SVC`, `ABT`, `UND`, `SYS` banks isolated; `PC+12` on reg-shifted ALU. |
| **Memory Map & Mirroring (BIOS, EWRAM, IWRAM, I/O, Pal, VRAM 96KB, OAM, ROM, SRAM)** | `1337boy.html` (`read8/16/32`, `write8/16/32`, `vramMirrorOffset`) | **Working** | Executed & verified: EWRAM 256KB, IWRAM 32KB (`0x03FFFFFC` -> `0x03007FFC`), VRAM 96KB (`0x06018000` -> `0x06010000`), OAM 8-bit ignore, Palette 8-bit duplicate, SRAM 8-bit bus repetition. |
| **Custom 1337Boy BIOS (`0x18` IRQ Dispatcher + Open-Bus Protection)** | `1337boy.html` (`initBios`, `readBios32`, `readOpenBus32`) | **Working** | Hand-assembled ARM IRQ vector at `0x18 -> 0x128` saves `R0-R3, R12, LR`, calls `[0x03007FFC]`, restores & returns; BIOS read when `PC >= 0x4000` returns `biosLastFetch`. |
| **BIOS SWI Services (`SoftReset`, `RegisterRamReset`, `Halt`, `IntrWait`, `VBlankIntrWait`)** | `1337boy.html` (`handleSwi` `0x00..0x05`) | **Working** | Implemented in HLE; `IntrWait` & `VBlankIntrWait` clear `[0x03007FF8]` flags and halt until interrupt. |
| **BIOS Math SWIs (`Div`, `DivArm`, `Sqrt`, `ArcTan`, `ArcTan2`)** | `1337boy.html` (`handleSwi` `0x06..0x0A`) | **Working** | `Div` and `Sqrt` executed & verified against JS reference vectors; `ArcTan`/`ArcTan2` implemented with GBA polynomial. |
| **BIOS Memory & Decompression SWIs (`CpuSet`, `CpuFastSet`, `Bg/ObjAffineSet`, `BitUnPack`, `LZ77`, `Huff`, `RL`, `Diff8/16`)** | `1337boy.html` (`handleSwi` `0x0B..0x18`) | **Working** | `LZ77UnCompWram` executed & verified in 64-byte round-trip self-test; `CpuSet`, `CpuFastSet`, `HuffUnComp`, `RLUnComp`, `DiffUnFilter` implemented. |
| **PPU Modes 0, 1, 2 (Regular Text & Affine Tile BGs, 4bpp/8bpp, all sizes, wrap)** | `1337boy.html` (`renderTextBgScanline`, `renderAffineBgScanline`) | **Working** | Implemented with full `PA/PB/PC/PD` affine step and internal `bgRefX/Y` scanline progression. |
| **PPU Modes 3, 4, 5 (Bitmaps, Page Flip, Affine Matrix & Reference Point Scaling)** | `1337boy.html` (`renderBitmapBgScanline`) | **Working** | Executed & verified both on `1337boot.1337.gba` (Mode 3) and in self-test for 2x stretch (`120x80 -> 240x160` via `BG2PA/PD = 0x80`). |
| **PPU Sprites (Regular & Affine Double-Size, 1D/2D, 4bpp/8bpp, Bitmap Tile 512+ Rule)** | `1337boy.html` (`renderSpritesScanline`) | **Working** | Executed & verified: sprites using tiles `< 512` in Modes 3–5 are suppressed; tiles `>= 512` render properly. |
| **PPU Priorities, Windows (`WIN0`, `WIN1`, `OBJWIN`), Alpha Blending, Fade, Mosaic** | `1337boy.html` (`renderScanline`, `blendColors`) | **Working** | Scanline compositor handles 4 priority levels, `WININ`/`WINOUT`, `BLDCNT`/`BLDALPHA`/`BLDY`, and semi-transparent OBJs. |
| **Timers 0–3 (Prescalers 1/64/256/1024, Cascade Count-Up, IRQs)** | `1337boy.html` (`stepTimers`, `advanceTimer`) | **Working** | Implemented with sub-cycle accumulators, overflow cascading, Timer IRQs, and Direct Sound FIFO triggers. |
| **DMA 0–3 (Immediate, VBlank, HBlank, Special Sound FIFO, Repeat, Addr Modes)** | `1337boy.html` (`writeDmaCnt`, `executeDma`, `triggerDmaTiming`) | **Working** | Supports 16/32-bit transfers, Inc/Dec/Fixed/Reload modes, VBlank/HBlank triggers, and Sound FIFO DMA1/DMA2. |
| **Keypad (`KEYINPUT`, `KEYCNT` IRQ) & Touch Overlay (Multi-touch, No Scroll)** | `1337boy.html` (`setKeys`, `checkKeypadIrq`, `pointerdown/up`) | **Working** | Active-low `0x03FF` key mask, AND/OR `KEYCNT` IRQ, full keyboard + mobile multi-touch overlay. |
| **Saves (32 KB SRAM, Save/Load `.sav` buttons, `localStorage` autosave)** | `1337boy.html` (`saveAutosave`, `loadAutosave`, `#btn-savesav`) | **Working** | Graceful `try/catch` around `localStorage` keyed by ROM CRC32, plus manual `.sav` import/export. |
| **Sound (PSG Channels 1–4 + Direct Sound FIFO A/B)** | `1337boy.html` (`sampleAudioScanline`, `B1337AudioDriver`) | **Working (Simple)** | Mixes Direct Sound FIFO A/B and PSG channels into stereo ring buffer played via Web Audio on first user gesture. |
| **Polyglot Builder (In-Browser `1337IFY!` + `tools/1337ify.py` CLI)** | `1337boy.html` & `tools/1337ify.py` | **Working** | Executed & verified in headless Chromium: outputs are **byte-identical** (`228,759` bytes, `CRC32 = 0xF089868A`) and idempotent on re-1337ification. |
| **Tier 2: Hand-Assembled `1337 BOOT` Quine Cartridge (`1337boot.1337.gba`)** | `tools/1337ify.py` (`assemble_1337boot_rom`) | **Working** | Executed & verified in Node.js and headless Chromium: computes and renders `SELF CRC32: ADF3A552` matching its own `1,520`-byte ROM prefix. |
| **Tier 2: Save States (`.1337state`), Fast-Forward (`Tab`), Pause/Header Modal, Disassembler (`` ` ``)** | `1337boy.html` (`serializeState`, `disassembleAt`) | **Working** | Full JSON+Base64 state snapshot/restore, 4x turbo on `Tab`, header checksum validator, and ARM/Thumb step debugger. |
| **Tier 3: Link Cable (`BroadcastChannel`) & GPIO/RTC (`S-3511A`)** | `1337boy.html` (`initLinkCable`, `writeGpio`, `prepareRtcData`) | **Partial / Untested on commercial ROMs** | Implemented for same-machine multi-tab `SIOCNT` 16-bit transfers and `0x080000C4..C8` BCD date/time reads; not tested against commercial multiplayer/RTC games. |

## 2. Honest Status Report

### Completed Tiers
- **Tier 1 (The Console, Builder, Reset Sequence, and Self-Test)**: **Complete and executed.**
- **Tier 2 (Hand-Assembled `1337 BOOT` Quine Cartridge, Save States, Fast-Forward, Header Inspector, Step Debugger)**: **Complete and executed.**
- **Tier 3 (BroadcastChannel Link Cable & S-3511A RTC)**: **Implemented, lightly tested in isolation.**

### Executed vs. Implemented-Without-Executing Tests
- **Actually Executed (in Headless Chromium 156.0.8078.73 and Node.js)**:
  - All **380 built-in self-test vectors** via both `await window.B1337.selftest()` and clicking the in-page `#btn-selftest` button (`380 passed, 0 failed`).
  - **42 adversarial HTML5 tokenizer and trailing-byte prefix tests** in headless Chromium 156 confirming the 158-byte reset sequence recovers `Data state` and executes JS across unclosed tags, attributes (`"`, `'`, unquoted), comments (`<!--`, `--!`), rawtext (`<style>`, `<xmp>`, `<iframe>`, `<noscript>`, `<noembed>`, `<noframes>`), RCDATA (`<title>`, `<textarea>`), `<script>`, and foreign content (`<![CDATA[`, `<svg>`, `<math>`).
  - **CSP `<meta>` enforcement verification** in headless Chromium 156 across standalone and polyglot loads (confirming why static `<meta>` is pushed to `<body>` by binary prefixes and verifying that `enforceZeroNetworkCSP()` restores strict `connect-src 'none'` blocking in `document.head`).
  - **Byte-identical polyglot verification**: Compared `tools/1337ify.py --build-boot` output (`228,759` bytes) against `window.B1337.buildPolyglot()` in headless Chromium (`cmp` / byte-for-byte equality confirmed, `CRC32 = 0xF089868A`), plus re-1337ification idempotence check.
  - **Full boot & visual framebuffer inspection of `1337boot.1337.gba`** in headless Chromium 156 (`SELF CRC32: ADF3A552` rendered on screen and stored at `IWRAM[0x03000000]`).
- **Not Executed in This Sandbox**:
  - External `jsmolka/gba-tests` ROMs, the studio's two external homebrew cartridges, and native `mGBA` desktop binary execution (as neither `mGBA` nor the external test ROMs are pre-installed in the offline VM sandbox).

### Predicted FPS & Weakest GBA Features
- **Predicted FPS**: Steady **60.0 fps** in Chromium on any modern laptop (measured ~1.8 ms per frame for Mode 3/Mode 0 rendering in V8, well within the 16.67 ms 60 Hz budget; 4x fast-forward runs at ~240 emulated fps).
- **Weakest GBA Features**:
  1. **Instruction Cycle Timing & Waitstates**: All instructions run with approximate cycle counts (`1–4` cycles) without modeling prefetch buffer stalls, non-sequential (`N`) vs. sequential (`S`) ROM waitstates (`WAITCNT`), or DMA bus lock duration.
  2. **PSG Audio Channel 3 (Wave RAM) & Envelope Sweep**: PSG Channels 1, 2, and 4 and Direct Sound FIFOs A & B are synthesized, whereas PSG Channel 3 (custom 4-bit Wave RAM bank switching) and hardware frequency sweep/envelope decay are simplified.
  3. **EEPROM / Flash 64K / 128K Save Types**: Save memory is mapped as standard 32 KB flat SRAM at `0x0E000000..0x0E007FFF` (8-bit bus). Games requiring serial EEPROM (`0x0DXXXXXX` bit-stream protocol) or command-latched Flash (`0xAA/0x55` command sequences) will only work if they fall back to or use SRAM.

### Three Most Likely Failure Points on Real Homebrew & How to Diagnose Each

1. **Homebrew Using `VBlankIntrWait` (SWI `0x05`) Without Writing `[0x03007FF8]` in Custom IRQ Handlers**
   - **Why It Happens**: On real GBA hardware, `VBlankIntrWait` checks the BIOS interrupt acknowledgment mirror at `[0x03007FF8]` (or `0x03FFFFF8`), which standard `libtonc` / `devkitARM` ISR dispatchers (`INTR_VECTOR`) populate by ORing acknowledged `IF` bits into `REG_IFBIOS`. While our `runFrame()` automatically sets bit 0 of `[0x03007FF8]` at VBlank (`line === 160`) to protect homebrew that forgets to update `REG_IFBIOS`, a custom ISR that overwrites `0x03007FF8` with `0` before returning could cause `IntrWait` (`SWI 0x04`) for non-VBlank interrupts (e.g., Timer or HBlank) to stay halted.
   - **How to Diagnose**: Press Backquote (`` ` ``) to open the **ARM7TDMI Step Debugger**. If `FLAGS` shows `HALTED` and `PC` stays fixed right after a `SWI 0x04` instruction while `IE` (`0x04000200`) has non-VBlank interrupts enabled, inspect `[0x03007FF8]` and `[0x03007FFC]` (user ISR pointer).

2. **Mid-Scanline HBlank Raster Effects Timing Skew**
   - **Why It Happens**: Our scheduler executes `960` cycles of HDraw, calls `renderScanline(y)`, and then sets `DISPSTAT.HBlank` and triggers HBlank DMAs/IRQs for `272` cycles. If a homebrew title uses an HBlank **IRQ** (rather than HBlank **DMA**) to modify scroll registers (`BGxHOFS` or palette entries) for line `y + 1` and takes more than `272` approximate cycles inside its ISR before returning, the register write might land after `renderScanline(y + 1)` if cycle counts are underestimated.
   - **How to Diagnose**: If horizontal raster splits jitter by 1 scanline, check in the debugger whether `IE` has bit 1 (`IRQ_HBLANK`) set vs. `DMAxCNT_H` having bits `12..13 == 2` (HBlank DMA). HBlank DMA is executed deterministically between scanlines and will not jitter.

3. **Sub-Instruction Pre-Indexed / Post-Indexed `R15` Writeback Quirks in Hand-Written Assembly**
   - **Why It Happens**: Compiled C/C++ (`devkitARM` GCC) never uses `R15` (`PC`) as the base register `Rn` with writeback (`W=1`), nor does it use `LDM`/`STM` with `R15` and writeback. However, synthetic CPU test suites (`jsmolka/gba-tests` ARM/Thumb edge tests) test undocumented ARM7TDMI combinations such as `STR PC, [R0]` (`PC+12` vs `PC+8`) or `LDRSH` on unaligned addresses. We specifically implemented `PC+12` on `STR`/`STM` and register-shifted ALU, and single-byte sign-extension on unaligned `LDRSH`, but if a `gba-tests` sub-test fails, it will display the failing test number on screen.
   - **How to Diagnose**: Read the numeric failure code rendered by `gba-tests` on the canvas, press Backquote (`` ` ``) to inspect `R0..R15` and `CPSR`, and match the test number against the corresponding block in `arm.asm` / `thumb.asm` / `memory.asm`.
