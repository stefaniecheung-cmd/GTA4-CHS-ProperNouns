# -*- coding: utf-8 -*-
from PIL import Image

W = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"
S, CELL, OX, OY0, COLS = 4096, 66, 0, 11, 62
im = Image.open(W + r"\v1_base.png").convert("RGBA")
AL = im.split()[3].tobytes()
TH = 150

rows = []
total = 0
for r in range(62):
    y0 = OY0 + r * CELL
    if y0 + CELL > S:
        rows.append(None); continue
    n = 0
    for c in range(COLS):
        x0 = OX + c * CELL
        if x0 + CELL > S:
            continue
        hit = False
        for y in range(CELL):
            base = (y0 + y) * S + x0
            seg = AL[base:base + CELL]
            if any(b > TH for b in seg):
                hit = True
                break
        if hit:
            n += 1
    rows.append(n)
    total += n

for r, n in enumerate(rows):
    if n is None:
        print("行 %2d (y0=%d)  超出" % (r, OY0 + r * CELL))
    else:
        print("行 %2d (y0=%4d)  非空 %2d/62 %s" % (r, OY0 + r * CELL, n, "★空" if n == 0 else ""))
print("\n合计非空格:", total)
print("v1.0 字表数:", 3580, "差:", 3580 - total)
