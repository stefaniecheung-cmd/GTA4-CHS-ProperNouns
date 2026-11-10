# -*- coding: utf-8 -*-
import struct, os, sys, collections
CT = r"C:\Game\Grand Theft Auto IV\plugins\GTA4.CHS\char_table.dat"
data = open(CT, "rb").read()
n = struct.unpack("<I", data[:4])[0]
cps = [struct.unpack("<I", data[4+i*4:8+i*4])[0] for i in range(n)]
print("条目:", n, " 格上限 64*62 =", 64*62)

def zone(c):
    if c < 0x80: return "ASCII"
    if c < 0x100: return "Latin-1"
    if 0x4E00 <= c <= 0x9FFF: return "CJK"
    if 0x3000 <= c <= 0x303F: return "CJK标点"
    if 0xFF00 <= c <= 0xFFEF: return "全角"
    if 0x2000 <= c <= 0x206F: return "通用标点"
    return "其它"

zc = collections.Counter(zone(c) for c in cps)
print("分区:", dict(zc))

# 找各分区起始索引
seen = {}
for i, c in enumerate(cps):
    z = zone(c)
    if z not in seen: seen[z] = (i, c)
for z, (i, c) in seen.items():
    print(f"  {z}: 起始索引 {i} 首个码位 U+{c:04X}")

# 前 512 项码位范围
print("\n前 512 项: 最小 U+%04X 最大 U+%04X" % (min(cps[:512]), max(cps[:512])))
print("前 512 项分区:", dict(collections.Counter(zone(c) for c in cps[:512])))
# 512 之后
print("512 之后分区:", dict(collections.Counter(zone(c) for c in cps[512:])))

# 目标新字在排序位的落点（假设插入）
targets = "厩唠啵喏嘀噗囔墩姘娄岬惭抡拣捋撬撵擞槌沤泞渥璀璨疵瘀瘆砌砺簸粝纭肏肓芋蔓虱辄遢邋酝钾韧颚髋"
print("\n新字排序落点（在现有表中的插入位置）:")
for ch in targets:
    o = ord(ch)
    # 二分插入位
    lo, hi = 0, n
    while lo < hi:
        mid = (lo+hi)//2
        if cps[mid] < o: lo = mid+1
        else: hi = mid
    ins = lo
    print(f"  {ch} U+{o:04X} 插入位 idx={ins}  {'<== 前512' if ins<512 else ''}")
