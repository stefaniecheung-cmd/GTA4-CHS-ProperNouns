# -*- coding: utf-8 -*-
from PIL import Image

W = r"C:\Game\gta4-chs\build\atlas_work"
im = Image.open(W + r"\atlas_base_px.png").convert("RGBA")
AL = im.split()[3].tobytes()
S, CELL = 4096, 66
TH = 150


def metrics(i, cols, ox, oy, flip):
    r, c = i // cols, i % cols
    x0 = ox + c * CELL
    y0 = (S - oy - (r + 1) * CELL) if flip else (oy + r * CELL)
    if x0 < 0 or y0 < 0 or x0 + CELL > S or y0 + CELL > S:
        return None
    xs = [x for x in range(CELL) if any(AL[(y0 + y) * S + x0 + x] > TH for y in range(CELL))]
    ys = [y for y in range(CELL) if any(AL[(y0 + y) * S + x0 + x] > TH for x in range(CELL))]
    if not xs or not ys:
        return (0, 0)
    return (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)


# 前 9 个应矮(h小)，第 10~20 应高(h大)
def score(cols, ox, oy, flip):
    hs = []
    for i in range(24):
        m = metrics(i, cols, ox, oy, flip)
        if m is None:
            return -1
        hs.append(m[1])
    low = sum(1 for h in hs[:9] if 4 <= h <= 45)
    high = sum(1 for h in hs[10:24] if h >= 50)
    return low * 2 + high


best = []
for flip in (False, True):
    for cols in (62, 63, 61):
        for ox in range(0, 8):
            for oy in range(0, 66):
                sc = score(cols, ox, oy, flip)
                if sc >= 18:
                    best.append((sc, flip, cols, ox, oy))
best.sort(reverse=True)
print("候选（得分>=18）:")
for b in best[:12]:
    print("  score=%d flip=%s cols=%d ox=%d oy=%d" % b)
if not best:
    print("无高分候选，最高分：")
    top = []
    for flip in (False, True):
        for cols in (62,):
            for ox in range(0, 8):
                for oy in range(0, 66):
                    top.append((score(cols, ox, oy, flip), flip, cols, ox, oy))
    top.sort(reverse=True)
    for t in top[:8]:
        print("  score=%d flip=%s cols=%d ox=%d oy=%d" % t)
