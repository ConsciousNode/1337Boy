    .syntax unified
    .arm
    .section .iwram, "ax", %progbits
    .align 2
    .global p_str_ew, p_ldm_iw, p_stm_ew, p_smull, p_shiftreg, p_ldrs_ew, p_bnt, p_ldrb_ew
p_str_ew:            @ 4 stores to EWRAM
    ldr r1, =0x02010000
1:  str r2, [r1]
    strh r2, [r1, #4]
    strb r2, [r1, #6]
    str r2, [r1, #8]
    subs r0, r0, #1
    bne 1b
    bx lr
p_ldm_iw:            @ LDM 4 regs from IWRAM
    push {r4-r7}
    ldr r1, =0x03004000
1:  ldmia r1, {r4-r7}
    subs r0, r0, #1
    bne 1b
    pop {r4-r7}
    bx lr
p_stm_ew:            @ STM 4 regs to EWRAM
    push {r4-r7}
    ldr r1, =0x02010000
1:  stmia r1, {r4-r7}
    subs r0, r0, #1
    bne 1b
    pop {r4-r7}
    bx lr
p_smull:             @ long multiplies
    ldr r1, =0x12345678
    ldr r2, =0x0FEDCBA9
1:  smull r3, r12, r1, r2
    umull r3, r12, r2, r1
    subs r0, r0, #1
    bne 1b
    bx lr
p_shiftreg:          @ register-specified shifts (+1 internal cycle each)
    mov r3, #3
1:  add r1, r1, r2, lsl r3
    eor r2, r2, r1, lsr r3
    subs r0, r0, #1
    bne 1b
    bx lr
p_ldrs_ew:           @ signed loads from EWRAM
    ldr r1, =0x02010000
1:  ldrsb r2, [r1]
    ldrsh r3, [r1, #2]
    subs r0, r0, #1
    bne 1b
    bx lr
p_bnt:               @ untaken branches
    mov r1, #1
    cmp r1, #0
1:  beq 9f
    beq 9f
    beq 9f
    subs r0, r0, #1
    bne 1b
9:  bx lr
p_ldrb_ew:           @ byte loads from EWRAM, then a dependent store to IWRAM
    ldr r1, =0x02010000
    ldr r3, =0x03004000
1:  ldrb r2, [r1, #1]
    strb r2, [r3]
    subs r0, r0, #1
    bne 1b
    bx lr
    .pool
    .thumb
    .align 2
    .global p_thumb_iw
    .thumb_func
p_thumb_iw:          @ Thumb code in IWRAM with EWRAM loads
    ldr r1, =0x02010000
1:  ldr r2, [r1]
    ldrh r3, [r1, #4]
    adds r2, r3
    subs r0, #1
    bne 1b
    bx lr
    .pool
    .text
    .thumb
    .align 2
    .global p_thumb_rom_ld
    .thumb_func
p_thumb_rom_ld:      @ Thumb code in ROM loading from IWRAM (prefetch buffer can work)
    ldr r1, =0x03004000
1:  ldr r2, [r1]
    adds r2, #1
    str r2, [r1]
    subs r0, #1
    bne 1b
    bx lr
    .pool
