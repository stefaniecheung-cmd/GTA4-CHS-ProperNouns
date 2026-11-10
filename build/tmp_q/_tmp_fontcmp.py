# -*- coding: utf-8 -*-
import struct
from PIL import Image, ImageDraw, ImageFont

V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
CT = V1 + r"\plugins\GTA4.CHS\char_table.dat"
PNG = r"C:\Game\gta4-chs\build\atlas_work\v1_base.png"
OUT = r"C:\Game\gta4-chs\build\atlas_work"

raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
im = Image.open(PNG).convert("RGBA")
a = im.split()[3]

FONTS = [("v1 atlas", None),
         ("msyhbd", r"C:\Windows\Fonts\msyhbd.ttc"),
         ("Dengb", r"C:\Windows\Fonts\Dengb.ttf"),
         ("simhei", r"C:\Windows\Fonts\simhei.ttf")]
TEST = ["吸", "幻", "容", "歇", "刺", "镖"]

S = 64
canvas = Image.new("L", (S * len(FONTS), S * len(TEST) + 20), 0)
dr = ImageDraw.Draw(canvas)
for r, ch in enumerate(TEST):
    idx = cps.index(ord(ch))
    row, col = idx // 64, idx % 64
    y0, x0 = 17 + row * 66, col * 64
    cell = a.crop((x0, y0, x0 + 64, y0 + 66)).resize((S, S))
    canvas.paste(cell, (0, r * S + 20))
    for c, (name, path) in enumerate(FONTS[1:], start=1):
        f = ImageFont.truetype(path, 58)
        img = Image.new("L", (96, 96), 0)
        d2 = ImageDraw.Draw(img)
        d2.text((10, 8), ch, font=f, fill=255)
        bb = img.getbbox()
        t = img.crop(bb)
        # 保持比例，缩到高 56
        hh = 56
        ww = int(t.width * hh / t.height)
        t = t.resize((ww, hh), Image.LANCZOS)
        canvas.paste(t, (c * S + (S - ww) // 2, r * S + 20 + (S - hh) // 2))

p = OUT + "\\_cmp_font.png"
canvas.save(p)
print("saved", p, canvas.size)
print("列顺序: " + " | ".join(f[0] for f in FONTS))
