# -*- coding: utf-8 -*-
from PIL import Image

W = r"C:\Game\gta4-chs\build\atlas_work"
S, CELL = 4096, 66
v1 = Image.open(W + r"\v1_base.png").convert("RGBA")
AL = v1.split()[3].tobytes()

# 统计 y 3110..3180 这一带，按 66 网格切有多少个字形
for oy in range(3100, 3130):
    for ox in (0, 2, 4):
        cells = []
        for c in range(70):
            x0 = ox + c * CELL
            if x0 + CELL > S:
                break
            xs = [x for x in range(CELL) if any(AL[(oy + y) * S + x0 + x] > 150 for y in range(CELL))]
            ys = [y for y in range(CELL) if any(AL[(oy + y) * S + x0 + x] > 150 for x in range(CELL))]
            if xs and ys:
                cells.append((c, max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
        if len(cells) >= 40:
            print("oy=%d ox=%d 有字形 %d 格，前 20:" % (oy, ox, len(cells)), cells[:20])
            break
    else:
        continue
    break

# 直接给出 3100-3200 每行像素数
print("\ny 3100..3200 每行 alpha>150 像素数:")
for y in range(3100, 3200, 4):
    seg = AL[y * S:(y + 1) * S]
    print("  y=%d  %d" % (y, sum(1 for b in seg if b > 150)))
