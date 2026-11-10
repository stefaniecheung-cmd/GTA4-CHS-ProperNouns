# -*- coding: utf-8 -*-
from PIL import Image

W = r"C:\Game\gta4-chs\build\atlas_work"
S, CELL, OX, OY0, COLS = 4096, 66, 0, 11, 62
im = Image.open(W + r"\v1_base.png").convert("RGBA")
AL = im.split()[3].tobytes()
TH = 150


def row_summary(r):
    y0 = OY0 + r * CELL
    out = []
    for c in range(COLS):
        x0 = OX + c * CELL
        if y0 + CELL > S:
            out.append("OUT")
            continue
        xs = [x for x in range(CELL) if any(AL[(y0 + y) * S + x0 + x] > TH for y in range(CELL))]
        ys = [y for y in range(CELL) if any(AL[(y0 + y) * S + x0 + x] > TH for x in range(CELL))]
        if not xs or not ys:
            out.append("EMPTY")
        else:
            out.append("w%d,h%d" % (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
    return out


for r in (47, 48, 49, 50, 51, 52, 57, 58):
    s = row_summary(r)
    nonEmpty = sum(1 for v in s if v not in ("EMPTY", "OUT"))
    print("行 %d (y0=%d) 非空 %d 格；前 12:" % (r, OY0 + r * CELL, nonEmpty), s[:12])
