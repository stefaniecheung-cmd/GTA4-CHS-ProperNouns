# -*- coding: utf-8 -*-
import struct, os

P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS.asi"
d = open(P, "rb").read()
print("asi 大小", len(d))

TARGETS = {
    3517: "原字表数", 3580: "v1字表数", 512: "汉字起点", 62: "列数", 66: "格距",
    3484: "末段起点", 3579: "末字index", 4096: "图宽", 3348: "ASCII起点", 3443: "末段格",
}
for val, name in TARGETS.items():
    pats = []
    # 4字节
    pats.append(("u32", struct.pack("<I", val)))
    # 3字节（可能被截断的小常量）
    if val < 0x1000000:
        pats.append(("u24", struct.pack("<I", val)[:3]))
    # 2字节
    if val < 0x10000:
        pats.append(("u16", struct.pack("<H", val)))
    hits = []
    for kind, p in pats:
        start = 0
        while True:
            i = d.find(p, start)
            if i < -1 or i == -1:
                break
            hits.append((kind, i))
            start = i + 1
            if len(hits) > 40:
                break
    print("%-10s %5d  命中 %d 处: %s" % (name, val, len(hits), hits[:12]))
