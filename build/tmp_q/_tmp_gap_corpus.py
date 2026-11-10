# -*- coding: utf-8 -*-
import csv, io, os, sys
csv.field_size_limit(10**9)
BUILD = r"C:\Game\gta4-chs\build"
# 读缺口清单
gap = list(csv.DictReader(io.open(os.path.join(BUILD, r"cmp_assets\未译_我方缺口_v10译了.tsv"), encoding="utf-8-sig"), delimiter="\t"))
# corpus 英文
corpus = {}
for ch in ("base", "TLAD", "TBoGT"):
    with io.open(os.path.join(BUILD, r"..\data", f"corpus_{ch}.tsv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            corpus[(ch, r["crc"].upper())] = r["english"]

for r in gap:
    en = corpus.get((r["章节"], r["CRC"]), "<无corpus>")
    print(f"{r['章节']:5} {r['CRC']}")
    print(f"   EN : {en[:90]!r}")
    print(f"   我方: {r['我方(英文)'][:90]!r}")
    print(f"   v10: {r['v10译文'][:90]!r}")
