# -*- coding: utf-8 -*-
from PIL import Image

PNG = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work\atlas_base_px.png"
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"

im = Image.open(PNG).convert("RGBA")
a = im.split()[3]


def strip(row, c0, count, scale, name):
    y0 = 17 + row * 66
    w = 64 * count
    canvas = Image.new("L", (w, 66), 0)
    for i in range(count):
        col = c0 + i
        x0 = col * 64
        canvas.paste(a.crop((x0, y0, x0 + 64, y0 + 66)), (i * 64, 0))
    if scale > 1:
        canvas = canvas.resize((w * scale, 66 * scale), Image.NEAREST)
    p = OUT + "\\" + name
    canvas.save(p)
    print("saved", p, canvas.size)


strip(46, 56, 8, 2, "_chk_p0_r46_end.png")   # 原版 idx3000..3007 应有字
strip(47, 0, 10, 2, "_chk_p0_r47.png")       # 原版 idx3008 应有 跋
strip(53, 40, 10, 2, "_chk_p0_r53.png")      # 原版 idx3432.. 应有 高鬼骑...
strip(54, 0, 10, 2, "_chk_p0_r54.png")       # 原版 idx3456 _
