#!/usr/bin/env python3
"""
1337ify.py - The 1337Boy(TM) Polyglot Cartridge Builder & Hand-Assembler
Copyright (c) 2026 Khamerron Kizer / ConsciousNode SoftWorks
License: MIT
House Philosophy: Xinu (Single File, Zero Dependencies, Offline-First)

Usage:
  python3 tools/1337ify.py game.gba -o game.1337.gba
  python3 tools/1337ify.py --build-boot -o 1337boot.1337.gba
"""

import argparse
import base64
import os
import re
import struct
import sys
import zlib

# Exact HTML5 Tokenizer Reset Sequence + Marker Comment (must match 1337boy.html byte-for-byte)
B1337_RESET_SEQ = b'\n"\'>-->*/</script></style></title></textarea></xmp></iframe></noscript></noembed></noframes>]]></svg></math><!--1337BOY-POLYGLOT-START-->\n'

# Official 156-byte GBA Header Logo Bitmap (0x04..0x9F) required by GBA hardware boot ROM
# Included for hardware interoperability per Sega Enterprises Ltd. v. Accolade, Inc., 977 F.2d 1510 (9th Cir. 1992).
NINTENDO_LOGO = bytes([
    0x24,0xFF,0xAE,0x51,0x69,0x9A,0xA2,0x21,0x3D,0x84,0x82,0x0A,0x84,0xE4,0x09,0xAD,
    0x11,0x24,0x8B,0x98,0xC0,0x81,0x7F,0x21,0xA3,0x52,0xBE,0x19,0x93,0x09,0xCE,0x20,
    0x10,0x46,0x4A,0x4A,0xF8,0x27,0x31,0xEC,0x58,0xC7,0xE8,0x33,0x82,0xE3,0xCE,0xBF,
    0x85,0xF4,0xDF,0x94,0xCE,0x4B,0x09,0xC1,0x94,0x56,0x8A,0xC0,0x13,0x72,0xA7,0xFC,
    0x9F,0x84,0x4D,0x73,0xA3,0xCA,0x9A,0x61,0x58,0x97,0xA3,0x27,0xFC,0x03,0x98,0x76,
    0x23,0x1D,0xC7,0x61,0x03,0x04,0xAE,0x56,0xBF,0x38,0x84,0x00,0x40,0xA7,0x0E,0xFD,
    0xFF,0x52,0xFE,0x03,0x6F,0x95,0x30,0xF1,0x97,0xFB,0xC0,0x85,0x60,0xD6,0x80,0x25,
    0xA9,0x63,0xBE,0x03,0x01,0x4E,0x38,0xE2,0xF9,0xA2,0x34,0xFF,0xBB,0x3E,0x03,0x44,
    0x78,0x00,0x90,0xCB,0x88,0x11,0x3A,0x94,0x65,0xC0,0x7C,0x63,0x87,0xF0,0x3C,0xAF,
    0xD6,0x25,0xE4,0x8B,0x38,0x0A,0xAC,0x72,0x21,0xD4,0xF8,0x07
])

FONT_8X8 = {
    ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
    '0': [0x3C,0x66,0x6E,0x76,0x66,0x66,0x3C,0x00],
    '1': [0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00],
    '2': [0x3C,0x66,0x06,0x1C,0x30,0x66,0x7E,0x00],
    '3': [0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00],
    '4': [0x0C,0x1C,0x3C,0x6C,0x7E,0x0C,0x0C,0x00],
    '5': [0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00],
    '6': [0x3C,0x60,0x7C,0x66,0x66,0x66,0x3C,0x00],
    '7': [0x7E,0x66,0x06,0x0C,0x18,0x18,0x18,0x00],
    '8': [0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00],
    '9': [0x3C,0x66,0x66,0x3E,0x06,0x0C,0x38,0x00],
    'A': [0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00],
    'B': [0x7C,0x66,0x66,0x7C,0x66,0x66,0x7C,0x00],
    'C': [0x3C,0x66,0x60,0x60,0x60,0x66,0x3C,0x00],
    'D': [0x78,0x6C,0x66,0x66,0x66,0x6C,0x78,0x00],
    'E': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x7E,0x00],
    'F': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x60,0x00],
    'G': [0x3C,0x66,0x60,0x6E,0x66,0x66,0x3E,0x00],
    'H': [0x66,0x66,0x66,0x7E,0x66,0x66,0x66,0x00],
    'I': [0x3C,0x18,0x18,0x18,0x18,0x18,0x3C,0x00],
    'J': [0x1E,0x0C,0x0C,0x0C,0x6C,0x6C,0x38,0x00],
    'K': [0x66,0x6C,0x78,0x70,0x78,0x6C,0x66,0x00],
    'L': [0x60,0x60,0x60,0x60,0x60,0x60,0x7E,0x00],
    'M': [0x63,0x77,0x7F,0x6B,0x63,0x63,0x63,0x00],
    'N': [0x66,0x76,0x7E,0x7E,0x6E,0x66,0x66,0x00],
    'O': [0x3C,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
    'P': [0x7C,0x66,0x66,0x7C,0x60,0x60,0x60,0x00],
    'Q': [0x3C,0x66,0x66,0x66,0x6A,0x6C,0x36,0x00],
    'R': [0x7C,0x66,0x66,0x7C,0x6C,0x66,0x66,0x00],
    'S': [0x3C,0x66,0x60,0x3C,0x06,0x66,0x3C,0x00],
    'T': [0x7E,0x18,0x18,0x18,0x18,0x18,0x18,0x00],
    'U': [0x66,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
    'V': [0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00],
    'W': [0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00],
    'X': [0x66,0x66,0x3C,0x18,0x3C,0x66,0x66,0x00],
    'Y': [0x66,0x66,0x66,0x3C,0x18,0x18,0x18,0x00],
    'Z': [0x7E,0x06,0x0C,0x18,0x30,0x60,0x7E,0x00],
    ':': [0x00,0x18,0x18,0x00,0x18,0x18,0x00,0x00],
    '-': [0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00],
    '.': [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x00],
    '!': [0x18,0x18,0x18,0x18,0x18,0x00,0x18,0x00],
    '/': [0x06,0x0C,0x18,0x30,0x60,0x40,0x00,0x00],
    '(': [0x0C,0x18,0x30,0x30,0x30,0x18,0x0C,0x00],
    ')': [0x30,0x18,0x0C,0x0C,0x0C,0x18,0x30,0x00],
    '=': [0x00,0x00,0x7E,0x00,0x7E,0x00,0x00,0x00],
}

def rgb15(r, g, b):
    return (r & 0x1F) | ((g & 0x1F) << 5) | ((b & 0x1F) << 10)


class ArmBuilder:
    """Zero-dependency ARM7TDMI machine-code assembler for the 1337 BOOT ROM."""

    def __init__(self, base=0x08000000):
        self.base = base
        self.code = bytearray()
        self.labels = {}
        self.fixups = []

    def align(self, n=4):
        while len(self.code) % n != 0:
            self.code.append(0)

    def label(self, name):
        self.labels[name] = self.base + len(self.code)

    def emit32(self, w):
        self.code.extend(struct.pack("<I", w & 0xFFFFFFFF))

    def emit_bytes(self, b):
        self.code.extend(b)

    def _enc_imm(self, val):
        val &= 0xFFFFFFFF
        for rot in range(16):
            shift = rot * 2
            imm8 = ((val << shift) | (val >> (32 - shift))) & 0xFFFFFFFF if shift else val
            if imm8 <= 0xFF:
                return (rot << 8) | imm8
        raise ValueError(f"Cannot encode ARM immediate {hex(val)}")

    def dp_imm(self, op, s, rn, rd, val, cond=0xE):
        return (cond << 28) | (1 << 25) | (op << 21) | (s << 20) | (rn << 16) | (rd << 12) | self._enc_imm(val)

    def dp_reg(self, op, s, rn, rd, rm, shift_imm=0, shift_type=0, cond=0xE):
        return (cond << 28) | (0 << 25) | (op << 21) | (s << 20) | (rn << 16) | (rd << 12) | (shift_imm << 7) | (shift_type << 5) | rm

    def dp_reg_rs(self, op, s, rn, rd, rm, rs, shift_type=0, cond=0xE):
        return (cond << 28) | (0 << 25) | (op << 21) | (s << 20) | (rn << 16) | (rd << 12) | (rs << 8) | (shift_type << 5) | (1 << 4) | rm

    def mov_imm(self, rd, val, s=0, cond=0xE):
        self.emit32(self.dp_imm(0xD, s, 0, rd, val, cond))

    def mvn_imm(self, rd, val, s=0, cond=0xE):
        self.emit32(self.dp_imm(0xF, s, 0, rd, val, cond))

    def add_imm(self, rd, rn, val, s=0, cond=0xE):
        self.emit32(self.dp_imm(0x4, s, rn, rd, val, cond))

    def sub_imm(self, rd, rn, val, s=0, cond=0xE):
        self.emit32(self.dp_imm(0x2, s, rn, rd, val, cond))

    def and_imm(self, rd, rn, val, s=0, cond=0xE):
        self.emit32(self.dp_imm(0x0, s, rn, rd, val, cond))

    def orr_imm(self, rd, rn, val, s=0, cond=0xE):
        self.emit32(self.dp_imm(0xC, s, rn, rd, val, cond))

    def cmp_imm(self, rn, val, cond=0xE):
        self.emit32(self.dp_imm(0xA, 1, rn, 0, val, cond))

    def mov_reg(self, rd, rm, shift_imm=0, shift_type=0, s=0, cond=0xE):
        self.emit32(self.dp_reg(0xD, s, 0, rd, rm, shift_imm, shift_type, cond))

    def mov_reg_rs(self, rd, rm, rs, shift_type=0, s=0, cond=0xE):
        self.emit32(self.dp_reg_rs(0xD, s, 0, rd, rm, rs, shift_type, cond))

    def add_reg(self, rd, rn, rm, shift_imm=0, shift_type=0, s=0, cond=0xE):
        self.emit32(self.dp_reg(0x4, s, rn, rd, rm, shift_imm, shift_type, cond))

    def eor_reg(self, rd, rn, rm, shift_imm=0, shift_type=0, s=0, cond=0xE):
        self.emit32(self.dp_reg(0x1, s, rn, rd, rm, shift_imm, shift_type, cond))

    def cmp_reg(self, rn, rm, shift_imm=0, shift_type=0, cond=0xE):
        self.emit32(self.dp_reg(0xA, 1, rn, 0, rm, shift_imm, shift_type, cond))

    def mul(self, rd, rm, rs, cond=0xE):
        self.emit32((cond << 28) | (rd << 16) | (rs << 8) | 0x90 | rm)

    def ldr_imm(self, rd, rn, offset=0, b=0, p=1, w=0, cond=0xE):
        u = 1 if offset >= 0 else 0
        self.emit32((cond << 28) | (1 << 26) | (p << 24) | (u << 23) | (b << 22) | (w << 21) | (1 << 20) | (rn << 16) | (rd << 12) | (abs(offset) & 0xFFF))

    def str_imm(self, rd, rn, offset=0, b=0, p=1, w=0, cond=0xE):
        u = 1 if offset >= 0 else 0
        self.emit32((cond << 28) | (1 << 26) | (p << 24) | (u << 23) | (b << 22) | (w << 21) | (0 << 20) | (rn << 16) | (rd << 12) | (abs(offset) & 0xFFF))

    def strh_imm(self, rd, rn, offset=0, p=1, w=0, cond=0xE):
        u = 1 if offset >= 0 else 0
        off = abs(offset) & 0xFF
        self.emit32((cond << 28) | (p << 24) | (u << 23) | (1 << 22) | (w << 21) | (0 << 20) | (rn << 16) | (rd << 12) | ((off >> 4) << 8) | 0xB0 | (off & 0xF))

    def ldrh_imm(self, rd, rn, offset=0, p=1, w=0, cond=0xE):
        u = 1 if offset >= 0 else 0
        off = abs(offset) & 0xFF
        self.emit32((cond << 28) | (p << 24) | (u << 23) | (1 << 22) | (w << 21) | (1 << 20) | (rn << 16) | (rd << 12) | ((off >> 4) << 8) | 0xB0 | (off & 0xF))

    def push(self, reg_mask, cond=0xE):
        self.emit32((cond << 28) | (0b10010010 << 20) | (13 << 16) | (reg_mask & 0xFFFF))

    def pop(self, reg_mask, cond=0xE):
        self.emit32((cond << 28) | (0b10001011 << 20) | (13 << 16) | (reg_mask & 0xFFFF))

    def b(self, label, cond=0xE, link=0):
        off = len(self.code)
        self.fixups.append((off, 'B', label, (cond, link)))
        self.emit32(0)

    def bl(self, label, cond=0xE):
        self.b(label, cond=cond, link=1)

    def adr(self, rd, label, cond=0xE):
        off = len(self.code)
        self.fixups.append((off, 'ADR', label, (cond, rd)))
        self.emit32(0)

    def ldr_lit(self, rd, label, cond=0xE):
        off = len(self.code)
        self.fixups.append((off, 'LDR_LIT', label, (cond, rd)))
        self.emit32(0)

    def resolve(self):
        for off, kind, label, extra in self.fixups:
            target = self.labels[label]
            pc = self.base + off + 8
            diff = target - pc
            if kind == 'B':
                cond, link = extra
                imm24 = (diff >> 2) & 0xFFFFFF
                w = (cond << 28) | (0x5 << 25) | (link << 24) | imm24
                struct.pack_into("<I", self.code, off, w)
            elif kind == 'ADR':
                cond, rd = extra
                w = self.dp_imm(0x4, 0, 15, rd, diff, cond) if diff >= 0 else self.dp_imm(0x2, 0, 15, rd, -diff, cond)
                struct.pack_into("<I", self.code, off, w)
            elif kind == 'LDR_LIT':
                cond, rd = extra
                u = 1 if diff >= 0 else 0
                imm12 = abs(diff)
                w = (cond << 28) | (0b01011001 << 20) | (u << 23) | (15 << 16) | (rd << 12) | imm12
                struct.pack_into("<I", self.code, off, w)


def assemble_1337boot_rom():
    """
    Hand-assembles the '1337 BOOT' GBA ROM from scratch:
      - 0x00..0xBF: Valid GBA ROM header (entry branch, logo, '1337BOOT', 'B13E', 'CN', valid complement check 0x52)
      - 0xC0..0x5EF: ARM7TDMI machine code that:
          1. Configures Mode 3 (240x160 15-bit BGR555 bitmap on BG2)
          2. Renders the 1337Boy Color Advance logo & banner boxes
          3. Computes the IEEE 802.3 CRC32 over its own ROM image (0x08000000 .. 0x080005F0)
          4. Converts the 32-bit CRC32 into 8 hexadecimal ASCII glyphs and draws 'SELF CRC32: ADF3A552'
          5. Animates a VBlank-synchronized color bar at the bottom of the screen
    """
    a = ArmBuilder(0x08000000)
    a.b("start")                        # 0x00: B start (0x080000C0)
    a.emit_bytes(NINTENDO_LOGO)         # 0x04..0x9F: 156-byte logo
    a.emit_bytes(b"1337BOOT    ")       # 0xA0..0xAB: Game Title (12 bytes)
    a.emit_bytes(b"B13E")               # 0xAC..0xAF: Game Code (4 bytes)
    a.emit_bytes(b"CN")                 # 0xB0..0xB1: Maker Code (2 bytes)
    a.emit_bytes(b"\x96\x00\x00")       # 0xB2..0xB4: Fixed 0x96, unit=0, device=0
    a.emit_bytes(b"\x00" * 7)           # 0xB5..0xBB: Reserved
    a.emit_bytes(b"\x01\x00\x00\x00")   # 0xBC..0xBF: Version=1, Checksum placeholder, Reserved

    chk = 0
    for b in a.code[0xA0:0xBD]:
        chk = (chk - b) & 0xFF
    chk = (chk - 0x19) & 0xFF
    a.code[0xBD] = chk

    a.label("start")
    a.ldr_lit(13, "lit_sp")             # LDR SP, =0x03007F00
    a.mov_imm(0, 0x04000000)            # MOV R0, #0x04000000 (REG_BASE)
    a.mov_imm(1, 0x0400)                # MOV R1, #0x0400 (BG2_ENABLE)
    a.orr_imm(1, 1, 0x0003)             # ORR R1, R1, #0x0003 (MODE_3)
    a.strh_imm(1, 0, 0)                 # STRH R1, [R0, #0] (DISPCNT)

    # Clear Mode 3 VRAM (240x160 halfwords)
    a.mov_imm(0, 0x06000000)
    a.ldr_lit(1, "lit_bg_color")
    a.mov_imm(2, 240 * 160)
    a.label("bg_loop")
    a.strh_imm(1, 0, 2, p=0)            # STRH R1, [R0], #2
    a.sub_imm(2, 2, 1, s=1)             # SUBS R2, R2, #1
    a.b("bg_loop", cond=0x1)            # BNE bg_loop

    # Top banner rectangle
    a.mov_imm(0, 10); a.mov_imm(1, 8); a.mov_imm(2, 220); a.mov_imm(3, 22)
    a.ldr_lit(4, "lit_banner_bg"); a.bl("fill_rect")

    # Middle CRC32 box rectangle
    a.mov_imm(0, 10); a.mov_imm(1, 68); a.mov_imm(2, 220); a.mov_imm(3, 38)
    a.ldr_lit(4, "lit_crc_box_bg"); a.bl("fill_rect")

    # Draw text lines
    a.mov_imm(0, 28); a.mov_imm(1, 15); a.adr(2, "str_title");   a.ldr_lit(3, "lit_cyan");  a.bl("draw_string")
    a.mov_imm(0, 40); a.mov_imm(1, 36); a.adr(2, "str_studio");  a.ldr_lit(3, "lit_gold");  a.bl("draw_string")
    a.mov_imm(0, 24); a.mov_imm(1, 50); a.adr(2, "str_sub");     a.ldr_lit(3, "lit_green"); a.bl("draw_string")
    a.mov_imm(0, 20); a.mov_imm(1, 74); a.adr(2, "str_region");  a.ldr_lit(3, "lit_white"); a.bl("draw_string")
    a.mov_imm(0, 20); a.mov_imm(1, 90); a.adr(2, "str_crc_lbl"); a.ldr_lit(3, "lit_gold");  a.bl("draw_string")

    # Compute bitwise IEEE 802.3 CRC32 over [0x08000000 .. rom_end)
    a.mov_imm(0, 0x08000000)
    a.ldr_lit(1, "lit_rom_end")
    a.mvn_imm(2, 0)                     # R2 = 0xFFFFFFFF
    a.ldr_lit(3, "lit_crc_poly")        # R3 = 0xEDB88320

    a.label("crc_byte_loop")
    a.ldr_imm(4, 0, 1, b=1, p=0)        # LDRB R4, [R0], #1
    a.eor_reg(2, 2, 4)                  # EOR R2, R2, R4
    a.mov_imm(5, 8)                     # MOV R5, #8
    a.label("crc_bit_loop")
    a.mov_reg(2, 2, shift_imm=1, shift_type=1, s=1) # MOVS R2, R2, LSR #1
    a.eor_reg(2, 2, 3, cond=0x2)        # EORCS R2, R2, R3
    a.sub_imm(5, 5, 1, s=1)             # SUBS R5, R5, #1
    a.b("crc_bit_loop", cond=0x1)       # BNE crc_bit_loop
    a.cmp_reg(0, 1)                     # CMP R0, R1
    a.b("crc_byte_loop", cond=0x3)      # BCC crc_byte_loop

    a.mvn_imm(4, 0)
    a.eor_reg(6, 2, 4)                  # R6 = ~R2 (Final CRC32)
    a.mov_imm(0, 0x03000000)
    a.str_imm(6, 0, 0)                  # Store CRC32 at [0x03000000] in IWRAM

    # Render R6 as 8 hex digits at (116, 90)
    a.mov_imm(7, 28)
    a.mov_imm(8, 116)
    a.label("hex_loop")
    a.mov_reg_rs(4, 6, 7, shift_type=1) # MOV R4, R6, LSR R7
    a.and_imm(4, 4, 0xF)
    a.cmp_imm(4, 10)
    a.add_imm(4, 4, ord('0'), cond=0x3)
    a.add_imm(4, 4, ord('A') - 10, cond=0x2)
    a.mov_reg(0, 8); a.mov_imm(1, 90); a.mov_reg(2, 4); a.ldr_lit(3, "lit_green")
    a.bl("draw_char")
    a.add_imm(8, 8, 8)
    a.sub_imm(7, 7, 4, s=1)
    a.b("hex_loop", cond=0x5)           # BPL hex_loop

    a.mov_imm(0, 20); a.mov_imm(1, 118); a.adr(2, "str_foot1"); a.ldr_lit(3, "lit_cyan");    a.bl("draw_string")
    a.mov_imm(0, 20); a.mov_imm(1, 134); a.adr(2, "str_foot2"); a.ldr_lit(3, "lit_magenta"); a.bl("draw_string")

    # VBlank-synced animated bar
    a.mov_imm(9, 0)
    a.label("main_loop")
    a.mov_imm(0, 0x04000000)
    a.label("wait_vblank")
    a.ldrh_imm(1, 0, 6)
    a.cmp_imm(1, 160)
    a.b("wait_vblank", cond=0x1)
    a.ldrh_imm(2, 0, 0x130)
    a.add_imm(9, 9, 1)
    a.mov_imm(0, 10); a.mov_imm(1, 148); a.mov_imm(2, 220); a.mov_imm(3, 4)
    a.add_reg(4, 9, 9, shift_imm=5, shift_type=0)
    a.bl("fill_rect")
    a.mov_imm(0, 0x04000000)
    a.label("wait_vblank_end")
    a.ldrh_imm(1, 0, 6)
    a.cmp_imm(1, 160)
    a.b("wait_vblank_end", cond=0x0)
    a.b("main_loop")

    # Subroutine: fill_rect(R0=x, R1=y, R2=w, R3=h, R4=color)
    a.label("fill_rect")
    a.push((1<<5)|(1<<6)|(1<<7)|(1<<8)|(1<<14))
    a.mov_imm(5, 0x06000000); a.mov_imm(6, 240)
    a.label("fr_y_loop")
    a.mul(7, 1, 6); a.add_reg(7, 7, 0); a.add_reg(7, 5, 7, shift_imm=1, shift_type=0)
    a.mov_reg(8, 2)
    a.label("fr_x_loop")
    a.strh_imm(4, 7, 2, p=0)
    a.sub_imm(8, 8, 1, s=1); a.b("fr_x_loop", cond=0x1)
    a.add_imm(1, 1, 1); a.sub_imm(3, 3, 1, s=1); a.b("fr_y_loop", cond=0x1)
    a.pop((1<<5)|(1<<6)|(1<<7)|(1<<8)|(1<<15))

    # Subroutine: draw_char(R0=x, R1=y, R2=ascii, R3=color)
    a.label("draw_char")
    a.push((1<<4)|(1<<5)|(1<<6)|(1<<7)|(1<<8)|(1<<9)|(1<<10)|(1<<14))
    a.sub_imm(4, 2, 32); a.adr(5, "font_table"); a.add_reg(5, 5, 4, shift_imm=3, shift_type=0)
    a.mov_imm(6, 0); a.mov_imm(10, 0x06000000)
    a.label("dc_row_loop")
    a.ldr_imm(7, 5, 1, b=1, p=0); a.mov_imm(8, 0)
    a.label("dc_col_loop")
    a.mov_imm(9, 0x80); a.mov_reg_rs(9, 9, 8, shift_type=1)
    a.emit32(a.dp_reg(0x8, 1, 7, 0, 9))
    a.b("dc_skip_px", cond=0x0)
    a.add_reg(4, 1, 6); a.mov_imm(9, 240); a.mul(4, 4, 9); a.add_reg(4, 4, 0); a.add_reg(4, 4, 8)
    a.add_reg(4, 10, 4, shift_imm=1, shift_type=0); a.strh_imm(3, 4, 0)
    a.label("dc_skip_px")
    a.add_imm(8, 8, 1); a.cmp_imm(8, 8); a.b("dc_col_loop", cond=0x3)
    a.add_imm(6, 6, 1); a.cmp_imm(6, 8); a.b("dc_row_loop", cond=0x3)
    a.pop((1<<4)|(1<<5)|(1<<6)|(1<<7)|(1<<8)|(1<<9)|(1<<10)|(1<<15))

    # Subroutine: draw_string(R0=x, R1=y, R2=str_ptr, R3=color)
    a.label("draw_string")
    a.push((1<<4)|(1<<5)|(1<<6)|(1<<14))
    a.mov_reg(4, 0); a.mov_reg(5, 1); a.mov_reg(6, 2)
    a.label("ds_loop")
    a.ldr_imm(2, 6, 1, b=1, p=0); a.cmp_imm(2, 0); a.b("ds_done", cond=0x0)
    a.mov_reg(0, 4); a.mov_reg(1, 5); a.bl("draw_char")
    a.add_imm(4, 4, 8); a.b("ds_loop")
    a.label("ds_done")
    a.pop((1<<4)|(1<<5)|(1<<6)|(1<<15))

    # Literal Pool
    a.align(4)
    a.label("lit_sp");         a.emit32(0x03007F00)
    a.label("lit_bg_color");   a.emit32(rgb15(2, 3, 8))
    a.label("lit_banner_bg");  a.emit32(rgb15(8, 2, 16))
    a.label("lit_crc_box_bg"); a.emit32(rgb15(1, 7, 11))
    a.label("lit_cyan");       a.emit32(rgb15(4, 31, 31))
    a.label("lit_gold");       a.emit32(rgb15(31, 27, 4))
    a.label("lit_green");      a.emit32(rgb15(6, 31, 10))
    a.label("lit_white");      a.emit32(rgb15(31, 31, 31))
    a.label("lit_magenta");    a.emit32(rgb15(31, 8, 28))
    a.label("lit_crc_poly");   a.emit32(0xEDB88320)
    a.label("lit_rom_end")
    rom_end_patch_offset = len(a.code)
    a.emit32(0)

    def emit_cstr(lbl, s):
        a.align(4)
        a.label(lbl)
        a.emit_bytes(s.encode('ascii') + b'\x00')
        a.align(4)

    emit_cstr("str_title",   "1337BOY COLOR ADVANCE")
    emit_cstr("str_studio",  "CONSCIOUSNODE / XINU")
    emit_cstr("str_sub",     "SELF-HOSTED POLYGLOT ROM")
    emit_cstr("str_region",  "ROM: 08000000 (QUINE)")
    emit_cstr("str_crc_lbl", "SELF CRC32: ")
    emit_cstr("str_foot1",   "HW == MGBA == 1337BOY")
    emit_cstr("str_foot2",   "EVERY CART IS A CONSOLE")

    a.align(4)
    a.label("font_table")
    for code_pt in range(32, 91):
        a.emit_bytes(bytes(FONT_8X8.get(chr(code_pt), [0]*8)))

    a.align(16)
    rom_len = len(a.code)
    struct.pack_into("<I", a.code, rom_end_patch_offset, 0x08000000 + rom_len)
    a.resolve()
    return bytes(a.code)


def strip_polyglot_tail(data):
    """If data is already a 1337Boy polyglot, strip the reset sequence and HTML tail."""
    idx = data.find(B1337_RESET_SEQ)
    if idx != -1:
        return data[:idx], True
    return data, False


def scan_rom(rom_bytes):
    """
    Scans ROM bytes case-insensitively for <plaintext (unrecoverable)
    and reports every other tag-like opening (< followed by letter, !, /, or ?).
    """
    lower = rom_bytes.lower()
    if b"<plaintext" in lower:
        raise ValueError("Refusing ROM: contains unrecoverable '<plaintext' sequence.")

    risky_tags = [
        b"<!--", b"<script", b"</script", b"<style", b"</style",
        b"<title", b"</title", b"<textarea", b"</textarea",
        b"<xmp", b"</xmp", b"<iframe", b"</iframe",
        b"<noscript", b"</noscript", b"<noembed", b"</noembed",
        b"<noframes", b"</noframes", b"<svg", b"</svg", b"<math", b"</math"
    ]
    found_risky = []
    for tag in risky_tags:
        pos = lower.find(tag)
        while pos != -1:
            found_risky.append((pos, tag.decode('ascii')))
            pos = lower.find(tag, pos + 1)

    openers = list(re.finditer(rb'<[a-zA-Z!/?]', rom_bytes))
    return found_risky, openers


def build_polyglot_bytes(rom_bytes, html_template_path):
    """
    Builds a byte-identical 1337Boy polyglot from rom_bytes and 1337boy.html.
    Matches the in-browser buildPolyglotCartridge() byte-for-byte.
    """
    clean_rom, was_stripped = strip_polyglot_tail(rom_bytes)
    found_risky, openers = scan_rom(clean_rom)

    with open(html_template_path, "rb") as f:
        template_bytes = f.read()

    # Extract pristine <style id="b1337-style"> and <script id="b1337-core">
    m_style = re.search(rb'<style id="b1337-style">([\s\S]*?)</style>', template_bytes)
    m_core  = re.search(rb'<script id="b1337-core">([\s\S]*?)</script>', template_bytes)
    if not m_style or not m_core:
        raise RuntimeError(f"Could not find pristine #b1337-style / #b1337-core tags in {html_template_path}")

    style_bytes = m_style.group(1)
    core_bytes  = m_core.group(1)
    rom_b64     = base64.b64encode(clean_rom)

    html_doc = (
        b'<!DOCTYPE html>\n'
        b'<html lang="en">\n'
        b'<head>\n'
        b'<meta charset="utf-8">\n'
        b'<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\' blob:; style-src \'unsafe-inline\'; img-src data: blob:; media-src blob:; worker-src blob:; connect-src \'none\';">\n'
        b'<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">\n'
        b'<title>1337Boy(TM) COLOR ADVANCE TURBO - Self-Hosted GBA Cartridge</title>\n'
        b'<style id="b1337-style">' + style_bytes + b'</style>\n'
        b'</head>\n'
        b'<body>\n'
        b'<script id="b1337-rom-b64" type="text/plain">' + rom_b64 + b'</script>\n'
        b'<script id="b1337-core">' + core_bytes + b'</script>\n'
        b'</body>\n'
        b'</html>\n'
    )

    return clean_rom + B1337_RESET_SEQ + html_doc, clean_rom, was_stripped, found_risky, openers


def find_default_template():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "1337boy.html"),
        os.path.join(here, "1337boy.html"),
        "1337boy.html",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Cannot locate 1337boy.html template. Pass --template <path>.")


def main():
    parser = argparse.ArgumentParser(description="1337ify: Build a self-playing GBA + HTML5 polyglot cartridge.")
    parser.add_argument("input", nargs="?", help="Input .gba ROM file (or existing .1337.gba polyglot)")
    parser.add_argument("-o", "--output", required=True, help="Output .1337.gba / .1337.html path")
    parser.add_argument("--template", help="Path to 1337boy.html template (auto-detected if omitted)")
    parser.add_argument("--build-boot", action="store_true", help="Hand-assemble the 1337 BOOT demo ROM and 1337ify it")
    parser.add_argument("--raw-boot-only", action="store_true", help="Output only the raw hand-assembled 1337boot.gba ROM")
    args = parser.parse_args()

    if args.raw_boot_only:
        rom_bytes = assemble_1337boot_rom()
        with open(args.output, "wb") as f:
            f.write(rom_bytes)
        crc = zlib.crc32(rom_bytes) & 0xFFFFFFFF
        print(f"[1337ify] Hand-assembled raw 1337boot.gba: {len(rom_bytes)} bytes, CRC32={crc:08X}")
        return 0

    if args.build_boot:
        rom_bytes = assemble_1337boot_rom()
        src_label = "hand-assembled 1337boot.gba"
    elif args.input:
        with open(args.input, "rb") as f:
            rom_bytes = f.read()
        src_label = args.input
    else:
        parser.error("Provide an input .gba file or pass --build-boot")

    tpl_path = args.template or find_default_template()
    poly_bytes, clean_rom, was_stripped, found_risky, openers = build_polyglot_bytes(rom_bytes, tpl_path)

    with open(args.output, "wb") as f:
        f.write(poly_bytes)

    crc = zlib.crc32(clean_rom) & 0xFFFFFFFF
    poly_crc = zlib.crc32(poly_bytes) & 0xFFFFFFFF
    if was_stripped:
        print(f"[1337ify] Detected existing 1337Boy tail on {src_label}; stripped old HTML tail before re-1337ifying.")
    print(f"[1337ify] Scanned {len(clean_rom)} ROM bytes: 0 '<plaintext' occurrences, {len(found_risky)} risky tag match(es), {len(openers)} tag-like opener(s) (<[a-zA-Z!/?]).")
    for pos, tok in found_risky:
        print(f"  -> Risky opener '{tok}' at offset 0x{pos:X}")
    print(f"[1337ify] ROM CRC32: 0x{crc:08X} | Polyglot output: {args.output} ({len(poly_bytes)} bytes, CRC32=0x{poly_crc:08X})")
    return 0


if __name__ == "__main__":
    sys.exit(main())