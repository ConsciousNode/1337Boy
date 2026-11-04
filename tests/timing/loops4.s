    .syntax unified
    .text
    .thumb
    .align 2
    .global q_bl, q_push, q_lit, q_vram16, q_ldrrom, q_ldrsp, q_bcond, q_ldmia
    .thumb_func
leaf: bx lr
    .thumb_func
q_bl:                @ BL + BX LR round trip
    push {lr}
1:  bl leaf
    subs r0, #1
    bne 1b
    pop {r1}
    bx r1
    .thumb_func
q_push:              @ push/pop 4 regs (IWRAM stack)
    push {r4-r7}
1:  push {r4-r7}
    pop {r4-r7}
    subs r0, #1
    bne 1b
    pop {r4-r7}
    bx lr
    .thumb_func
q_lit:               @ PC-relative literal loads (ROM data)
1:  ldr r1, =0x12345678
    ldr r2, =0x0BADF00D
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
q_vram16:            @ halfword read-modify-write in VRAM
    ldr r1, =0x06008000
1:  ldrh r2, [r1]
    adds r2, #1
    strh r2, [r1]
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
q_ldrrom:            @ word + byte loads from ROM table
    ldr r1, =tbl
1:  ldr r2, [r1, #4]
    ldrb r3, [r1, #9]
    subs r0, #1
    bne 1b
    bx lr
    .thumb_func
q_ldrsp:             @ SP-relative load/store (IWRAM)
    sub sp, #8
1:  str r0, [sp, #4]
    ldr r1, [sp, #4]
    subs r0, #1
    bne 1b
    add sp, #8
    bx lr
    .thumb_func
q_bcond:             @ taken short branch chain
1:  b 2f
2:  b 3f
3:  subs r0, #1
    bne 1b
    bx lr
    .thumb_func
q_ldmia:             @ Thumb LDMIA from ROM
    push {r4,r5}
1:  ldr r1, =tbl
    ldmia r1!, {r2-r5}
    subs r0, #1
    bne 1b
    pop {r4,r5}
    bx lr
    .pool
    .align 2
tbl: .word 1,2,3,4,5,6,7,8
