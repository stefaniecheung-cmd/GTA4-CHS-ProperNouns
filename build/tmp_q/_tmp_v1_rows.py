# -*- coding: utf-8 -*-
import struct
from PIL import Image

V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
PNG = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work\v1_base.png"
CT = V1 + r"\plugins\GTA4.CHS\char_table.dat"

raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]

im = Image.open(PNG).convert("RGBA")
a = im.split()[3].load()
W, H = im.size


def cellstat(row, col):
    y0 = 17 + row * 66
    x0 = col * 64
    top = bot = left = right = None
    for y in range(y0, min(y0 + 66, H)):
        for x in range(x0, min(x0 + 64, W)):
            if a[x, y] > 40:
                if top is None:
                    top = y
                bot = y
                if left is None or x < left:
                    left = x
                if right is None or x > right:
                    right = x
    if top is None:
        return None
    return (left - x0, top - y0, bot - top + 1, right - left + 1)


print("总字数", n, "-> 行数", (n + 63) // 64)
print("\n行号 | 该行首字索引 | 首字 | 首格(top,h,w) | 该行非空格数")
for row in range(0, 61):
    base = row * 64
    c0 = chr(cps[base]) if base < n else "-"
    s0 = cellstat(row, 0)
    cnt = 0
    for col in range(64):
        if cellstat(row, col):
            cnt += 1
    if row <= 56:
        print(" %2d  | %5d | %r | %s | %d/64" % (row, base, c0, s0, cnt))
    else:
        print(" %2d  |  ---  |  -  | %s | %d/64" % (row, s0, cnt))
