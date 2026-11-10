# -*- coding: utf-8 -*-
import os
from PIL import Image

W = r"C:\Game\gta4-chs\build\atlas_work"
im = Image.open(W + r"\atlas_base_px.png").convert("RGBA")
bg = Image.new("RGBA", im.size, (0, 0, 0, 255)); bg.alpha_composite(im)
rgb = bg.convert("RGB")

EXPECT = "—、。〇《》「」『』一丁七万丈三上下不与丐丑专且世丘丙业丛东丝丢两严丧个"
print("期望前 30:", EXPECT[:30])

CANDS = [
    ("c66x62_2_17", 66, 62, 2, 17),
    ("c66x62_0_0", 66, 62, 0, 0),
    ("c66x62_2_0", 66, 62, 2, 0),
    ("c64x64_0_0", 64, 64, 0, 0),
    ("c66x62_0_17", 66, 62, 0, 17),
]
for name, cell, cols, ox, oy in CANDS:
    n, m = 15, 2
    strip = Image.new("RGB", (n * cell, m * cell), (0, 0, 0))
    for k in range(n * m):
        r, c = k // n, k % n
        x0 = ox + c * cell
        y0 = oy + (r) * cell
        if x0 + cell > rgb.width or y0 + cell > rgb.height:
            continue
        strip.paste(rgb.crop((x0, y0, x0 + cell, y0 + cell)), (c * cell, r * cell))
    strip = strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST)
    out = os.path.join(W, f"strip_{name}.png")
    strip.save(out)
    print("写出", out)

# 用选定的格子去比对：把前 30 格与期望字逐格量化对比字形「笔画数」不可行，
# 改为直接输出每格的非空像素数，人工核对是否为 0（空格/标点）
