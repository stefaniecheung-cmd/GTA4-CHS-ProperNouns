# -*- coding: utf-8 -*-
"""基于定稿 gxt 全量文本，对部署 char_table.dat 求缺字差集。"""
import io, os, sys, struct, csv, collections, re
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
B = os.path.join(G, "gta4-chs", "build")
CT = os.path.join(G, "plugins", "GTA4.CHS", "char_table.dat")
OUT = os.path.join(B, "cmp_assets")

# 字表现有码点
data = open(CT, "rb").read()
n = struct.unpack("<I", data[:4])[0]
cps = [struct.unpack("<I", data[4+i*4:8+i*4])[0] for i in range(n)]
have = set(cps)
print("char_table 条目:", n, "文件:", len(data), "校验:", 4+4*n)
# 升序检查
print("升序:", cps == sorted(cps), " 重复:", len(cps)-len(have))

use = collections.Counter()
where = {}
for ch, fn in [("base","zchs_base_tr.gxt"),("TLAD","zchs_TLAD_tr.gxt"),("TBoGT","zchs_TBoGT_tr.gxt")]:
    _, es = parse_gxt(os.path.join(B, fn))
    for t, c, x in es:
        for ch_ in x:
            o = ord(ch_)
            if o > 127:
                use[ch_] += 1
                if ch_ not in where:
                    where[ch_] = (ch, t, "%08X"%c, x[:60])

miss = {c: k for c, k in use.items() if ord(c) not in have}
def cat(c):
    o = ord(c)
    if 0x4E00 <= o <= 0x9FFF: return "CJK"
    if 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF: return "标点/全角"
    if o in (0x2122,0x00AE,0x00A9,0x00AC): return "符号"
    if o >= 0x80: return "拉丁重音/其它"
    return "其它"

groups = collections.defaultdict(list)
for c, k in sorted(miss.items(), key=lambda x:-x[1]):
    groups[cat(c)].append((c, k, where[c]))

print("\n译文非 ASCII 种类:", len(use), " 缺字:", len(miss), " 缺字出现总次数:", sum(miss.values()))
for g, items in groups.items():
    print(f"\n=== {g}  {len(items)} 字 ===")
    for c, k, info in items:
        print("  %r U+%04X x%d  %s" % (c, ord(c), k, info))

with io.open(os.path.join(OUT, "缺字清单_最新.tsv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["字符","码位","类别","出现次数","章节","表","CRC","首见文本"])
    for g, items in groups.items():
        for c, k, info in items:
            w.writerow([c, "U+%04X"%ord(c), g, k, info[0], info[1], info[2], info[3]])
