# -*- coding: utf-8 -*-
import struct, io, csv
csv.field_size_limit(10**9)

Z = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
NEW = Z + r"\plugins\GTA4.CHS\char_table.dat"
OLD = Z + r"\_ORIGINAL_char_table.dat"


def load(p):
    d = open(p, "rb").read()
    n = struct.unpack("<I", d[:4])[0]
    cps = [struct.unpack("<I", d[4 + 4*i:8 + 4*i])[0] for i in range(n)]
    assert 4 + 4*n == len(d), (len(d), n)
    return cps


old = load(OLD)
new = load(NEW)
print("原版字表 %d 个，扩容后 %d 个，新增 %d" % (len(old), len(new), len(new) - len(old)))
add = [c for c in new if c not in set(old)]
print("新增字符:", "".join(chr(c) for c in add))
print("新增码点:", ["U+%04X" % c for c in add])
print("是否纯追加（旧序不变）:", new[:len(old)] == old)
if new[:len(old)] != old:
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b:
            print("  首个不一致位置", i, hex(a), hex(b)); break

# 我们的译文用字
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
used = set()
for ch in ("base", "TLAD", "TBoGT"):
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            used |= set(c for c in (r.get("text") or "") if ord(c) > 127)

has_new = used & set(new)
miss_new = used - set(new)
print("\n我方非 ASCII 用字 %d 种；补丁之补丁字表覆盖 %d 种；仍缺 %d 种" %
      (len(used), len(has_new), len(miss_new)))
print("仍缺:", "".join(sorted(miss_new)))
from collections import Counter
cnt = Counter()
for ch in ("base", "TLAD", "TBoGT"):
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for c in (r.get("text") or ""):
                if ord(c) > 127 and c in miss_new:
                    cnt[c] += 1
print("\n仍缺按次数:", [(c, n) for c, n in cnt.most_common()])
