# -*- coding: utf-8 -*-
from PIL import Image

W = r"C:\Game\gta4-chs\build\atlas_work"
im = Image.open(W + r"\atlas_base_px.png").convert("RGBA")
AL = im.split()[3].tobytes()
S, CELL = 4096, 66


def cell_metrics(i, cols, flip, TH):
    r, c = i // cols, i % cols
    x0 = c * CELL
    if flip:
        y0 = S - (r + 1) * CELL
    else:
        y0 = r * CELL
    if x0 + CELL > S or y0 < 0 or y0 + CELL > S:
        return None
    xs = [x for x in range(CELL) if any(AL[(y0 + y) * S + x0 + x] > TH for y in range(CELL))]
    ys = [y for y in range(CELL) if any(AL[(y0 + y) * S + x0 + x] > TH for x in range(CELL))]
    if not xs or not ys:
        return (0, 0, 0, 0)
    return (min(xs), max(xs) - min(xs) + 1, min(ys), max(ys) - min(ys) + 1)


EXPECT = list("—、。〇《》「」『』一丁七万丈三上下不与丐丑")
for TH in (120, 160, 200):
    for cols in (62,):
        for flip in (False, True):
            got = []
            for i in range(21):
                m = cell_metrics(i, cols, flip, TH)
                if m is None:
                    got.append("NA"); continue
                got.append("%s(w%d,h%d)" % (EXPECT[i] if i < len(EXPECT) else "?", m[1], m[3]))
            print("TH=%d cols=%d flip=%-5s %s" % (TH, cols, flip, " ".join(got)))
