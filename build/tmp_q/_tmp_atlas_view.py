# -*- coding: utf-8 -*-
import os
from PIL import Image

W = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"

for ch in ("base", "TLAD", "TBoGT"):
    p = os.path.join(W, f"atlas_{ch}_px.png")
    im = Image.open(p)
    print(ch, "尺寸", im.size, "模式", im.mode)
    im2 = im.convert("RGBA")
    # 白字透明底 -> 黑底合成
    bg = Image.new("RGBA", im2.size, (0, 0, 0, 255))
    bg.alpha_composite(im2)
    rgb = bg.convert("RGB")
    rgb.resize((1024, 1024), Image.LANCZOS).save(os.path.join(W, f"view_{ch}.png"))
    # 左上 512x512 原尺寸裁切（看格子）
    rgb.crop((0, 0, 512, 512)).save(os.path.join(W, f"corner_{ch}.png"))
    print("  写出 view_/corner_", ch)
