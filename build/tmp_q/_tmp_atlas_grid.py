# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw

W = r"C:\Game\gta4-chs\build\atlas_work"
im = Image.open(W + r"\atlas_base_px.png").convert("RGBA")
bg = Image.new("RGBA", im.size, (0, 0, 0, 255)); bg.alpha_composite(im)
rgb = bg.convert("RGB")

for name, cell, ox, oy in (("g66_0_0", 66, 0, 0), ("g66_2_17", 66, 2, 17)):
    cp = rgb.copy()
    d = ImageDraw.Draw(cp)
    x = ox
    while x < 4096:
        d.line([(x, 0), (x, 4095)], fill=(255, 60, 60), width=1)
        x += cell
    y = oy
    while y < 4096:
        d.line([(0, y), (4095, y)], fill=(60, 255, 60), width=1)
        y += cell
    cp.crop((0, 0, 1320, 1320)).resize((990, 990), Image.LANCZOS).save(os.path.join(W, f"grid_{name}.png"))
    print("写出 grid_" + name)
