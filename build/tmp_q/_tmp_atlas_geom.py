# -*- coding: utf-8 -*-
from PIL import Image

W = r"C:\Game\gta4-chs\build\atlas_work"
im = Image.open(W + r"\atlas_base_px.png").convert("RGBA")
AL = im.split()[3].tobytes()
S = 4096


def rowcount(y):
    seg = AL[y * S:(y + 1) * S]
    # 统计 > 8 的个数
    return sum(1 for b in seg if b > 8)


row = [rowcount(y) for y in range(S)]
print("非空行总数:", sum(1 for v in row if v))

bands = []
inb = False
for y in range(S):
    busy = row[y] > 0
    if busy and not inb:
        s = y; inb = True
    elif not busy and inb:
        bands.append((s, y - 1)); inb = False
if inb:
    bands.append((s, S - 1))
print("文本行带数量:", len(bands))
print("前 10:", bands[:10])
print("末 8:", bands[-8:])
hs = [b - a0 + 1 for a0, b in bands]
from collections import Counter
print("带高度众数:", Counter(hs).most_common(8))
dif = [bands[i + 1][0] - bands[i][0] for i in range(len(bands) - 1)]
print("相邻起点间距众数:", Counter(dif).most_common(8))
print("带起点列表（前 40）:", [b[0] for b in bands[:40]])

# 水平方向：在第一条带内数列
if bands:
    y0, y1 = bands[0]
    cols = []
    for x in range(S):
        c = 0
        for y in range(y0, y1 + 1):
            if AL[y * S + x] > 8:
                c += 1
        cols.append(c)
    blanks = [x for x in range(S) if cols[x] == 0]
    # 连续空列区间
    segs = []
    s = None
    for x in range(S):
        if cols[x] == 0:
            if s is None:
                s = x
        else:
            if s is not None:
                segs.append((s, x - 1)); s = None
    if s is not None:
        segs.append((s, S - 1))
    print("\n第一条带内空列段数:", len(segs))
    print("空列段前 20:", segs[:20])
    widths = [b - a0 + 1 for a0, b in segs]
    print("空列宽众数:", Counter(widths).most_common(6))
    # 字符块宽度
    blocks = []
    s = None
    for x in range(S):
        if cols[x] > 0:
            if s is None:
                s = x
        else:
            if s is not None:
                blocks.append((s, x - 1)); s = None
    if s is not None:
        blocks.append((s, S - 1))
    print("字符块数:", len(blocks))
    print("块宽前 30:", [b - a0 + 1 for a0, b in blocks[:30]])
    print("块起点前 30:", [a0 for a0, b in blocks[:30]])
    gaps = [blocks[i + 1][0] - blocks[i][0] for i in range(len(blocks) - 1)]
    print("块起点间距众数:", Counter(gaps).most_common(6))
