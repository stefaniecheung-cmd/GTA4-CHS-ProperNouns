# -*- coding: utf-8 -*-
from PIL import Image

W = r"C:\Game\gta4-chs\build\atlas_work"
S = 4096

old = Image.open(W + r"\atlas_base_px.png").convert("RGBA").split()[3].tobytes()
new = Image.open(W + r"\v1_base.png").convert("RGBA").split()[3].tobytes()

row_new = []
for y in range(S):
    o = old[y * S:(y + 1) * S]
    n = new[y * S:(y + 1) * S]
    cnt = sum(1 for i in range(S) if n[i] > 150 and o[i] <= 60)
    row_new.append(cnt)

# 找新增行段
segs = []
s = None
for y in range(S):
    if row_new[y] > 10:
        if s is None:
            s = y
    else:
        if s is not None:
            segs.append((s, y - 1, sum(row_new[s:y]))); s = None
if s is not None:
    segs.append((s, S - 1, sum(row_new[s:])))

print("新增像素所在行段（阈值>10像素/行）:")
for a, b, c in segs:
    print("   y %d..%d  高%d  像素%d" % (a, b, b - a + 1, c))
print("总新增像素:", sum(row_new))
