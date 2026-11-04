    .syntax unified
    .text
    .thumb
    .align 2
    .global r_ldm4rom, r_ldm4iw, r_ldm1rom, r_stm4iw, r_ldm1iw
    .thumb_func
r_ldm4rom:
    push {r4,r5}
    ldr r1, =tbl5
1:  ldmia r1!, {r2-r5}
    subs r1, #16
    subs r0, #1
    bne 1b
    pop {r4,r5}
    bx lr
    .thumb_func
r_ldm4iw:
    push {r4,r5}
    ldr r1, =0x03004000
1:  ldmia r1!, {r2-r5}
    subs r1, #16
    subs r0, #1
    bne 1b
    pop {r4,r5}
    bx lr
    .thumb_func
r_ldm1rom:
    ldr r1, =tbl5
1:  ldmia r1!, {r2}
    subs r1, #4
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
r_ldm1iw:
    ldr r1, =0x03004000
1:  ldmia r1!, {r2}
    subs r1, #4
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
r_stm4iw:
    push {r4,r5}
    ldr r1, =0x03004000
1:  stmia r1!, {r2-r5}
    subs r1, #16
    subs r0, #1
    bne 1b
    pop {r4,r5}
    bx lr
    .pool
    .align 2
tbl5: .word 1,2,3,4,5,6,7,8
    .arm
    .align 2
    .global a_ldriw, a_ldmiw, a_strvr, a_ldrrom
a_ldriw:
    ldr r1, =0x03004000
1:  ldr r2, [r1]
    add r3, r2, #1
    subs r0, r0, #1
    bne 1b
    bx lr
a_ldmiw:
    push {r4-r7}
    ldr r1, =0x03004000
1:  ldmia r1, {r4-r7}
    subs r0, r0, #1
    bne 1b
    pop {r4-r7}
    bx lr
a_strvr:
    ldr r1, =0x06008000
1:  str r0, [r1]
    strh r0, [r1, #4]
    subs r0, r0, #1
    bne 1b
    bx lr
a_ldrrom:
    ldr r1, =tbl5
1:  ldr r2, [r1, #4]
    ldrb r3, [r1, #9]
    subs r0, r0, #1
    bne 1b
    bx lr
    .pool
