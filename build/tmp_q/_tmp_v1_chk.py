# -*- coding: utf-8 -*-
import struct
from PIL import Image

V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
PNG = r"C:\Game\gta4-chs\build\atlas_work\v1_base.png"
OUT = r"C:\Game\gta4-chs\build\atlas_work"

im = Image.open(PNG).convert("RGBA")
a = im.split()[3]


def strip(row, c0, count, scale, name):
    y0 = 17 + row * 66
    parts = []
    for i in range(count):
        col = c0 + i
        x0 = col * 64
        c = a.crop((x0, y0, x0 + 64, y0 + 66))
        parts.append(c)
    w = 64 * count
    canvas = Image.new("L", (w, 66), 0)
    for i, c in enumerate(parts):
        canvas.paste(c, (i * 64, 0))
    if scale > 1:
        canvas = canvas.resize((w * scale, 66 * scale), Image.NEAREST)
    p = OUT + "\\" + name
    canvas.save(p)
    print("saved", p, canvas.size)


strip(54, 0, 10, 2, "_chk_row54_a.png")     # idx3456.. 应含 饰饿饼饼...
strip(54, 40, 10, 2, "_chk_row54_b.png")    # 应含 高鬼...
strip(55, 48, 10, 2, "_chk_row55_c.png")    # 应为 龙龟！，－：；？Ａ～
strip(47, 56, 8, 2, "_chk_row47_d.png")     # idx3064.. 已画区末尾
