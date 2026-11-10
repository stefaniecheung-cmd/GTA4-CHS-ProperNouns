# -*- coding: utf-8 -*-
from PIL import Image

PNG = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work\v1_base.png"
im = Image.open(PNG).convert("RGBA")
a = im.split()[3]
W, H = im.size

# 找"宽扁"字形（"一" 形态）：宽>=45, 高<=18
print("搜索宽扁字形（可能是「一」/「—」/「￣」）...")
hits = []
for row in range(0, 56):
    y0 = 17 + row * 66
    for col in range(0, 64):
        x0 = col * 64
        bb = a.crop((x0, y0, x0 + 64, y0 + 64)).getbbox()
        if not bb:
            continue
        w = bb[2] - bb[0]
        h = bb[3] - bb[1]
        if w >= 44 and h <= 20:
            hits.append((row, col, w, h))
print("命中数", len(hits))
for h in hits[:30]:
    print("  row%2d col%2d  w=%d h=%d  => 若 row起点512: idx=%d" % (h[0], h[1], h[2], h[3], 512 + h[0] * 64 + h[1]))
