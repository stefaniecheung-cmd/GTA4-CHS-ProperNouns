# -*- coding: utf-8 -*-
from PIL import Image

PNG = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work\v1_base.png"
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"
im = Image.open(PNG).convert("RGBA")
a = im.split()[3]

def strip(row, c0, count, scale, name, yoff=17, pitch=66, cell=64):
    y0 = yoff + row * pitch
    w = cell * count
    canvas = Image.new("L", (w, cell), 0)
    for i in range(count):
        col = c0 + i
        x0 = col * cell
        canvas.paste(a.crop((x0, y0, x0 + cell, y0 + cell)), (i * cell, 0))
    if scale > 1:
        canvas = canvas.resize((w * scale, cell * scale), Image.NEAREST)
    p = OUT + "\\" + name
    canvas.save(p)
    print("saved", p, canvas.size)

strip(0, 0, 12, 2, "_v1_r0_a.png")
strip(1, 0, 12, 2, "_v1_r1_a.png")
strip(8, 0, 12, 2, "_v1_r8_a.png")
strip(16, 0, 12, 2, "_v1_r16_a.png")
