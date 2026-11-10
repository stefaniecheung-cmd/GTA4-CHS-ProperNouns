# -*- coding: utf-8 -*-
import io, os, sys, csv
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt
ROOT = r"C:\Game\gta4-chs"

# 1) zh_global 原始目标行
print("=== zh_global.tsv 目标行（物理行）===")
gp = os.path.join(ROOT, "data", "zh_global.tsv")
targets = {"2C924360","9AF702B1","BF73CBAA","D3CE008D","92984525","FB0B04EC",
           "4C6144A0","E8506E8D","A8889735","B558BA99"}
with io.open(gp, encoding="utf-8") as f:
    head = f.readline().rstrip("\n").split("\t")
    print("表头:", head)
    for line in f:
        q = line.rstrip("\n").split("\t")
        if q and q[0].strip().upper() in targets:
            print(" | ".join(repr(x) for x in q))

# 2) 同表上下文（定稿 gxt）
def show(ch, crc, n=4):
    p = os.path.join(ROOT, "build", f"zchs_{ch}_tr.gxt")
    tables, entries = parse_gxt(p)
    idx = [i for i,(t,c,x) in enumerate(entries) if "%08X"%c == crc]
    if not idx:
        print(ch, crc, "未找到"); return
    i = idx[0]
    print(f"\n=== {ch} 表上下文 (条目 {i}) ===")
    for j in range(max(0,i-n), min(len(entries), i+n+1)):
        t,c,x = entries[j]
        mark = ">>" if j==i else "  "
        print(f"{mark} [{t} %08X] {x[:70]!r}" % c)

show("TLAD", "4C6144A0")
show("TBoGT", "A8889735")
