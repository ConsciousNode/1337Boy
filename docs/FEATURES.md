# 1337Boy™ v1.1 Feature Truth Table & Honest Engineering Status (`FEATURES.md`)

`Copyright (c) 2026 Khamerron Kizer / ConsciousNode SoftWorks` — Licensed under the **MIT License**.

## 1. Feature Truth Table (v1.1)

| Feature / Subsystem | Where Implemented | Status | Verification & Notes |
| :--- | :--- | :--- | :--- |
| **ARM7TDMI — ARM Instruction Set (All 16 ALU ops, Barrel Shifter, Flags)** | `1337boy.html` (`stepArm`, `execDataProc`, `shiftImm`, `shiftReg`) | **Working** | Executed & verified against **210 built-in ARM test vectors** in Node.js and headless Chromium, plus `jsmolka/gba-tests` `arm.gba` (verified by Kehai Interim). |
| **ARM7TDMI — Thumb Instruction Set + Empty `rlist` `STMIA`/`PUSH` (`thumb` test 229)** | `1337boy.html` (`stepThumb`) | **Working** | Fixed Format 15 `STMIA Rb!, {}` (`0xC000`) and Format 14 `PUSH {}` (`0xB400`) to store `pc + 6` (`instr_addr + 6`) and adjust base by `0x40`. Verified in built-in self-test. |
| **ARM7TDMI — 2-Stage Prefetch Pipeline (`nes` test 1)** | `1337boy.html` (`pipe0`, `pipe1`, `pipePc`, `fetchArmOpcode`, `fetchThumbOpcode`) | **Working** | Executes from prefetched queue when self-modifying code overwrites `pc + 4` (ARM) or `pc + 2` (Thumb); flushes on all writes to `R15`. Executed & verified in ARM and Thumb self-tests. |
| **BIOS Open-Bus Latch States (`bios` test 1–3) & `GetBiosChecksum` (`SWI 0x0D`)** | `1337boy.html` (`initBios`, `readBios32`, `handleSwi`, `execDataProc`) | **Working** | Verified all 4 hardware states: `0xE129F000` (post-boot/SoftReset/IntrWait), `0xE25EF004` (during IRQ), `0xE55EC002` (after IRQ return via `0x0144` prefetch), `0xE3A02004` (after SWI), plus `SWI 0x0D` (`0xBAAE187F`). |
| **Save Memory — SRAM 32 KB & `NONE` (`save/sram.gba`, `save/none.gba`)** | `1337boy.html` (`readSave8`, `writeSave8`) | **Working** | Initialized to `0xFF` (erased state) and mirrored across `0x0E000000–0x0FFFFFFF`. Executed & verified in self-test. |
| **Save Memory — Flash 64 KB (`0x1CC2`) & 128 KB (`0x1362`) (`save/flash64.gba`, `save/flash128.gba`)** | `1337boy.html` (`readSave8`, `writeSave8`) | **Working** | Full `0xAA`/`0x55` command state machine: Chip ID (`0x90`, Macronix `0x1CC2` for 64KB, Sanyo `0x1362` for 128KB), Reset (`0xF0`), Sector Erase (`0x80`->`0x30`), Chip Erase (`0x80`->`0x10`), Byte Program (`0xA0`), and 128KB Bank Switch (`0xB0`). Verified in self-test. |
| **Save Memory — EEPROM 512 B & 8 KB (DMA3 Serial Protocol at `0x0D000000`)** | `1337boy.html` (`handleEepromDmaWrite`, `handleEepromDmaRead`, `read16`) | **Working** | Infers 6-bit (`9`/`73` halfwords) vs. 14-bit (`17`/`81` halfwords) addressing from DMA3 count; returns ready bit `1` on `0x0D000000` reads. Executed & verified in 64-bit write/read round-trip self-test. |
| **Save Type Auto-Detection + Heuristic Fallback + UI Override** | `1337boy.html` (`detectSaveType`, `setSaveType`, `#sel-savetype`) | **Working** | Scans ROM for `SRAM_V`, `SRAM_F_V`, `FLASH_V`, `FLASH512_V`, `FLASH1M_V`, `EEPROM_V`; upgrades heuristically when no string is present; manual UI selector & `B1337.setSaveType()`. |
| **Deterministic Headless Stepping Hook (`window.B1337.setRealtime`)** | `1337boy.html` (`window.B1337.setRealtime`) | **Working** | Pauses/resumes `requestAnimationFrame` stepping so `B1337.runFrames(n)` runs an exact deterministic frame count. Executed & verified in headless Chromium. |
| **Hardware Cycle Timing (`WAITCNT` `0x04000204`, Prefetch Buffer, DMA Stalls)** | `1337boy.html` (`updateWaitstates`, `finishCycles`, `executeDma`) | **Working** | Models ROM WS0/1/2 N & S waitstates (16/32-bit), SRAM waitstates, EWRAM (3/6 cycles), VRAM/Pal/OAM bus widths, Game Pak prefetch buffer (bit 14), Booth multiplier internal cycles, and DMA bus stalls. Verified in self-test. |
| **Sound — PSG Channel 3 Wave RAM, Envelopes/Sweep, `SOUNDBIAS`, `AudioWorklet`** | `1337boy.html` (`stepPsgFrameSequencer`, `sampleAudioScanline`, `B1337AudioDriver`) | **Working** | Dual-bank 32/64-sample Wave RAM (`0x90..0x9F`), 512 Hz frame sequencer (length, Ch1 sweep, volume envelopes), `SOUNDCNT_X` active bits, `SOUNDBIAS` resolution, and inline `Blob` `AudioWorklet` with `ScriptProcessorNode` fallback. |
| **Tier 3 Toolkit (Gamepad API, Remap UI, 4 Save Slots + Thumbnails, Rewind, Speed `0.25x..8x`, Frame Step, PNG Snap, Integer Scale, LCD Grid, GBA Color Correction, Fullscreen, IndexedDB Library, Cheats)** | `1337boy.html` (`initB1337App`, `BGR555_CC_LUT`, `B1337LibraryDB`) | **Working** | All 9 toolkit features implemented in-page with zero external dependencies; phone layout rules from 1.0.1 preserved and verified at `360px`, `412px`, and `600px` viewports. |

## 2. Honest Status Report (v1.1)

### Executed vs. Unexecuted Tests
- **Executed in Headless Chromium 156 & Node.js V8**:
  - **391 / 391 built-in self-test vectors** (`window.B1337.selftest()`), including dedicated unit tests reproducing the exact instruction/bus sequences of `thumb.gba` test 229 (`STMIA R0!, {}` storing `PC + 6`), `nes.gba` test 1 (ARM and Thumb self-modifying code at `PC + 4` / `PC + 2`), `bios.gba` tests 1–3 (`0xE129F000`, `0xE3A02004`, `0xE25EF004` during IRQ, `0xE55EC002` after IRQ return), `save/{sram,none,flash64,flash128}` + `EEPROM` DMA3, `WAITCNT` timing tables, and Wave RAM bank isolation.
  - **CLI vs. Browser Byte-Identity & Idempotence**: Verified in headless Chromium that `tools/1337ify.py --build-boot` and `window.B1337.buildPolyglot()` produce byte-for-byte identical `302,635`-byte files (`CRC32 = 0xD58473CB`), and re-1337ifying is idempotent.
  - **Phone Viewport Layout Verification**: Tested in headless Chromium at `360x740`, `412x740`, and `600x740` viewports (`scrollWidth == clientWidth`, zero horizontal overflow, 3:2 canvas ratio preserved).
- **Not Executed in This Offline Sandbox**:
  - External `jsmolka/gba-tests` ROM binaries (`thumb.gba`, `nes.gba`, `bios.gba`, `save/*.gba`), the studio's two external homebrew ROMs (*Wrongfully Accused*, *GBA-Craft*), and native `mGBA` (not present in the sandbox VM).
  - Note on `bios.gba`: Tests 1–3 (open-bus states) and all HLE math/decompression SWI tests are modeled, whereas any `bios.gba` sub-test that branches directly into undocumented mid-function addresses inside Nintendo's proprietary 16 KB BIOS binary requires a real GBA BIOS dump.

### Measured FPS Before (1.0.1) vs. After (1.1)
1. **Full-Frame Emulation (`1337boot.gba`, 300 frames in Headless Chromium 156)**:
   - **1.0.1 Baseline**: `651.30 ms` -> **`460.6 FPS`** (`2.171 ms/frame`)
   - **1.1 (with 2-stage pipeline, `WAITCNT` waitstates, and BGR555 LUT)**: `411.90 ms` -> **`728.3 FPS`** (`1.373 ms/frame`, **12.1x real-time 60 fps headroom**)
2. **Full-Frame Emulation (`1337boot.gba`, 600 frames in Node.js V8)**:
   - **1.0.1 Baseline**: `2248.38 ms` -> **`266.9 FPS`** (`3.747 ms/frame`)
   - **1.1**: `1178.92 ms` -> **`508.9 FPS`** (`1.965 ms/frame`)
   *(Why ROM frame rate increased: in 1.0.1 every ROM instruction took 1 cycle so the CPU executed ~5x too many ROM instructions per scanline; modeling real `WAITCNT` ROM waitstates + a precomputed 32K BGR555-to-RGBA lookup table cut per-frame work nearly in half.)*
3. **Pure 1-Cycle IWRAM Tight Loop (300 frames, 280,896 single-cycle instructions/frame in Node.js V8 — isolating raw CPU dispatch overhead)**:
   - **1.0.1 Baseline**: `865.84 ms` -> **`346.5 FPS`** (`2.886 ms/frame`)
   - **1.1 (with 2-stage pipeline + waitstate/prefetch accounting)**: `1413.21 ms` -> **`212.3 FPS`** (`4.711 ms/frame`, **3.5x real-time 60 fps headroom** even in the worst-case 100% 1-cycle IWRAM loop).

### Three Most Likely Regressions to Check First
1. **Waitstate Cycle Counting on *GBA-Craft* (3D Voxel Frame Pacing)**:
   - *Why*: In 1.0.1, ROM and EWRAM accesses cost 1 cycle, whereas in 1.1 ROM accesses cost `WAITCNT` N/S cycles (`4–8` cycles) and 32-bit EWRAM accesses cost `6` cycles. If *GBA-Craft* runs its software 3D renderer from ROM/EWRAM without setting `WAITCNT = 0x4317`, its frame rate could change relative to 1.0.1 (though it should now be closer to hardware/mGBA).
2. **Pipeline Flush Coverage on Unusual `R15` Writes**:
   - *Why*: The 2-stage prefetch pipeline (`pipe0`, `pipe1`, `pipePc`) relies on flushing `this.pipePc = -1` whenever an instruction writes to `R15` (including a branch to `pc + 4`, the very next instruction). We flush on all `B`/`BL`/`BX`, `LDR/LDH/LDRSB/LDRSH PC`, `LDM {PC}`, `POP {PC}`, `ALU/Hi-Reg Rd=15`, `MSR` T-bit changes, `SWI`, and `IRQ`, but any missed edge case would execute one stale prefetched opcode.
3. **Heuristic Save Type Auto-Detection (`AUTO`) on Homebrew Without SDK Strings**:
   - *Why*: When a ROM lacks a standard ID string (`SRAM_V`, `FLASH_V`, `EEPROM_V`), 1.1 starts in `AUTO` mode (reading `0xFF` across `0x0E000000–0x0FFFFFFF`), upgrading to `FLASH128` only if the exact 3-step unlock sequence (`0xAA @ 0x5555 -> 0x55 @ 0x2AAA -> CMD @ 0x5555`) is written, to `EEPROM` on DMA3 to `0x0D000000`, and to `SRAM` on any other write to `0x0E000000`. If a Flash homebrew game writes a stray byte to `0x0E000000` before its first Flash unlock command, it would lock into `SRAM` unless overridden via the UI dropdown or `B1337.setSaveType('FLASH128')`.
