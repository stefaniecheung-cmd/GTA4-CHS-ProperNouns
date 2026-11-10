# -*- coding: utf-8 -*-
import struct

P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS.asi"
d = open(P, "rb").read()

SECT = [(".text", 0x1000, 0x2DD98, 0x2DE00, 0x400),
        (".rdata", 0x2F000, 0xC0DA, 0xC200, 0x2E200),
        (".data", 0x3C000, 0x599C, 0x4A00, 0x3A400)]
IMG = 0x10000000


def f2v(off):
    for n, va, vsz, rsz, rp in SECT:
        if rp <= off < rp + rsz:
            return IMG + va + (off - rp)
    return None


print("== 0x100305E8 处的第三个资源名（长 24） ==")
foff = None
for n, va, vsz, rsz, rp in SECT:
    if IMG + va <= 0x100305E8 < IMG + va + vsz:
        foff = rp + (0x100305E8 - (IMG + va))
print("  文件偏移 0x%X" % foff)
raw = d[foff:foff + 0xC0]
print("  hex:", raw.hex(" "))
import re
for m in re.finditer(rb"[ -~]{3,}", raw):
    print("  串:", m.group().decode("latin-1"))

print("\n== 浮点常量搜索 ==")
CAND = {
    "4096.0f": 0x45800000, "66.0f": 0x42840000, "62.0f": 0x42780000,
    "33.0f": 0x42040000, "512.0f": 0x44000000, "4092.0f": 0x457FC000,
    "0.01515151f": 0, "1/4096f": 0x39800000,
}
for name, u in CAND.items():
    if u == 0:
        continue
    pat = struct.pack("<I", u)
    hits = []
    s = 0
    while True:
        i = d.find(pat, s)
        if i == -1:
            break
        hits.append(i)
        s = i + 1
    print("  %-12s 0x%08X 命中 %d: %s" % (name, u, len(hits), ["0x%06X(VA 0x%08X)" % (h, f2v(h)) for h in hits[:8]]))

# 搜 double
print("\n== double 常量 ==")
for name, u in {"4096.0": 0x40B0000000000000, "66.0": 0x4050800000000000,
                "62.0": 0x404F000000000000}.items():
    pat = struct.pack("<Q", u)
    hits = []
    s = 0
    while True:
        i = d.find(pat, s)
        if i == -1:
            break
        hits.append(i); s = i + 1
    print("  %-8s 命中 %d: %s" % (name, len(hits), ["0x%06X" % h for h in hits[:8]]))
