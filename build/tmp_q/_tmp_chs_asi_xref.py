# -*- coding: utf-8 -*-
import struct

P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS\asi_dummy_noop.tmp"
P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS.asi"
d = open(P, "rb").read()

SECT = [(".text", 0x1000, 0x2DD98, 0x2DE00, 0x400),
        (".rdata", 0x2F000, 0xC0DA, 0xC200, 0x2E200),
        (".data", 0x3C000, 0x599C, 0x4A00, 0x3A400),
        (".rsrc", 0x42000, 0x1E0, 0x200, 0x3EE00),
        (".reloc", 0x43000, 0x2A5C, 0x2C00, 0x3F000)]
IMG = 0x10000000


def f2v(off):
    for n, va, vsz, rsz, rp in SECT:
        if rp <= off < rp + rsz:
            return IMG + va + (off - rp)
    return None


def v2f(va):
    for n, sva, vsz, rsz, rp in SECT:
        if IMG + sva <= va < IMG + sva + vsz:
            return rp + (va - (IMG + sva))
    return None


TARGETS = {
    "char_table.dat": 0x2F7C8,
    "whm_table.dat": 0x2F7D8,
    "font_chs": 0x2E6C0,
    "GTA4.CHS": 0x2F7BC,
}
for name, off in TARGETS.items():
    va = f2v(off)
    print("\n%s  文件 0x%06X -> VA 0x%08X" % (name, off, va))
    pat = struct.pack("<I", va)
    refs = []
    start = 0
    while True:
        i = d.find(pat, start)
        if i == -1:
            break
        refs.append(i)
        start = i + 1
    print("  引用 %d 处:" % len(refs), ["0x%06X(VA 0x%08X)" % (r, f2v(r)) for r in refs[:10]])
