# 1337Boy™ System Architecture & Polyglot File Layout

`Copyright (c) 2026 Khamerron Kizer / ConsciousNode SoftWorks` — Licensed under the **MIT License**.

## 1. Polyglot File Layout & Byte Offsets (`1337boot.1337.gba`)

A 1337Boy cartridge is a linear concatenation of three regions with zero recursion. Below is the exact byte-offset diagram for the pre-built **`1337boot.1337.gba`** (`228,759` bytes total):

```
+-----------------------------------------------------------------------------+
| OFFSET (HEX / DEC)        | LENGTH     | REGION & HARDWARE/BROWSER ROLE     |
+---------------------------+------------+------------------------------------+
| 0x00000000 (0)            | 1,520 B    | [1] UNMODIFIED GBA ROM PREFIX      |
|   0x00000000..0x00000003  |   4 B      |   ARM Branch: EA00002E (B 0xC0)    |
|   0x00000004..0x0000009F  |   156 B    |   GBA Boot Header Bitmap           |
|   0x000000A0..0x000000AB  |   12 B     |   Title: "1337BOOT    "            |
|   0x000000AC..0x000000B1  |   6 B      |   Game Code "B13E", Maker "CN"     |
|   0x000000B2..0x000000BF  |   14 B     |   Fixed 0x96, Ver 1, Chk 0x52      |
|   0x000000C0..0x00000413  |   852 B    |   ARM7TDMI Mode 3 + CRC32 Code     |
|   0x00000414..0x000005EF  |   476 B    |   Literal Pool, Strings, 8x8 Font  |
|                           |            |   -> ROM CRC32 = 0xADF3A552        |
+---------------------------+------------+------------------------------------+
| 0x000005F0 (1,520)        | 158 B      | [2] HTML5 TOKENIZER RESET SEQUENCE |
|   0x000005F0..0x0000066E  |   127 B    |   \n"'>-->*/</script>...</math>    |
|   0x0000066F..0x0000068D  |   31 B     |   <!--1337BOY-POLYGLOT-START-->\n  |
+---------------------------+------------+------------------------------------+
| 0x0000068E (1,678)        | 227,081 B  | [3] PURE 7-BIT ASCII HTML DOCUMENT |
|   0x0000068E..0x00004224  |   15,255 B |   <!DOCTYPE html>..<style>..</head>|
|   0x00004225..0x00004AC5  |   2,209 B  |   <script id="b1337-rom-b64">      |
|                           |            |     (2,028 B Base64 of 0x0..0x5EF) |
|   0x00004AC6..0x00037D96  |   209,617 B|   <script id="b1337-core">         |
|                           |            |     (1337Boy Emulator + Self-Test) |
+-----------------------------------------------------------------------------+
| EOF: 0x00037D97 (228,759 bytes)        | Full Polyglot CRC32 = 0xF089868A   |
+-----------------------------------------------------------------------------+
```

### Why the Base64 Copy Exists (and Why There Is No Recursion)
1. **Hardware / Emulator View**: GBA hardware and mGBA map the cartridge into Waitstate 0 (`0x08000000`). The program code inside `1337boot` knows its own length (`0x080005F0` stored in its literal pool at `lit_rom_end`) and ignores any trailing flash-cart bytes after `0x080005EF`.
2. **Browser View**: A page opened over `file://` cannot `fetch()` its own file due to browser same-origin policies, and reading `document.body.textContent` before DOM cleanup is lossy because the HTML5 parser replaces `0x00` (`NUL`) with `U+FFFD`, normalizes `\r\n` (`0x0D 0x0A`) to `\n` (`0x0A`), and consumes byte sequences that look like HTML tags. Embedding a Base64 copy of the unmodified ROM bytes (`0x00000000..0x000005EF`) inside `<script id="b1337-rom-b64" type="text/plain">` gives the JavaScript emulator an exact, lossless byte array at startup.
3. **One Source of Truth & Idempotence**: When re-exporting via **1337IFY!** or `tools/1337ify.py`, the builder strips everything from `B1337_RESET_SEQ` onward and reconstructs the HTML tail from the pristine `#b1337-style` and `#b1337-core` elements.

### Content-Security-Policy (`<meta>`) Behavior in Standalone vs. Polyglot Mode
We tested the `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; ... connect-src 'none';">` tag in headless Chromium 156 across both modes:
- **Standalone (`1337boy.html`)**: The static `<meta>` tag sits inside `<head>` at byte offset `55`, so the browser parser registers the CSP immediately during head parsing (`staticMetaInHead = 1`, `fetch()` blocked immediately).
- **Polyglot (`1337boot.1337.html`)**: Because the binary ROM prefix (`1,520` bytes) contains printable bytes before `<!DOCTYPE html>`, the HTML5 tree builder implicitly opens `<html><head></head><body>` at byte `0` to hold the binary text nodes. When the parser later encounters `<head>` and `<meta http-equiv="Content-Security-Policy">` after the reset sequence, the tree builder is already in the **"in body"** insertion mode, so the static `<meta>` element lands in `document.body` (`staticMetaInBody = 1`, `staticMetaInHead = 0`), where HTML5 ignores `http-equiv="Content-Security-Policy"`.
- **Our Fix (`enforceZeroNetworkCSP()`)**: On startup, `1337Boy` inspects `document.head` and dynamically appends `<meta http-equiv="Content-Security-Policy" ...>` directly into `document.head`. Verified in headless Chromium: after `enforceZeroNetworkCSP()` runs, `fetch()` and external `Image` loads are strictly blocked by Chromium's CSP engine in both standalone and polyglot files.

## 2. ARM7TDMI CPU Architecture

The CPU core (`GBA.prototype.stepArm` and `GBA.prototype.stepThumb`) is written in pure integer/typed-array JavaScript (`Int32Array`, `Uint32Array`, `BigInt` for 64-bit multiplies) with zero floating-point operations and zero object allocations in the execution loop:
- **Registers & Banked Modes**: 16 general-purpose 32-bit registers (`this.r[0..15]`), `CPSR`, and dedicated register banks for `User/System` (`0x10`/`0x1F`), `FIQ` (`0x11`, banking `R8..R14`), `IRQ` (`0x12`, banking `R13..R14`), `Supervisor` (`0x13`), `Abort` (`0x17`), and `Undefined` (`0x1B`), plus per-mode `SPSR`.
- **Pipeline-Accurate PC Reads**:
  - In **ARM state**, `this.r[15]` is advanced by `+4` upon fetch; `this.getReg(15, 4)` returns `PC + 8` for standard instructions and `PC + 12` (`getReg(15, 8)`) when `I=0` and a register-specified shift (`bit 4 = 1`) or `STR/STM R15` is executed.
  - In **Thumb state**, `this.r[15]` is advanced by `+2` upon fetch; reading `PC` returns `PC + 4`.
- **Barrel Shifter & Carry-Out**: Implements `LSL`, `LSR`, `ASR`, `ROR`, and `RRX` for both 5-bit immediate shifts (including `LSR #0 -> LSR #32`, `ASR #0 -> ASR #32`, `ROR #0 -> RRX #1`) and register-specified shifts (`Rs & 0xFF`, handling shift amounts `0`, `1..31`, `32`, and `>32`).
- **ARM7TDMI `LDM`/`STM` Hardware Edge Cases**:
  - **Empty Register List (`rlist == 0`)**: Transfers `R15` and increments/decrements the base register `Rn` by `0x40` (`64` bytes).
  - **Base Register in `STM` List with Writeback (`W=1`)**: If `Rn` is the lowest-numbered register in `rlist`, stores the **original** unindexed base; if `Rn` is not first in `rlist`, stores the **new** written-back base.
  - **User-Bank Transfer (`S=1`)**: Transfers registers to/from the User mode bank (`R8_usr..R14_usr`) even while executing in `IRQ` or `SVC` mode; if `LDM` includes `R15` with `S=1`, copies `SPSR` to `CPSR` and switches mode.

## 3. Memory Map & Custom 1337Boy BIOS

| Region | Address Range | Size & Bus Width | Mirroring & Hardware Notes |
| :--- | :--- | :--- | :--- |
| **BIOS** | `0x00000000..0x00003FFF` | 16 KB (32-bit) | Readable only when `PC < 0x4000`; returns `biosLastFetch` latch (`0xE129F000` post-IRQ/IntrWait) otherwise. |
| **EWRAM** | `0x02000000..0x0203FFFF` | 256 KB (16-bit) | Mirrored every `0x40000` across `0x02000000..0x02FFFFFF`. |
| **IWRAM** | `0x03000000..0x03007FFF` | 32 KB (32-bit) | Mirrored every `0x8000` across `0x03000000..0x03FFFFFF` (so `0x03FFFFFC` mirrors `0x03007FFC`). |
| **I/O** | `0x04000000..0x040003FE` | 1 KB (16/32-bit) | PPU, Sound, DMA0-3, Timers 0-3, SIO, Keypad, IE/IF/IME, HALTCNT. |
| **Palette** | `0x05000000..0x050003FF` | 1 KB (16-bit) | 256 BG + 256 OBJ BGR555 entries. 8-bit writes duplicate byte to halfword. |
| **VRAM** | `0x06000000..0x06017FFF` | 96 KB (16-bit) | 64 KB + 32 KB mirrored in 128 KB window (`0x06018000..0x0601FFFF` mirrors `0x06010000..0x06017FFF`). |
| **OAM** | `0x07000000..0x070003FF` | 1 KB (32-bit) | 128 OBJs + 32 affine matrices. 8-bit writes are ignored by hardware. |
| **ROM** | `0x08000000..0x0DFFFFFF` | Up to 32 MB | Mirrored across Waitstates 0/1/2 (`0x08`, `0x0A`, `0x0C`). Out-of-bounds reads return `(addr/2) & 0xFFFF`. |
| **SRAM** | `0x0E000000..0x0FFFFF` | 32 KB (8-bit bus) | True 8-bit bus: 16-bit and 32-bit reads repeat the byte (`b * 0x0101` / `b * 0x01010101`). |

### Custom 1337Boy BIOS & Hardware IRQ Stub (`0x00000018`)
At reset, 1337Boy initializes post-BIOS registers (`SP_usr = 0x03007F00`, `SP_irq = 0x03007FA0`, `SP_svc = 0x03007FE0`, `PC = 0x08000000`, `CPSR = 0x1F`) and places real ARM machine code at `0x00000018` and `0x00000128`:
1. `0x0018: EA000042` (`B 0x0128`)
2. `0x0128: E92D500F` (`STMDB SP!, {R0-R3, R12, LR}`)
3. `0x012C: E3A00301` (`MOV R0, #0x04000000`)
4. `0x0130: E28FE000` (`ADR LR, 0x0138`)
5. `0x0134: E510F004` (`LDR PC, [R0, #-4]` — jumps to the user's IRQ vector at `[0x03FFFFFC] == [0x03007FFC]`)
6. `0x0138: E8BD500F` (`LDMIA SP!, {R0-R3, R12, LR}`)
7. `0x013C: E25EF004` (`SUBS PC, LR, #4` — restores `CPSR` from `SPSR_irq` and resumes interrupted ARM or Thumb code).

## 4. PPU Scanline Renderer & Frame Scheduler

Each frame consists of **228 scanlines** (`280,896` CPU cycles at `16.78 MHz`):
- **Lines `0..159` (Visible)**: `960` cycles HDraw -> `renderScanline(y)` -> `272` cycles HBlank (triggers HBlank IRQ & HBlank DMA). At the end of each visible line, internal affine reference registers `bgRefX[0..1]` and `bgRefY[0..1]` advance by `PB` and `PD`.
- **Lines `160..227` (VBlank)**: Line `160` sets `DISPSTAT.VBlank`, latches internal affine reference points from `BG2X/Y` and `BG3X/Y`, triggers VBlank IRQ and VBlank DMA, and updates `[0x03007FF8]` for `VBlankIntrWait`.
- **Affine Bitmap Modes (Modes 3, 4, 5)**: `renderBitmapBgScanline` applies the full `2x2` affine matrix (`PA, PB, PC, PD`) and internal reference coordinates (`bgRefX[0], bgRefY[0]`) on every pixel, supporting games that render a `120x80` buffer and stretch it `2x` to `240x160` via `BG2PA = 0x0080, BG2PD = 0x0080`.
- **Bitmap-Mode Sprite Restriction**: In Modes 3, 4, and 5, `renderSpritesScanline` enforces the hardware rule that OBJ tiles `< 512` (`0x06010000..0x06013FFF`) are overlapped by the bitmap background and cannot be rendered by sprites.
