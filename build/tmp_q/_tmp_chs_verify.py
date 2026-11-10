# -*- coding: utf-8 -*-
import struct, os
from PIL import Image

CT = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS\char_table.dat"
raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
print("char_table 数量 =", n, " 文件大小", len(raw), " 期望", 4 + 4 * n)

bad = [(i, cps[i - 1], cps[i]) for i in range(1, n) if cps[i] <= cps[i - 1]]
print("非升序位置数 =", len(bad))
for b in bad[:10]:
    print("   idx %d: 0x%04X -> 0x%04X  (%r -> %r)" % (b[0], b[1], b[2], chr(b[1]), chr(b[2])))

print("前 20:", [chr(c) for c in cps[:20]])
print("后 20:", [chr(c) for c in cps[-20:]])
print("最小/最大码点: 0x%04X / 0x%04X" % (min(cps), max(cps)))
dup = n - len(set(cps))
print("重复码点数 =", dup)

# 图集验证：用原版补丁图集
PNG = r"C:\Game\gta4-chs\build\atlas_work\atlas_base_px.png"
im = Image.open(PNG).convert("RGBA")
a = im.split()[3]
W, H = im.size
px = a.load()


def cellbbox(x0, y0, w=64, h=90):
    top = bot = left = right = None
    for y in range(y0, min(y0 + h, H)):
        for x in range(x0, min(x0 + w, W)):
            if px[x, y] > 40:
                if top is None:
                    top = y
                bot = y
                if left is None or x < left:
                    left = x
                if right is None or x > right:
                    right = x
    if top is None:
        return None
    return (left, top, right, bot, right - left + 1, bot - top + 1)


print("\n== 验证：假设 y0 = 17 + row*66, x0 = col*64 ==")
for idx in (0, 1, 64, 512, 513, 1024, 3580 - 64, 3579):
    row, col = idx // 64, idx % 64
    y0 = 17 + row * 66
    x0 = col * 64
    bb = cellbbox(x0, y0)
    ch = chr(cps[idx]) if idx < n else "?"
    print("  idx%4d %r  row%2d col%2d  区(0x%04X,0x%04X) bbox=%s" % (idx, ch, row, col, x0, y0, bb))
