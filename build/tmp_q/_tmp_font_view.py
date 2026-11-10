# -*- coding: utf-8 -*-
from PIL import Image

OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"
for n in ("p0_font1", "p0_font2"):
    im = Image.open(OUT + "\\" + n + ".png").convert("RGBA")
    a = im.split()[3]
    # 只看左上 512x256 区域放大 2x
    crop = a.crop((0, 0, 512, 256)).resize((1024, 512), Image.NEAREST)
    crop.save(OUT + "\\" + n + "_a.png")
    # 全图缩略 700
    a.resize((700, 700), Image.LANCZOS).save(OUT + "\\" + n + "_s.png")
    print("ok", n, a.getextrema())
