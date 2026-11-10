# -*- coding: utf-8 -*-
import io, csv, re, struct
from collections import Counter, defaultdict
csv.field_size_limit(10**9)

CT = r"C:\Users\yy253\Desktop\GTA4汉化补丁2026-11-09\release\plugins\GTA4.CHS\char_table.dat"
data = open(CT, "rb").read()
n = struct.unpack("<I", data[:4])[0]
cps = set(struct.unpack("<I", data[4 + i*4:8 + i*4])[0] for i in range(n))

B = r"C:\Game\gta4-chs\build"
rows = []
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            miss = set(c for c in t if ord(c) > 127 and ord(c) not in cps)
            if miss:
                rows.append((ch, r.get("table"), r.get("crc"), t, miss))

print("含缺字的条目数:", len(rows))
print("按章:", Counter(r[0] for r in rows))

# 分成两类：只有 ･ ；还有别的缺字
only_dot = [r for r in rows if r[4] == {"･"}]
has_real = [r for r in rows if r[4] != {"･"}]
print("只含 ･ 缺字的条目:", len(only_dot))
print("还含其它缺字的条目:", len(has_real))

# 其它缺字频次
other = Counter()
for r in has_real:
    for c in r[4]:
        if c != "･":
            other[c] += 1
print("\n其它缺字（先按条目数）：", len(other), "种")
print("".join(sorted(other.keys(), key=lambda x: -other[x])))

print("\n=== 还含其它缺字的条目（逐条列出，最多 200）===")
for ch, tb, crc, t, miss in has_real[:200]:
    ms = "".join(sorted(c for c in miss if c != "･"))
    print("  [%s|%s|%s] 缺={%s} %s" % (ch, tb, crc, ms, t[:100]))
print("\n总计需改条目:", len(has_real), "（另有", len(only_dot), "条仅需去掉 ･）")
