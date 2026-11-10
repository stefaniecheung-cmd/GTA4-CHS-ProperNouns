# -*- coding: utf-8 -*-
import struct
from PIL import Image

V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
CT = V1 + r"\plugins\GTA4.CHS\char_table.dat"
raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
print("v1.0 char_table 数量 =", n, "文件", len(raw), "期望", 4 + 4 * n)
bad = [i for i in range(1, n) if cps[i] <= cps[i - 1]]
print("非升序位置数 =", len(bad), bad[:10])
print("重复 =", n - len(set(cps)))

# 差集：v1 比原多哪些
P0 = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS\char_table.dat"
r0 = open(P0, "rb").read()
n0 = struct.unpack_from("<I", r0, 0)[0]
c0 = [struct.unpack_from("<I", r0, 4 + 4 * i)[0] for i in range(n0)]
s0, s1 = set(c0), set(cps)
add = sorted(s1 - s0)
rem = sorted(s0 - s1)
print("\n新增 %d 个: %s" % (len(add), "".join(chr(x) for x in add)))
print("消失 %d 个: %s" % (len(rem), "".join(chr(x) for x in rem)))

# 图集验证
PNG = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work\v1_base.png"
im = Image.open(PNG).convert("RGBA")
a = im.split()[3].load()
W, H = im.size
print("\n图集尺寸", im.size)


def bb(x0, y0, w=64, h=66):
    top = bot = left = right = None
    for y in range(y0, min(y0 + h, H)):
        for x in range(x0, min(x0 + w, W)):
            if a[x, y] > 40:
                if top is None:
                    top = y
                bot = y
                if left is None or x < left:
                    left = x
                if right is None or x > right:
                    right = x
    return None if top is None else (left, top, right, bot, right - left + 1, bot - top + 1)


print("== v1.0 图集按 y=17+row*66, x=col*64 验证 格 64x66 ==")
for idx in (0, 1, 64, 512, 1024, 200, 3579):
    row, col = idx // 64, idx % 64
    y0 = 17 + row * 66
    x0 = col * 64
    ch = chr(cps[idx])
    print("  idx%4d %r row%2d col%2d 区(%4d,%4d) bbox=%s" % (idx, ch, row, col, x0, y0, bb(x0, y0)))
