# -*- coding: utf-8 -*-
import io, csv, re
csv.field_size_limit(10**9)
ZG = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\zh_global.tsv"

VAR = ["尼克", "尼科", "尼可", "Niko", "NICKO", "Nico",
       "罗曼", "羅曼", "Roman", "ROMAN", "罗曼表哥", "表哥"]
cnt = {v: 0 for v in VAR}
hit = []
with io.open(ZG, encoding="utf-8", newline="") as f:
    rd = csv.reader(f, delimiter="\t")
    next(rd, None)
    for p in rd:
        if len(p) < 2:
            continue
        z = p[1]
        for v in VAR:
            if v in z:
                cnt[v] += 1
        # 同时含中英
        if ("尼克" in z or "尼科" in z) and "Niko" in z:
            hit.append(p)
print("zh_global 各变体出现条数：")
for v in VAR:
    print("   %-10s %d" % (v, cnt[v]))
print("\n同一行内中英并存（尼克+Niko）:", len(hit))
for p in hit[:10]:
    print("   ", p[0], "|", p[1][:90])
