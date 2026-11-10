# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw

W = r"C:\Game\gta4-chs\build\atlas_work"
im = Image.open(W + r"\atlas_base_px.png").convert("RGBA")
bg = Image.new("RGBA", im.size, (0, 0, 0, 255)); bg.alpha_composite(im)
rgb = bg.convert("RGB")

# 底部 1320 高
bot = rgb.crop((0, 4096 - 1320, 1320, 4096))
d = ImageDraw.Draw(bot)
x = 0
while x < 1320:
    d.line([(x, 0), (x, 1319)], fill=(255, 60, 60), width=1); x += 66
y = 0
while y < 1320:
    d.line([(0, y), (1319, y)], fill=(60, 255, 60), width=1); y += 66
bot.resize((990, 990), Image.LANCZOS).save(os.path.join(W, "grid_bottom.png"))
print("写出 grid_bottom.png")

# 也翻转后看顶部 20 行
flip = rgb.transpose(Image.FLIP_TOP_BOTTOM)
t = flip.crop((0, 0, 1320, 1320))
d2 = ImageDraw.Draw(t)
x = 0
while x < 1320:
    d2.line([(x, 0), (x, 1319)], fill=(255, 60, 60), width=1); x += 66
y = 0
while y < 1320:
    d2.line([(0, y), (1319, y)], fill=(60, 255, 60), width=1); y += 66
t.resize((990, 990), Image.LANCZOS).save(os.path.join(W, "grid_flip_top.png"))
print("写出 grid_flip_top.png")
