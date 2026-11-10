# -*- coding: utf-8 -*-
import csv, io, random, sys, os
csv.field_size_limit(10**9)
p = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\cmp_assets\未译_分类.tsv"
rd = list(csv.DictReader(io.open(p, encoding="utf-8-sig"), delimiter="\t"))
random.seed(7)
for r in random.sample(rd, 45):
    print(f"{r['章节']:5} {r['CRC']} {r['英文原文'][:70]}")
