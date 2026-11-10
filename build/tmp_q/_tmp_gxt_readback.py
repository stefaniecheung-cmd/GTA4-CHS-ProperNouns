# -*- coding: utf-8 -*-
import io, os, sys
csv = None
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt
ROOT = r"C:\Game\gta4-chs"
TARGET = {
    "base": ["2C924360","9AF702B1","BF73CBAA","D3CE008D","92984525","FB0B04EC"],
    "TLAD": ["4C6144A0","4FC055AF","E8506E8D"],
    "TBoGT": ["B558BA99","9603CE32","A8889735"],
}
for ch, crcs in TARGET.items():
    p = os.path.join(ROOT, "build", f"zchs_{ch}_tr.gxt")
    _, es = parse_gxt(p)
    m = {"%08X"%c: x for t,c,x in es}
    for c in crcs:
        print(f"[{ch} {c}] {m.get(c,'<缺失!>')!r}")
