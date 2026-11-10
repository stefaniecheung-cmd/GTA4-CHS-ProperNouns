# -*- coding: utf-8 -*-
import struct, sys, collections

sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

PATCH = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release"
CT = PATCH + r"\plugins\GTA4.CHS\char_table.dat"
MINE = [r"C:\Game\gta4-chs\build\zchs_base_tr.gxt",
        r"C:\Game\gta4-chs\build\zchs_TLAD_tr.gxt",
        r"C:\Game\gta4-chs\build\zchs_TBoGT_tr.gxt"]

raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
idx_of = {c: i for i, c in enumerate(cps)}
print("原版表项数", n)

cnt = collections.Counter()
for p in MINE:
    tables, items = parse_gxt(p)
    for tb, crc, t in items:
        for ch in t:
            if ord(ch) < 128:
                continue
            cnt[ch] += 1
print("我方非 ASCII 字符种类", len(cnt), "总次数", sum(cnt.values()))

buckets = {"不在表(无位置)": [], "在表 idx<512(无位图)": [], "在表 idx>=512(有位图)": []}
for ch, c in cnt.items():
    i = idx_of.get(ord(ch))
    if i is None:
        buckets["不在表(无位置)"].append((ch, c))
    elif i < 512:
        buckets["在表 idx<512(无位图)"].append((ch, c))
    else:
        buckets["在表 idx>=512(有位图)"].append((ch, c))

for k, v in buckets.items():
    print("\n%s: 种类 %d 次数 %d" % (k, len(v), sum(c for _, c in v)))
    v2 = sorted(v, key=lambda p: -p[1])
    print("  " + " ".join("%s%d" % (ch, c) for ch, c in v2[:60]))

# 中文生僻字 vs 非中文
def is_cjk(ch):
    return 0x4E00 <= ord(ch) <= 0x9FFF
miss = buckets["不在表(无位置)"]
cjk_new = [(ch, c) for ch, c in miss if is_cjk(ch)]
other_new = [(ch, c) for ch, c in miss if not is_cjk(ch)]
print("\n缺字中 中文 %d 种 / 非中文 %d 种" % (len(cjk_new), len(other_new)))
print("  中文: " + "".join(ch for ch, _ in sorted(cjk_new)))
print("  非中文: " + " ".join("%s(U+%04X)×%d" % (ch, ord(ch), c) for ch, c in sorted(other_new, key=lambda p: -p[1])))

# 扩容后的表容量核算
new_total = n + len(cjk_new)
print("\n扩容后表项数(只补中文) = %d" % new_total)
print("图集需画 idx 512..%d 共 %d 格 -> 需要 %d 行" % (new_total - 1, new_total - 512, (new_total - 512 + 63) // 64))
print("图集可用行 row0..53 = %d 格" % (54 * 64))
