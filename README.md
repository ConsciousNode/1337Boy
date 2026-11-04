# 1337Boy™ COLOR ADVANCE TURBO v1.1 (999,999 GAMES IN 1!)

> **CONSCIOUSNODE SOFTWORKS // XINU EDITION v1.1**
> *"FLASH IT TO A CART, OR DOUBLE-CLICK IT IN A BROWSER. THE CARTRIDGE IS ITS OWN CONSOLE."*
> `Copyright (c) 2026 Khamerron Kizer / ConsciousNode SoftWorks` — Licensed under the **MIT License**.

Welcome to **1337Boy™ COLOR ADVANCE TURBO v1.1**, the self-hosting Game Boy Advance polyglot system engineered under the **Xinu** house philosophy (the inverse of Unix): **single file, zero dependencies, offline-first, and constraint generates novelty**.

A 1337Boy cartridge is **one file** that is, byte-for-byte, both:
1. **A valid Game Boy Advance ROM** (`0x08000000` entry branch, valid 192-byte cartridge header, unmodified binary prefix) that boots on real GBA hardware via a flash cart and in emulators like mGBA.
2. **A valid HTML5 document** that, opened in any modern browser, executes a hand-written, zero-dependency ARM7TDMI + GBA emulator and boots the exact cartridge it carries.

Name it `.1337.gba` and drop it into mGBA or an EverDrive. Name the **exact same bytes** `.1337.html` and open it in Chromium, Firefox, or Safari. Both play the same cartridge.

## v1.1.1 (Kehai Interim, 2026-11-04)

Argon's 1.1 tested independently against mGBA and jsmolka's gba-tests (all 13 pass). Two fixes on top, details and evidence in [TESTING.md](TESTING.md):

- **CPU timing now matches mGBA instruction for instruction.** Six homebrew probe ROMs (`tests/timing/`) time 47 kinds of instruction loop under both `WAITCNT` settings (87 measurements). 1.1 matched mGBA in 38 of them. 1.1 undercharged long multiplies (`SMULL`/`UMULL`, a flat 3 cycles) and Thumb `MUL`. It didn't charge the non-sequential fetch after a load or store from ROM code, and its prefetch buffer used a different model from mGBA's. 1.1.1 matches on every row except one deliberate choice: an `LDM` that reads cartridge data follows GBATEK. That was why *GBA-Craft* rolled a different world seed than in mGBA; now its seed, world and frame rate are identical.
- **Games run at the GBA's own 59.73 Hz on any screen.** 1.1 still ran one GBA frame per display refresh, so 90/120/144 Hz phones played games 1.5 to 2.4 times too fast. This is the 1.0.2 fix, carried over and combined with 1.1's speed control and fast-forward.

Every cartridge in the repo was rebuilt from the 1.1.1 console. Argon's 1.1 is preserved exactly in the commit before this one.

## What's New in v1.1

- **Tier 1 Correctness Upgrades**:
  - **Thumb `STMIA` & `PUSH` Empty Register List (`thumb.gba` test 229)**: `STMIA Rb!, {}` (`0xC000`) and `PUSH {}` (`0xB400`) now store `PC + 6` (`instr_addr + 6`, matching the pipeline PC seen by the next instruction) and adjust the base/stack pointer by `0x40`.
  - **2-Stage ARM & Thumb Instruction Prefetch Pipeline (`nes.gba` test 1)**: Models the hardware 2-slot prefetch queue (`pipe0`, `pipe1`, `pipePc`), executing already-fetched opcodes when self-modifying code overwrites `PC + 4` (ARM) or `PC + 2` (Thumb), and flushing on any write to `R15` (`B`, `BL`, `BX`, `LDR PC`, `LDM {PC}`, `POP {PC}`, `ALU Rd=15`, `SWI`, `IRQ`).
  - **Hardware-Accurate BIOS Open-Bus Reads (`bios.gba` test 3)**: Tracks the exact BIOS fetch latch across all 4 hardware states: `0xE129F000` after startup/`SoftReset`/`IntrWait`/`VBlankIntrWait`, `0xE25EF004` **during** an IRQ, `0xE55EC002` **after** IRQ return (`SUBS PC, LR, #4` at `0x013C`), and `0xE3A02004` after a `SWI` (plus `SWI 0x0D` `GetBiosChecksum` returning `0xBAAE187F`).
  - **All 4 Save Memory Types (`SRAM`, `FLASH64`, `FLASH128`, `EEPROM` 512B/8KB, plus `NONE`)**:
    - **SRAM (32 KB)**: Initialized to `0xFF` (erased state) and mirrored across the full `0x0E000000–0x0FFFFFFF` region (`save/sram.gba` & `save/none.gba`).
    - **Flash 64 KB & 128 KB**: Full command state machine (`0xAA` at `0x5555`, `0x55` at `0x2AAA`, commands `0x90` Chip ID, `0xF0` Reset, `0x80` Erase setup, `0x10` Chip erase, `0x30` 4 KB Sector erase, `0xA0` Byte program, and `0xB0` Bank switch for 128 KB), using Macronix `MX29L512` (`0x1CC2`) for 64 KB and Sanyo `LE26FV10N1TS` (`0x1362`) for 128 KB (`save/flash64.gba` & `save/flash128.gba`).
    - **EEPROM 512 B & 8 KB**: Serial bitstream protocol over DMA3 at `0x0D000000–0x0DFFFFFF` with 6-bit vs. 14-bit address width inferred from DMA3 transfer length (`9`/`73` vs. `17`/`81` halfwords) and ready-bit (`1`) polling.
    - **Auto-Detection + Heuristic Fallback + UI Override**: Scans ROM bytes for `SRAM_V`, `SRAM_F_V`, `FLASH_V`, `FLASH512_V`, `FLASH1M_V`, `EEPROM_V`, falls back heuristically when no string is present, and provides a manual override dropdown in the **PAUSE / INFO** modal and `window.B1337.setSaveType()`.
  - **Deterministic Headless Stepping (`window.B1337.setRealtime(false|true)`)**: Pauses the `requestAnimationFrame` loop so headless test runners calling `B1337.runFrames(n)` step the exact requested frame count.
- **Tier 2 Accuracy Upgrades**:
  - **Hardware Cycle Timing (`WAITCNT` `0x04000204`, Prefetch Buffer, and DMA Stalls)**: Implements non-sequential (`N`) and sequential (`S`) waitstate tables for ROM WS0/WS1/WS2 (16-bit and 32-bit), SRAM waitstates, EWRAM (3 cycles 8/16-bit, 6 cycles 32-bit), VRAM/Palette/OAM bus width rules, the Game Pak Prefetch Buffer (`WAITCNT` bit 14), Booth multiplier internal cycles, and DMA bus stall cycles.
  - **Sound Upgrade (PSG Channel 3 Wave RAM, Envelopes/Sweep, `SOUNDBIAS`, and `AudioWorklet`)**: Full dual-bank 32/64-sample Wave RAM at `0x04000090–0x0400009F`, 512 Hz PSG Frame Sequencer (256 Hz length counters, 128 Hz Channel 1 frequency sweep, 64 Hz volume envelopes), `SOUNDCNT_X` active channel flags, `SOUNDBIAS` bit-depth quantization, and an inline `Blob` URL `AudioWorklet` driver with automatic `ScriptProcessorNode` fallback.
- **Tier 3 Standard Emulator Toolkit**:
  - **Physical Gamepad API (`navigator.getGamepads()`) + Custom Key Remapping** persisted to `localStorage`.
  - **4 Save-State Slots (`F1–F4` Load / `Shift+F1–F4` Save)** with live 60x40 screen thumbnails and per-ROM persistence, plus `.1337state` file export/import.
  - **Real-Time Rewind Ring Buffer** (hold `R` or the on-screen `REWIND` button to step backward through 15 seconds of gameplay).
  - **Speed Control (`0.25x`, `0.5x`, `1x`, `2x`, `4x`, `8x`) & Single-Frame Advance (`+1 FRAME` / `N`)**.
  - **PNG Screenshot Button (`SNAP PNG`)**, **Integer Scaling (`INT SCALE`)**, **Subpixel LCD Grid Overlay (`LCD GRID`)**, **GBA AGB-001 LCD Color Correction (`GBA COLOR`)**, **Fullscreen Toggle (`FULLSCREEN`)**, **Offline Recent ROMs Library (`IndexedDB`)**, and **Memory Cheats Engine (`ADDR:VAL` & CodeBreaker)**.
  - **Preserved 1.0.1 Phone Layout CSS**: Verified at `360px`, `412px`, and `600px` mobile viewports with zero horizontal overflow (`scrollWidth == clientWidth`).

## Quick Start & Operating Instructions

### 1. Playing the Blank Console (`1337boy.html`)
Open `1337boy.html` directly in your browser:
- **Insert Any Cartridge**: Drag and drop any `.gba` ROM onto the screen bezel (or click **INSERT .GBA**) to boot and play immediately at 60 fps.
- **Play the Built-in Quine Demo**: Click **BOOT 1337 DEMO** to run the hand-assembled `1337 BOOT` cartridge (`1,520` bytes, `CRC32 = 0xADF3A552`), which computes and displays the CRC32 of its own `0x08000000` ROM region in real time.
- **Forge a Polyglot in the Browser**: Load any `.gba` ROM and click **1337IFY! (EXPORT POLYGLOT)** to download `<title>.1337.gba` and `<title>.1337.html`. Both files are byte-identical polyglots constructed from the page's pristine `<style id="b1337-style">` and `<script id="b1337-core">` source tags.

#### On Android: copy, don't rename

Kham tested 1.1.1 on his phone. The exported `.1337.html` opens and plays, the exported `.1337.gba` loads as a ROM, and renaming the `.html` to `.gba` works too. Going the other way, renaming the `.gba` to `.html`, showed the file as raw text.

The bytes aren't the problem: both exports are identical. Android file managers hand the file to Chrome (a `content://` address) along with the type Android recorded when the file was saved, and renaming often doesn't update that type. Chrome then can't treat the file as a web page by looking at it, because a polyglot has to start with the GBA ROM, not with `<html>`. Desktop browsers go by the file name, so renaming works there.

On Android:
- open the `.1337.html` export directly, or
- make a **copy** named `.html` instead of renaming (a new file gets its type from its name), or
- open the cartridge from the GitHub Pages site, which serves it as HTML.

### 2. Forging Polyglots from the Command Line (`tools/1337ify.py`)
Use the zero-dependency Python 3 CLI builder (`tools/1337ify.py`, standard library only) to convert any homebrew `.gba` ROM into a self-hosting 1337Boy cartridge:

```bash
# Convert any .gba ROM into a byte-identical 1337Boy polyglot
python3 tools/1337ify.py game.gba -o game.1337.gba

# Copy or rename to .html (identical bytes) to open in a browser
cp game.1337.gba game.1337.html

# Hand-assemble the 1337 BOOT demo cartridge from scratch and 1337ify it
python3 tools/1337ify.py --build-boot -o 1337boot.1337.gba

# Emit only the raw 1,520-byte hand-assembled 1337boot.gba ROM
python3 tools/1337ify.py --raw-boot-only -o 1337boot.gba
```

### 3. Running the Built-In Hardware Self-Test (391 Vectors)
1337Boy v1.1 ships with **391 built-in hardware verification tests** covering ARM ALU/shifter/flags (210 cases), Thumb instructions across all 19 formats including empty-list `STMIA`/`PUSH` (137 cases), ARM & Thumb 2-stage prefetch pipeline self-modifying code (`nes` test 1), BIOS open-bus states (`bios` test 1–3), all 4 save memory protocols (`SRAM`, `FLASH64`, `FLASH128`, `EEPROM`), `WAITCNT` timing tables, PSG Channel 3 dual-bank Wave RAM, PPU Mode 3 affine scaling & bitmap-mode OBJ tile 512+ restrictions, and in-memory polyglot round-trip verification:
- **In-Page Button**: Click **SELF-TEST** on the top toolbar (or on the splash dropzone).
- **JavaScript Hook**: Call `await window.B1337.selftest()` from the console or test runner, which resolves to `{ passed, failed, results: [{ name, pass, detail }] }`.

### 4. Automation Hooks for Headless Testing
When loaded in headless Chromium or any browser, `window.B1337` exposes:

| Hook | Signature & Return Value |
| :--- | :--- |
| `window.B1337.setRealtime(bool)` | Pauses (`false`) or resumes (`true`) the `requestAnimationFrame` loop so `runFrames(n)` steps an exact deterministic number of frames. |
| `window.B1337.loadRom(u8)` | Loads a `Uint8Array` (raw `.gba` or `.1337.gba` polyglot), resets the console, and returns the 32-bit unsigned ROM `CRC32`. |
| `window.B1337.runFrames(n)` | Steps `n` complete frames (228 scanlines x 1,232 cycles = 280,896 cycles/frame) and returns the `240x160x4` RGBA `Uint8ClampedArray`. |
| `window.B1337.setKeys(mask)` | Sets active button bitmask (`bit 0=A, 1=B, 2=Select, 3=Start, 4=Right, 5=Left, 6=Up, 7=Down, 8=R, 9=L`). |
| `window.B1337.frameBuffer()` | Returns a copy of the `240x160x4` RGBA `Uint8ClampedArray` framebuffer (`153,600` bytes). |
| `window.B1337.crc32()` | Returns the unsigned 32-bit IEEE 802.3 CRC32 of the loaded ROM prefix. |
| `window.B1337.saveType()` | Returns the active save memory type (`'SRAM'`, `'FLASH64'`, `'FLASH128'`, `'EEPROM'`, `'AUTO'`, `'NONE'`). |
| `window.B1337.setSaveType(type)` | Overrides the save memory type (`'AUTO'`, `'SRAM'`, `'FLASH64'`, `'FLASH128'`, `'EEPROM512'`, `'EEPROM8K'`, `'NONE'`). |
| `window.B1337.sram()` | Returns a `Uint8Array` copy of the active battery save buffer (`32 KB` SRAM, `64 KB`/`128 KB` Flash, or `512 B`/`8 KB` EEPROM). |
| `window.B1337.setSpeed(mult)` | Sets the emulation speed multiplier (`0.25`, `0.5`, `1`, `2`, `4`, `8`). |
| `window.B1337.buildPolyglot(u8)` | Builds and returns a byte-exact `.1337.gba` / `.1337.html` polyglot `Uint8Array` from `u8`. |
| `window.B1337.selftest()` | Runs all 391 built-in tests and returns a `Promise<{passed, failed, results}>`. |

## Prior Art & Legal Note on Lockout Header Bytes

### Credit to Prior Art
- **PoC||GTFO 14:12** (*"A Polyglot PDF/ZIP/NES ROM"*): Demonstrated a single file valid as a PDF document, ZIP archive, and NES ROM that prints its own MD5 digest.
- **Vi Grey (PoC||GTFO 18:04)**: Built an NES ROM that is simultaneously a valid ZIP archive containing its own source code (a hardware/archive quine).
- **Kamila Szewczyk (Jan 2026)**: Built a PE/ELF/HTML polyglot Snake game placing binary executable headers at offset `0x00` followed by an HTML document that cleans up stray prefix garbage.
- **Kyle Conroy (2014)**: Coined *"HTML ROMs"* for self-contained, single-file offline web applications.

### Interoperability & the GBA Cartridge Header Logo (*Sega v. Accolade*)
- **1337Boy (`1337boy.html`) contains zero Nintendo BIOS code and zero commercial ROM data.** Its 16 KB BIOS (`0x00000000..0x00003FFF`) and all 22 SWI routines are written from scratch from hardware specifications.
- **GBA Cartridge Header (`0x04..0x9F`)**: Real Game Boy Advance hardware verifies a mandatory 156-byte compressed bitmap at cartridge offset `0x04..0x9F` before jumping to `0x08000000`. When 1337Boy wraps a user's ROM, those bytes come from the user's ROM. For the hand-assembled `1337 BOOT` demo cartridge (`1337boot.1337.gba`), `tools/1337ify.py` emits the mandatory 156-byte header sequence strictly as required for hardware lockout compliance, following the well-established interoperability precedent of *Sega Enterprises Ltd. v. Accolade, Inc.*, 977 F.2d 1510 (9th Cir. 1992).
