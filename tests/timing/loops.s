@ Timing probes (Kehai Interim). Each takes r0 = iteration count.
    .syntax unified
    .arm
    .section .iwram, "ax", %progbits
    .align 2
    .global t_iw_alu, t_iw_ldr_iw, t_iw_ldr_ew, t_iw_mul, t_iw_str_vram, t_iw_branch, t_iw_ldr_rom
t_iw_alu:            @ 4 ALU ops + loop
1:  add r1, r1, #1
    add r2, r2, #1
    eor r3, r3, r1
    orr r12, r12, r2
    subs r0, r0, #1
    bne 1b
    bx lr
t_iw_ldr_iw:         @ 4 loads from IWRAM
    ldr r1, =0x03004000
1:  ldr r2, [r1]
    ldr r3, [r1, #4]
    ldr r12, [r1, #8]
    ldr r2, [r1, #12]
    subs r0, r0, #1
    bne 1b
    bx lr
t_iw_ldr_ew:         @ 4 loads from EWRAM
    ldr r1, =0x02010000
1:  ldr r2, [r1]
    ldr r3, [r1, #4]
    ldrh r12, [r1, #8]
    ldrb r2, [r1, #12]
    subs r0, r0, #1
    bne 1b
    bx lr
t_iw_mul:            @ 2 multiplies with a large operand
    ldr r1, =0x12345678
    ldr r2, =0x0FEDCBA9
1:  mul r3, r1, r2
    mla r12, r2, r1, r3
    subs r0, r0, #1
    bne 1b
    bx lr
t_iw_str_vram:       @ 4 stores to VRAM
    ldr r1, =0x06010000
1:  str r2, [r1]
    strh r2, [r1, #4]
    str r2, [r1, #8]
    strb r2, [r1, #12]
    subs r0, r0, #1
    bne 1b
    bx lr
t_iw_branch:         @ taken branches
1:  b 2f
2:  b 3f
3:  subs r0, r0, #1
    bne 1b
    bx lr
t_iw_ldr_rom:        @ 4 loads from ROM
    ldr r1, =0x08000100
1:  ldr r2, [r1]
    ldr r3, [r1, #4]
    ldrh r12, [r1, #8]
    ldr r2, [r1, #64]
    subs r0, r0, #1
    bne 1b
    bx lr
    .pool
    .text
    .thumb
    .align 2
    .global t_rom_thumb
    .thumb_func
t_rom_thumb:         @ Thumb loop running from ROM
1:  adds r1, #1
    adds r2, #1
    eors r3, r1
    subs r0, #1
    bne 1b
    bx lr
    .arm
    .align 2
    .global t_rom_arm
t_rom_arm:           @ ARM loop running from ROM
1:  add r1, r1, #1
    add r2, r2, #1
    subs r0, r0, #1
    bne 1b
    bx lr
