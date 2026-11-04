    .syntax unified
    .section .iwram, "ax", %progbits
    .arm
    .align 2
    .global p_umlal_small, p_smull_neg
p_umlal_small:       @ UMLAL with small unsigned multiplier, and UMULL with 0xFFFFFF00 (signed-small but unsigned-large)
    mov r1, #7
    ldr r2, =0xFFFFFF00
1:  umlal r3, r12, r2, r1
    umull r3, r12, r1, r2
    subs r0, r0, #1
    bne 1b
    bx lr
p_smull_neg:         @ SMULL with -2 multiplier (m=1 signed)
    mvn r1, #1
    ldr r2, =0x12345678
1:  smull r3, r12, r2, r1
    smlal r3, r12, r2, r1
    subs r0, r0, #1
    bne 1b
    bx lr
    .pool
    .thumb
    .align 2
    .global p_tmul_small, p_tmul_big
    .thumb_func
p_tmul_small:        @ Thumb MUL, Rd (multiplier) small
    movs r1, #5
1:  movs r2, #9
    muls r2, r1
    movs r2, #9
    muls r2, r1
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
p_tmul_big:          @ Thumb MUL, Rd large
    movs r1, #5
    ldr r3, =0x12345678
1:  adds r2, r3, #0
    muls r2, r1
    adds r2, r3, #0
    muls r2, r1
    subs r0, #1
    bne 1b
    bx lr
    .pool
