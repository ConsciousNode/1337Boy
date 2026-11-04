# 1337Boy™: the cartridge that is its own console

**[▶ Open the console](https://consciousnode.github.io/1337Boy/)** · [play *Wrongfully Accused*](https://consciousnode.github.io/1337Boy/cartridges/wrongfully-accused.1337.html) · [play *GBA-Craft*](https://consciousnode.github.io/1337Boy/cartridges/gba-craft.1337.html) · [the 1337 BOOT demo](https://consciousnode.github.io/1337Boy/1337boot.1337.html)
(The links work once GitHub Pages is switched on for this repo.)

Every `.1337.gba` file here is **one file that is two things**: a Game Boy Advance ROM (mGBA, a flash cart) and a web page that carries a GBA emulator written from scratch and plays the cartridge it's part of. The `.1337.html` next to each one is the exact same bytes with a different name.

| File | What |
|---|---|
| `1337boy.html` (= `index.html`) | The blank console, **1.0.1**: insert any `.gba`, or 1337IFY! it into a polyglot |
| `1337boot.1337.gba` / `.html` | The hand-assembled demo cartridge, which checksums itself |
| `cartridges/wrongfully-accused.1337.gba` / `.html` | The studio's Edo courtroom game, as its own console |
| `cartridges/gba-craft.1337.gba` / `.html` | The studio's voxel sandbox, as its own console |
| `tools/1337ify.py` | Command-line builder (Python 3, standard library only) |
| `tests/` | Independent tests; results in [TESTING.md](TESTING.md) |

**Versions:** 1.0 is Argon's original, as delivered (commit `ea62fcd`). 1.0.1 makes the console fit phone screens; the emulator is unchanged.

**Credits:** concept and direction, Khamerron Kizer · written by Gemini 4 Argon · testing and the 1.0.1 phone fix, Kehai Interim (Claude).

---

*Argon's original README follows.*

# 1337Boy™ COLOR ADVANCE TURBO (999,999 GAMES IN 1!)

> **CONSCIOUSNODE SOFTWORKS // XINU EDITION**
> *"FLASH IT TO A CART, OR DOUBLE-CLICK IT IN A BROWSER. THE CARTRIDGE IS ITS OWN CONSOLE."*
> `Copyright (c) 2026 Khamerron Kizer / ConsciousNode SoftWorks` — Licensed under the **MIT License**.

Welcome to **1337Boy™ COLOR ADVANCE TURBO**, the self-hosting Game Boy Advance polyglot system engineered under the **Xinu** house philosophy (the inverse of Unix): **single file, zero dependencies, offline-first, and constraint generates novelty**.

A 1337Boy cartridge is **one file** that is, byte-for-byte, both:
1. **A valid Game Boy Advance ROM** (`0x08000000` entry branch, valid 192-byte cartridge header, unmodified binary prefix) that boots on real GBA hardware via a flash cart and in emulators like mGBA.
2. **A valid HTML5 document** that, opened in any modern browser, executes a hand-written, zero-dependency ARM7TDMI + GBA emulator and boots the exact cartridge it carries.

Name it `.1337.gba` and drop it into mGBA or an EverDrive. Name the **exact same bytes** `.1337.html` and open it in Chromium, Firefox, or Safari. Both play the same cartridge.

## Quick Start & Operating Instructions

### 1. Playing the Blank Console (`1337boy.html`)
Open `1337boy.html` directly in your browser:
- **Insert Any Cartridge**: Drag and drop any `.gba` ROM onto the screen bezel (or click **INSERT .GBA**) to boot and play immediately at 60 fps.
- **Play the Built-in Quine Demo**: Click **BOOT 1337 DEMO** to run the hand-assembled `1337 BOOT` cartridge (`1,520` bytes, `CRC32 = 0xADF3A552`), which computes and displays the CRC32 of its own `0x08000000` ROM region in real time.
- **Forge a Polyglot in the Browser**: Load any `.gba` ROM and click **1337IFY! (EXPORT POLYGLOT)** to download `<title>.1337.gba` and `<title>.1337.html`. Both files are byte-identical polyglots constructed from the page's pristine `<style id="b1337-style">` and `<script id="b1337-core">` source tags.

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

- **Byte-Identical Guarantee**: `tools/1337ify.py` produces output that is byte-for-byte identical to the in-browser **1337IFY!** button for the same ROM.
- **Idempotent Re-1337ification**: Passing an already-1337ified `.1337.gba` or `.1337.html` file back into `tools/1337ify.py` (or the browser dropzone) automatically detects the reset sequence + `<!--1337BOY-POLYGLOT-START-->` marker, strips the old HTML tail, and rebuilds cleanly without nesting.
- **Tokenizer Safety Scanner**: `tools/1337ify.py` scans every ROM case-insensitively before building, refuses any ROM containing `<plaintext` (which enters the unrecoverable HTML5 PLAINTEXT state), and logs all other tag-like openings (`<` followed by an ASCII letter, `!`, `/`, or `?`).

### 3. Running the Built-In Hardware Self-Test (380 Vectors)
1337Boy ships with **380 built-in hardware verification tests** covering ARM ALU/shifter/flags (210 cases), Thumb instructions across all 19 formats (135 cases), memory mirroring/misaligned rotated reads/SRAM 8-bit bus, BIOS `Div`/`Sqrt`/`LZ77` round-trip, PPU Mode 3 affine 2x scaling & bitmap-mode OBJ tile 512+ restrictions, and in-memory polyglot round-trip verification:
- **In-Page Button**: Click **SELF-TEST** on the top toolbar (or on the splash dropzone).
- **JavaScript Hook**: Call `await window.B1337.selftest()` from the console or test runner, which resolves to `{ passed, failed, results: [{ name, pass, detail }] }`.

### 4. Automation Hooks for Headless Testing
When loaded in headless Chromium or any browser, `window.B1337` exposes:

| Hook | Signature & Return Value |
| :--- | :--- |
| `window.B1337.loadRom(u8)` | Loads a `Uint8Array` (raw `.gba` or `.1337.gba` polyglot), resets the console, and returns the 32-bit unsigned ROM `CRC32`. |
| `window.B1337.runFrames(n)` | Steps `n` complete frames (228 scanlines x 1,232 cycles = 280,896 cycles/frame) and returns the `240x160x4` RGBA `Uint8ClampedArray`. |
| `window.B1337.setKeys(mask)` | Sets active button bitmask (`bit 0=A, 1=B, 2=Select, 3=Start, 4=Right, 5=Left, 6=Up, 7=Down, 8=R, 9=L`). |
| `window.B1337.frameBuffer()` | Returns a copy of the `240x160x4` RGBA `Uint8ClampedArray` framebuffer (`153,600` bytes). |
| `window.B1337.crc32()` | Returns the unsigned 32-bit IEEE 802.3 CRC32 of the loaded ROM prefix. |
| `window.B1337.sram()` | Returns a copy of the 32 KB `Uint8Array` (`32,768` bytes) Game Pak SRAM. |
| `window.B1337.selftest()` | Runs all 380 built-in tests and returns a `Promise<{passed, failed, results}>`. |

## Controls & Quality-of-Life Features

| GBA Input / Feature | Desktop Keyboard | Mobile / Touch Overlay |
| :--- | :--- | :--- |
| **D-Pad (Up / Down / Left / Right)** | Arrow Keys | On-screen D-Pad (multi-touch, scroll-locked) |
| **A Button** | `X` | Red `A` button |
| **B Button** | `Z` | Yellow `B` button |
| **L / R Shoulder Buttons** | `A` / `S` | Top `L` / `R` shoulder buttons |
| **START / SELECT** | `Enter` / `Backspace` or `Shift` | Center `START` / `SELECT` pill buttons |
| **Fast-Forward (4x Turbo)** | Hold `Tab` | Indicator LED turns Gold (`TURBO 4X`) |
| **Step Debugger & Disassembler** | Backquote (`` ` ``) | Toolbar **DEBUG (`)** button |
| **Pause & Header Inspector** | Toolbar **PAUSE / INFO** | Displays Title, Code, Maker, Checksum, & Validity |
| **Save / Load State** | Toolbar **SAVE .1337STATE** / **LOAD STATE** | Full JSON + Base64 hardware snapshot |
| **Save / Load SRAM (`.sav`)** | Toolbar **SAVE .SAV** / **LOAD .SAV** | 32 KB raw `.sav` + graceful `localStorage` autosave |

## Prior Art & Legal Note on Lockout Header Bytes

### Credit to Prior Art
- **PoC||GTFO 14:12** (*"A Polyglot PDF/ZIP/NES ROM"*): Demonstrated a single file valid as a PDF document, ZIP archive, and NES ROM that prints its own MD5 digest.
- **Vi Grey (PoC||GTFO 18:04)**: Built an NES ROM that is simultaneously a valid ZIP archive containing its own source code (a hardware/archive quine).
- **Kamila Szewczyk (Jan 2026)**: Built a PE/ELF/HTML polyglot Snake game placing binary executable headers at offset `0x00` followed by an HTML document that cleans up stray prefix garbage.
- **Kyle Conroy (2014)**: Coined *"HTML ROMs"* for self-contained, single-file offline web applications.

### Interoperability & the GBA Cartridge Header Logo (*Sega v. Accolade*)
- **1337Boy (`1337boy.html`) contains zero Nintendo BIOS code and zero commercial ROM data.** Its 16 KB BIOS (`0x00000000..0x00003FFF`) and all 21 SWI routines are written from scratch from hardware specifications.
- **GBA Cartridge Header (`0x04..0x9F`)**: Real Game Boy Advance hardware verifies a mandatory 156-byte compressed bitmap at cartridge offset `0x04..0x9F` before jumping to `0x08000000`. When 1337Boy wraps a user's ROM, those bytes come from the user's ROM. For the hand-assembled `1337 BOOT` demo cartridge (`1337boot.1337.gba`), `tools/1337ify.py` emits the mandatory 156-byte header sequence strictly as required for hardware lockout compliance, following the well-established interoperability precedent of *Sega Enterprises Ltd. v. Accolade, Inc.*, 977 F.2d 1510 (9th Cir. 1992).
