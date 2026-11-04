# 1337Boy™ v1.1 System Architecture & Polyglot File Layout

`Copyright (c) 2026 Khamerron Kizer / ConsciousNode SoftWorks` — Licensed under the **MIT License**.

## 1. Polyglot File Layout & Byte Offsets (`1337boot.1337.gba`)

A 1337Boy cartridge is a linear concatenation of three regions with zero recursion. Below is the exact byte-offset diagram for the pre-built v1.1 **`1337boot.1337.gba`** (`302,635` bytes total):

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
| 0x0000068E (1,678)        | 300,957 B  | [3] PURE 7-BIT ASCII HTML DOCUMENT |
|   0x0000068E..0x00004AD1  |   17,476 B |   <!DOCTYPE html>..<style>..</head>|
|   0x00004AD2..0x00005372  |   2,209 B  |   <script id="b1337-rom-b64">      |
|                           |            |     (2,028 B Base64 of 0x0..0x5EF) |
|   0x00005373..0x00049E2A  |   281,272 B|   <script id="b1337-core">         |
|                           |            |     (1337Boy v1.1 Core + 391 Tests)|
+-----------------------------------------------------------------------------+
| EOF: 0x00049E2B (302,635 bytes)        | Full Polyglot CRC32 = 0xD58473CB   |
+-----------------------------------------------------------------------------+
```

### Why the Base64 Copy Exists (and Why There Is No Recursion)
1. **Hardware / Emulator View**: GBA hardware and mGBA map the cartridge into Waitstate 0 (`0x08000000`). The program code inside `1337boot` knows its own length (`0x080005F0` stored in its literal pool at `lit_rom_end`) and ignores any trailing flash-cart bytes after `0x080005EF`.
2. **Browser View**: A page opened over `file://` cannot `fetch()` its own file due to browser same-origin policies, and reading `document.body.textContent` before DOM cleanup is lossy because the HTML5 parser replaces `0x00` (`NUL`) with `U+FFFD`, normalizes `\r\n` (`0x0D 0x0A`) to `\n` (`0x0A`), and consumes byte sequences that look like HTML tags. Embedding a Base64 copy of the unmodified ROM bytes (`0x00000000..0x000005EF`) inside `<script id="b1337-rom-b64" type="text/plain">` gives the JavaScript emulator an exact, lossless byte array at startup.
3. **One Source of Truth & Idempotence**: When re-exporting via **1337IFY!** or `tools/1337ify.py`, the builder strips everything from `B1337_RESET_SEQ` onward and reconstructs the HTML tail from the pristine `#b1337-style` and `#b1337-core` elements.

## 2. ARM7TDMI CPU & 2-Stage Prefetch Pipeline Architecture

The CPU core (`GBA.prototype.stepArm` and `GBA.prototype.stepThumb`) is written in pure integer/typed-array JavaScript (`Int32Array`, `Uint32Array`, `BigInt` for 64-bit multiplies) with zero floating-point operations and zero object allocations in the execution loop:
- **2-Stage Prefetch Pipeline (`pipe0`, `pipe1`, `pipePc`)**:
  - Models the ARM7TDMI Fetch/Decode/Execute pipeline queue: when instruction at `pc` enters Execute, `pipe0` already holds `pc + step` (`+4` in ARM, `+2` in Thumb) and the Fetch stage reads `pc + 2*step` into `pipe1` **before** the executing instruction performs any memory writes.
  - Self-modifying code that overwrites `pc + 4` (ARM) or `pc + 2` (Thumb) executes the already-prefetched old opcode (`nes.gba` test 1).
  - Any write to `R15` (`B`, `BL`, `BX`, `LDR PC`, `LDM {PC}`, `POP {PC}`, `ALU Rd=15`, `SWI`, `IRQ`) sets `this.pipePc = -1` to flush and refill the pipeline on the next instruction.
- **ARM & Thumb `LDM`/`STM`/`PUSH`/`POP` Hardware Edge Cases**:
  - **Empty Register List (`rlist == 0`)**: In ARM `STM`/`LDM`, transfers `R15` (`PC + 12` on store) and adjusts `Rn` by `+/- 0x40`. In Thumb `STMIA Rb!, {}` (`0xC000`) and `PUSH {}` (`0xB400`), stores `pc + 6` (`instr_addr + 6`, matching the pipeline `PC` read by the next instruction) and adjusts `Rb`/`SP` by `0x40` (`thumb.gba` test 229).
  - **Base Register in `STM` List with Writeback (`W=1`)**: If `Rn` is the lowest-numbered register in `rlist`, stores the **original** unindexed base; if `Rn` is not first in `rlist`, stores the **new** written-back base.
- **Waitstate & Prefetch Buffer Timing (`WAITCNT` `0x04000204`)**:
  - Precomputes 16-entry region lookup tables (`ws16N`, `ws16S`, `ws32N`, `ws32S`) whenever `WAITCNT` is written: IWRAM/BIOS/OAM (`1` cycle 32-bit), Palette/VRAM (`1` cycle 16-bit, `2` cycles 32-bit), EWRAM (`3` cycles 8/16-bit, `6` cycles 32-bit), SRAM (`5, 4, 3, 9` cycles), and ROM WS0/WS1/WS2 N/S waitstates.
  - Models the Game Pak Prefetch Buffer (`WAITCNT` bit 14), accumulating prefetched halfwords during non-ROM bus cycles and reducing sequential ROM instruction fetches to `1` cycle per halfword.
  - Models DMA bus stalls (`dmaCyclesStall`), advancing timers and scanline cycles for the duration of every DMA transfer.

## 3. Memory Map, Save Memory Subsystem & Custom 1337Boy BIOS

| Region | Address Range | Size & Bus Width | Mirroring & Hardware Notes |
| :--- | :--- | :--- | :--- |
| **BIOS** | `0x00000000..0x00003FFF` | 16 KB (32-bit) | Readable only when `PC < 0x4000`; returns `biosLastFetch` (`0xE129F000` boot/IntrWait, `0xE25EF004` during IRQ, `0xE55EC002` post-IRQ, `0xE3A02004` post-SWI) otherwise. |
| **EWRAM** | `0x02000000..0x0203FFFF` | 256 KB (16-bit) | Mirrored every `0x40000` across `0x02000000..0x02FFFFFF` (`3` cycles 8/16-bit, `6` cycles 32-bit). |
| **IWRAM** | `0x03000000..0x03007FFF` | 32 KB (32-bit) | Mirrored every `0x8000` across `0x03000000..0x03FFFFFF` (`0x03FFFFFC` mirrors `0x03007FFC`, `1` cycle). |
| **I/O** | `0x04000000..0x040003FE` | 1 KB (16/32-bit) | PPU, Sound + Wave RAM, DMA0-3, Timers 0-3, SIO, Keypad, IE/IF/WAITCNT/IME, HALTCNT. |
| **Palette** | `0x05000000..0x050003FF` | 1 KB (16-bit) | 256 BG + 256 OBJ BGR555 entries. 8-bit writes duplicate byte to halfword. |
| **VRAM** | `0x06000000..0x06017FFF` | 96 KB (16-bit) | 64 KB + 32 KB mirrored in 128 KB window (`0x06018000..0x0601FFFF` mirrors `0x06010000..0x06017FFF`). |
| **OAM** | `0x07000000..0x070003FF` | 1 KB (32-bit) | 128 OBJs + 32 affine matrices. 8-bit writes are ignored by hardware. |
| **ROM** | `0x08000000..0x0DFFFFFF` | Up to 32 MB | Mirrored across Waitstates 0/1/2 (`0x08`, `0x0A`, `0x0C`). Out-of-bounds reads return `(addr/2) & 0xFFFF`. |
| **EEPROM** | `0x0D000000..0x0DFFFFFF` | 512 B / 8 KB | Serial bitstream over DMA3 (6-bit or 14-bit block address inferred from DMA length); CPU reads return ready bit `1`. |
| **SRAM / Flash** | `0x0E000000..0x0FFFFFFF` | 32 KB / 64 KB / 128 KB | Erased state `0xFF`; 8-bit bus repeats byte across 16/32-bit reads; supports SRAM 32 KB mirrors and Flash 64 KB (`0x1CC2`) / 128 KB (`0x1362`) command protocol. |

### Custom 1337Boy BIOS & Hardware IRQ Stub (`0x00000018`)
At reset, 1337Boy initializes post-BIOS registers (`SP_usr = 0x03007F00`, `SP_irq = 0x03007FA0`, `SP_svc = 0x03007FE0`, `PC = 0x08000000`, `CPSR = 0x1F`) and places real ARM machine code at `0x00000018` and `0x00000128`:
1. `0x0018: EA000042` (`B 0x0128`)
2. `0x0128: E92D500F` (`STMDB SP!, {R0-R3, R12, LR}`)
3. `0x012C: E3A00301` (`MOV R0, #0x04000000`)
4. `0x0130: E28FE000` (`ADR LR, 0x0138`)
5. `0x0134: E510F004` (`LDR PC, [R0, #-4]` — jumps to `[0x03FFFFFC] == [0x03007FFC]`; pipeline prefetches `0x0134 + 8 = 0x013C` = `0xE25EF004` during IRQ)
6. `0x0138: E8BD500F` (`LDMIA SP!, {R0-R3, R12, LR}`)
7. `0x013C: E25EF004` (`SUBS PC, LR, #4` — returns from IRQ; pipeline prefetches `0x013C + 8 = 0x0144` = `0xE55EC002` after IRQ return)
8. `0x0140: E55EC002` / `0x0144: E55EC002` (`LDRB R12, [LR, #-2]` — post-IRQ BIOS opcode signature).
