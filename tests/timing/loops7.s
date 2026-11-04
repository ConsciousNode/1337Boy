    .syntax unified
    .text
    .thumb
    .align 2
    .global v_ldr, v_ldm
    .thumb_func
v_ldr:               @ LDR one word from ROM
    ldr r1, =tbl7
1:  ldr r2, [r1]
    adds r1, #0
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
v_ldm:               @ LDMIA one word from the same ROM address
    ldr r1, =tbl7
1:  ldmia r1!, {r2}
    subs r1, #4
    subs r0, #1
    bne 1b
    bx lr
    .pool
    .align 2
tbl7: .word 0x12345678, 0
