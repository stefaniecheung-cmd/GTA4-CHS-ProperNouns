# -*- coding: utf-8 -*-
import struct

P0 = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS\char_table.dat"
V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0\plugins\GTA4.CHS\char_table.dat"


def load(p):
    raw = open(p, "rb").read()
    n = struct.unpack_from("<I", raw, 0)[0]
    return n, [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]


n0, c0 = load(P0)
n1, c1 = load(V1)
print("原版", n0, " v1.0", n1)

TARGETS = "高黑马鲁麻麦龄鬼骑驾馆骗鸡鱼黄首驶验骨骚饿香龙鼠魔黏饰鸽鹿鸣鸟鼓默饼"
print("\n%-3s %-6s %-8s %-8s %s" % ("字", "码点", "原版idx(row,col)", "v1idx(row,col)", "原版有字形?"))
for ch in TARGETS:
    cp = ord(ch)
    i0 = c0.index(cp) if cp in c0 else -1
    i1 = c1.index(cp) if cp in c1 else -1
    ok = "是" if 0 <= i0 < 3008 else ("否" if i0 >= 0 else "无此字")
    s0 = ("%d(%d,%d)" % (i0, i0 // 64, i0 % 64)) if i0 >= 0 else "-"
    s1 = ("%d(%d,%d)" % (i1, i1 // 64, i1 % 64)) if i1 >= 0 else "-"
    print("%-3s U+%04X %-14s %-14s %s" % (ch, cp, s0, s1, ok))

# 原版中落在 >=3008 的字符总数
late0 = [c for c in c0 if c0.index(c) >= 3008]
print("\n原版 idx>=3008 的字数 =", n0 - 3008)
print("原版 idx>=3456 的字数 =", n0 - 3456)
print("原版末 70 字:", "".join(chr(c) for c in c0[-70:]))
