# -*- coding: utf-8 -*-
import io, csv, re
from collections import Counter
csv.field_size_limit(10**9)
ZG = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\zh_global.tsv"

# 抓「名字 + 间隔符 + 后续」的完整全名形态
pat = re.compile(r"(尼克|尼科|罗曼)[\u00b7\uff65\u2022\.]?\s?(贝[利里][克奇])?")
full = Counter()
lanc = []
with io.open(ZG, encoding="utf-8", newline="") as f:
    rd = csv.reader(f, delimiter="\t")
    next(rd, None)
    for p in rd:
        if len(p) < 2: continue
        z = p[1]
        for m in re.finditer(r"(尼克|尼科|罗曼)[\u00b7\uff65·.]?(贝[利里][克奇])", z):
            full[m.group(0)] += 1
        for m in re.finditer(r"(尼克|尼科|罗曼)[\u00b7\uff65·.]([^\s，。！？、]+)", z):
            if "贝" not in m.group(0):
                lanc.append((p[0], z[max(0,m.start()-12):m.end()+12]))

print("全名形态：")
for k, v in full.most_common():
    print("   %3d  %r" % (v, k))
print("\n间隔符后接非『贝』的其它专名（需人工确认不是主角）：")
for crc, s in lanc:
    print("   ", crc, "|", s)
