# -*- coding: utf-8 -*-
import struct, zlib, hashlib, io, sys, collections, bisect
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
CT = V1 + r"\plugins\GTA4.CHS\char_table.dat"

RARE = list("厩唠啵喏嘀噗囔墩姘娄岬惭抡拣捋撬撵擞槌沤泞渥璀璨疵瘀瘆砌砺簸粝纭肏肓芋蔓虱辄遢邋酝钾韧颚髋")

raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4*i)[0] for i in range(n)]
print("v1 表项数", n, "最大码点 U+%04X" % cps[-1])
print("升序:", all(cps[i] < cps[i+1] for i in range(n-1)))
idx_of = {c: i for i, c in enumerate(cps)}

# 我方 gxt 次数
cnt = collections.Counter()
for ch, f in (("base", "zchs_base_tr.gxt"), ("TLAD", "zchs_TLAD_tr.gxt"), ("TBoGT", "zchs_TBoGT_tr.gxt")):
    _, items = parse_gxt(G + "\\gta4-chs\\build\\" + f)
    for _, _, t in items:
        for c in t:
            if c in RARE:
                cnt[c] += 1

print("\n=== 45 字核查（码点 / 插入后idx / 落点行 / 我方次数）===")
in_low, in_miss = [], []
for c in RARE:
    cp = ord(c)
    i = idx_of.get(cp)
    pos = bisect.bisect_left(cps, cp)
    row = (pos - 512) // 64 if pos >= 512 else -1
    tag = "已有" if i is not None else ("无位图区(idx<512)" if pos < 512 else "可画位图 row%d" % row)
    if i is None:
        in_miss.append(c)
        if pos < 512:
            in_low.append(c)
    print("  %s U+%04X  新idx=%-5d row=%-3d 我方%4d  %s" % (c, cp, pos, row, cnt[c], tag))

print("\n缺失:", "".join(in_miss), "共", len(in_miss))
print("落入无位图区:", "".join(in_low), "共", len(in_low))
print("我方 44 字总次数:", sum(cnt.values()))

# 三章 font_chs 段是否同构
print("\n=== 三章图集 font_chs 段比对 ===")
paths = {
    "pc":   "update\\pc\\textures\\fonts.wtd",
    "TLAD": "update\\TLAD\\pc\\textures\\fonts.wtd",
    "TBoGT":"update\\TBoGT\\pc\\textures\\fonts.wtd",
}
for ch, rel in paths.items():
    p = V1 + "\\" + rel
    b = zlib.decompress(open(p, "rb").read()[0xC:])
    chs = b[-16_777_216:]
    print("  %-6s 解压%10d  font_chs md5 %s" % (ch, len(b), hashlib.md5(chs).hexdigest()[:12]))
