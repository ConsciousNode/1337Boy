// Timing probe ROM: cycles per loop iteration, measured with cascaded timers.
#include <tonc.h>
typedef void (*fn)(u32);
extern void t_iw_alu(u32), t_iw_ldr_iw(u32), t_iw_ldr_ew(u32), t_iw_mul(u32), t_iw_str_vram(u32), t_iw_branch(u32), t_iw_ldr_rom(u32);
extern void t_rom_thumb(u32), t_rom_arm(u32);
static void utoa_pad(char *b, u32 v, int w) { char t[12]; int n = 0; do { t[n++] = "0123456789"[v % 10]; v /= 10; } while (v); for (int i = 0; i < w - n; i++) *b++ = ' '; while (n) *b++ = t[--n]; *b = 0; }
static u32 timeit(fn f, u32 n) {
    REG_TM2CNT = 0; REG_TM3CNT = 0; REG_TM2D = 0; REG_TM3D = 0;
    REG_TM3CNT = TM_ENABLE | TM_CASCADE; REG_TM2CNT = TM_ENABLE;
    f(n);
    REG_TM2CNT = 0;
    return ((u32)REG_TM3D << 16) | REG_TM2D;
}
int main(void) {
    REG_IME = 0;
    tte_init_chr4c_default(0, BG_CBB(0) | BG_SBB(31));
    REG_DISPCNT = DCNT_MODE0 | DCNT_BG0;
    static const struct { const char *name; fn f; } T[] = {
        {"IW ALU4  ", t_iw_alu}, {"IW LDR IW", t_iw_ldr_iw}, {"IW LDR EW", t_iw_ldr_ew}, {"IW MUL2  ", t_iw_mul},
        {"IW STR VR", t_iw_str_vram}, {"IW BRANCH", t_iw_branch}, {"IW LDRROM", t_iw_ldr_rom},
        {"ROM THUMB", (fn)t_rom_thumb}, {"ROM ARM  ", t_rom_arm}};
    char buf[48]; int y = 0;
    for (int w = 0; w < 2; w++) {
        REG_WAITCNT = w ? 0x4317 : 0x0000;
        tte_set_pos(0, y); tte_write(w ? "WAITCNT 4317 cyc x100/iter" : "WAITCNT 0000 cyc x100/iter"); y += 8;
        for (unsigned i = 0; i < sizeof T / sizeof T[0]; i++) {
            u32 n = 2000, c = timeit(T[i].f, n), base = timeit(T[i].f, 1);
            u32 per = ((c - base) * 100) / (n - 1);
            tte_set_pos(0, y); tte_write(T[i].name); utoa_pad(buf, per, 7); tte_write(buf); y += 8;
        }
    }
    while (1) VBlankIntrWait();
}
