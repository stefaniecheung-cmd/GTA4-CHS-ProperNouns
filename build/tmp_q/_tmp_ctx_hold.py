# -*- coding: utf-8 -*-
import io, sys
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
targets = {"E50E2243", "CC495487", "1AEDA761", "96E75BE0", "BBC92791", "5D478FFD"}
files = [("base", "zchs_base.gxt"), ("TLAD", "zchs_TLAD.gxt"), ("TBoGT", "zchs_TBoGT.gxt")]

for chap, fn in files:
    try:
        tables, items = parse_gxt(rf"{B}\{fn}")
    except Exception as e:
        print("ERR", fn, e); continue
    idx = {}
    for t, c, txt in items:
        k = c if isinstance(c, int) else int(c, 16)
        idx.setdefault((t, k), txt)
    for t, k in idx:
        hexk = "%08X" % k
        if hexk in targets:
            print("=" * 70)
            print(f"[{chap}] table={t} crc={hexk}")
            print("FULL:", repr(idx[(t, k)]))
            # 同表相邻 4 条
            keys = sorted([kk for (tt, kk) in idx if tt == t])
            pos = keys.index(k)
            for j in range(max(0, pos - 3), min(len(keys), pos + 4)):
                kk = keys[j]
                mark = ">>" if kk == k else "  "
                print(mark, "%08X" % kk, repr(idx[(t, kk)])[:300])
