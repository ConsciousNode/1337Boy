    .syntax unified
    .text
    .thumb
    .align 2
    .global u_tmul, u_ret, u_tlsl, u_tldrew, u_tstrvr
    .thumb_func
u_tmul:
    ldr r3, =0x12345
1:  adds r2, r3, #0
    muls r2, r3
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
fpop: push {r4, lr}
    pop {r4, pc}
    .thumb_func
u_ret:
    push {lr}
1:  bl fpop
    subs r0, #1
    bne 1b
    pop {r1}
    bx r1
    .thumb_func
u_tlsl:
    movs r3, #3
1:  lsls r1, r3
    lsrs r1, r3
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
u_tldrew:
    ldr r1, =0x02010000
1:  ldr r2, [r1]
    adds r2, #1
    adds r2, #1
    adds r2, #1
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
u_tstrvr:
    ldr r1, =0x06008000
1:  str r0, [r1]
    strh r0, [r1, #4]
    adds r2, #1
    subs r0, #1
    bne 1b
    bx lr
    .pool
    .arm
    .align 2
    .global u_amul, u_amull
u_amul:
    ldr r3, =0x12345
1:  mul r2, r3, r3
    subs r0, r0, #1
    bne 1b
    bx lr
u_amull:
    ldr r3, =0x12345678
1:  umull r2, r12, r3, r3
    subs r0, r0, #1
    bne 1b
    bx lr
    .pool
