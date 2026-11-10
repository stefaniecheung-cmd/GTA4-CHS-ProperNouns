# -*- coding: utf-8 -*-
import io, csv, re, struct, sys
from collections import Counter
csv.field_size_limit(10**9)

CT = r"C:\Users\yy253\Desktop\GTA4汉化补丁2026-11-09\release\plugins\GTA4.CHS\char_table.dat"
B = r"C:\Game\gta4-chs\build"

data = open(CT, "rb").read()
n = struct.unpack("<I", data[:4])[0]
cps = [struct.unpack("<I", data[4 + i*4:8 + i*4])[0] for i in range(n)]
print("char_table 条目数:", n, "文件大小:", len(data), "校验:", 4 + 4*n)
chars = set(chr(c) for c in cps if c < 0x110000)
print("前 30 个码点字符:", "".join(chr(c) for c in cps[:30]))
print("末尾 30 个:", "".join(chr(c) for c in cps[-30:]))
print("非 ASCII 字符数:", sum(1 for c in chars if ord(c) > 127))

# 扫我们三章译文用字
use = Counter()
where = {}
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            for c in t:
                if ord(c) > 127:
                    use[c] += 1
                    if c not in where:
                        where[c] = (ch, r.get("table"), r.get("crc"), t[:70])

print("\n译文用到的非 ASCII 字符种类:", len(use))

miss = {c: n for c, n in use.items() if c not in chars}
print("其中不在 char_table 的:", len(miss), "总出现次数:", sum(miss.values()))
print("\n=== 缺字清单（按出现次数降序）===")
for c, cnt in sorted(miss.items(), key=lambda x: -x[1]):
    info = where.get(c, ())
    print("  %r U+%04X 出现%3d次  首见: %s" % (c, ord(c), cnt, info))
