# -*- coding: utf-8 -*-
import struct
from PIL import Image

P0 = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS\char_table.dat"
PNG = r"C:\Game\gta4-chs\build\atlas_work\atlas_base_px.png"

raw = open(P0, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
im = Image.open(PNG).convert("RGBA")
a = im.split()[3].load()
W, H = im.size
print("原版字数", n, "图集", im.size)


def cellstat(row, col):
    y0 = 17 + row * 66
    x0 = col * 64
    if y0 + 66 > H:
        return None
    top = bot = left = right = None
    for y in range(y0, y0 + 66):
        for x in range(x0, x0 + 64):
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
    return (top - y0, bot - top + 1, right - left + 1)


print("\n行 | 首索引 | 首字 | 首格(top,h,w) | 非空格数")
for row in range(40, 61):
    base = row * 64
    c0 = chr(cps[base]) if base < n else "-"
    s0 = cellstat(row, 0)
    cnt = sum(1 for col in range(64) if cellstat(row, col))
    print(" %2d | %5d | %r | %s | %d/64" % (row, base, c0, s0, cnt))
