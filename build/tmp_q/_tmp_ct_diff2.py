# -*- coding: utf-8 -*-
import struct, io, csv
csv.field_size_limit(10**9)

Z = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"


def load(p):
    d = open(p, "rb").read()
    n = struct.unpack("<I", d[:4])[0]
    return set(struct.unpack("<I", d[4 + 4*i:8 + 4*i])[0] for i in range(n))


v1 = load(Z + r"\plugins\GTA4.CHS\char_table.dat")
print("v1.0 字表码点数:", len(v1))

B = r"C:\Game\gta4-chs\build"
used = set()
for ch in ("base", "TLAD", "TBoGT"):
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            used |= set(c for c in (r.get("text") or "") if ord(c) > 127)
print("我方用字种类:", len(used))

miss = set(ord(c) for c in used) - v1
print("v1.0 仍缺:", len(miss), "".join(chr(c) for c in sorted(miss)))

# 缺字涉及条目与次数
if miss:
    from collections import Counter
    cnt = Counter()
    rows = 0
    for ch in ("base", "TLAD", "TBoGT"):
        with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                t = r.get("text") or ""
                hit = [c for c in t if ord(c) in miss]
                if hit:
                    rows += 1
                    for c in hit:
                        cnt[c] += 1
    print("受影响条目:", rows, "总出现:", sum(cnt.values()))
    print("按次数:", [(c, n) for c, n in cnt.most_common(40)])
