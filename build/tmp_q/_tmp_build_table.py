# -*- coding: utf-8 -*-
"""构建新 char_table.dat：旧表 3580 ∪ 44 新 CJK，升序去重，离线校验。"""
import os, csv, struct, sys

G = r"C:\Game\Grand Theft Auto IV"
DEP_TAB = os.path.join(G, "plugins", "GTA4.CHS", "char_table.dat")
MAN = os.path.join(G, "gta4-chs", "build", "font_work", "render_manifest.tsv")
OUT = os.path.join(G, "gta4-chs", "build", "font_work", "char_table_new.dat")

# 旧表
b = open(DEP_TAB, "rb").read()
n = struct.unpack("<I", b[:4])[0]
old = list(struct.unpack("<%dI" % n, b[4:4+n*4]))
print("旧表条目:", n, "升序:", old == sorted(old), "重复:", len(old)-len(set(old)))

# 新字码点
new = []
with open(MAN, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        new.append(int(r["码位"].replace("U+",""), 16))
print("新字:", len(new), "已在旧表:", [hex(c) for c in new if c in set(old)])

merged = sorted(set(old) | set(new))
print("合并后:", len(merged), "升序:", merged == sorted(merged),
      "重复:", len(merged)-len(set(merged)))
print("旧字全保留:", set(old) <= set(merged))
print("新字全纳入:", set(new) <= set(merged))

# 写表
out = struct.pack("<I", len(merged)) + b"".join(struct.pack("<I", c) for c in merged)
open(OUT, "wb").write(out)
print("写出:", OUT, len(out), "B  预期:", 4+len(merged)*4)

# 校验回读
b2 = open(OUT, "rb").read()
n2 = struct.unpack("<I", b2[:4])[0]
cps2 = list(struct.unpack("<%dI" % n2, b2[4:4+n2*4]))
print("回读:", n2, "一致:", cps2 == merged)
