# -*- coding: utf-8 -*-
"""我方非中文条目 vs v10 成品交叉：v10 译了我方没译才是真缺口。"""
import csv, io, os, re, sys, collections
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

BUILD = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
V10 = {
    "base": r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0\update\common\text\american.gxt",
    "TLAD": r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0\update\TLAD\common\text\american.gxt",
    "TBoGT": r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0\update\TBoGT\common\text\american.gxt",
}
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\cmp_assets\未译_我方缺口_v10译了.tsv"

def has_cjk(s):
    return any("\u4e00" <= x <= "\u9fff" for x in s)

# v10 键集
v10 = {}
for ch, p in V10.items():
    _, es = parse_gxt(p)
    v10[ch] = {(t, "%08X" % c): x for t, c, x in es}

gap, keep_both, missing_v10 = [], [], []
counts = collections.Counter()
for ch in ("base", "TLAD", "TBoGT"):
    p = os.path.join(BUILD, f"src_{ch}_tr.tsv")
    with io.open(p, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            zh = r["text"]
            if has_cjk(zh):
                continue
            key = (r["table"], r["crc"].upper())
            v = v10[ch].get(key)
            if v is None:
                counts[(ch, "v10无键")] += 1
                missing_v10.append((ch, *key, zh, ""))
            elif has_cjk(v):
                counts[(ch, "我方缺口")] += 1
                gap.append((ch, *key, zh, v))
            else:
                counts[(ch, "双方保留英文")] += 1
                keep_both.append((ch, *key, zh, v))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8-sig", newline="") as g:
    g.write("章节\t表\tCRC\t我方(英文)\tv10译文\n")
    for ch, t, c, x, v in gap:
        g.write(f"{ch}\t{t}\t{c}\t{x}\t{v}\n")

for ch in ("base", "TLAD", "TBoGT"):
    print(f"[{ch}] 缺口(v10译了)={counts[(ch,'我方缺口')]} 双方保留={counts[(ch,'双方保留英文')]} v10无键={counts[(ch,'v10无键')]}")
print("缺口合计:", len(gap), "->", OUT)
