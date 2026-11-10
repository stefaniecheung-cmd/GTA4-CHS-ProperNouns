# -*- coding: utf-8 -*-
import struct, io, os, sys

sys.path.insert(0, r"C:\Game\_tools")

V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
CT = V1 + r"\plugins\GTA4.CHS\char_table.dat"
raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
idx_of = {chr(c): i for i, c in enumerate(cps)}

BUILD = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
GXTS = ["zchs_base_tr.gxt", "zchs_TLAD_tr.gxt", "zchs_TBoGT_tr.gxt"]

try:
    from gxt_extract import parse_gxt
except Exception as e:
    print("导入 gxt_extract 失败:", e)
    raise


def texts(path):
    res = parse_gxt(path)
    if isinstance(res, tuple) and len(res) == 2:
        tables, items = res
    else:
        tables, items = res, []
    out = []
    for it in items:
        # items: (table, crc, text)
        if len(it) >= 3:
            out.append(it[2])
    return out


allchar = {}
where = {}
for g in GXTS:
    p = os.path.join(BUILD, g)
    ts = texts(p)
    print("%-16s 条目 %d" % (g, len(ts)))
    for t in ts:
        for ch in t:
            if ord(ch) < 128:
                continue
            allchar[ch] = allchar.get(ch, 0) + 1
            where.setdefault(ch, set()).add(g)

print("\n我方三章译文非 ASCII 字符种数 =", len(allchar))
print("总出现次数 =", sum(allchar.values()))

missing = [c for c in allchar if c not in idx_of]
covered = [c for c in allchar if c in idx_of]
late = [c for c in covered if idx_of[c] >= 3456]
early = [c for c in covered if idx_of[c] < 3456]

print("\n== 覆盖分析（对照 v1.0 字表 3,580 / 图集实画 3,068 格 / 行54起ASCII） ==")
print("  完全不在字表      : %d 种 / 出现 %d 次" % (len(missing), sum(allchar[c] for c in missing)))
print("  在字表且 idx<3068 (有字形): %d 种 / 出现 %d 次" % (len(early), sum(allchar[c] for c in early)))
print("  在字表但 idx>=3068(图集空格区或ASCII区): %d 种 / 出现 %d 次" % (len(late), sum(allchar[c] for c in late)))

print("\n-- 缺失(不在字表)清单 --")
ms = sorted(missing, key=lambda c: -allchar[c])
for c in ms:
    print("   %r U+%04X  %d 次  %s" % (c, ord(c), allchar[c], ",".join(sorted(where[c]))))

print("\n-- idx>=3068 的(chars in table but glyph slot beyond painted area) --")
for c in sorted(late, key=lambda c: -allchar[c])[:40]:
    print("   %r U+%04X idx=%d row=%d col=%d %d次 %s" % (c, ord(c), idx_of[c], idx_of[c] // 64, idx_of[c] % 64, allchar[c], ",".join(sorted(where[c]))))
