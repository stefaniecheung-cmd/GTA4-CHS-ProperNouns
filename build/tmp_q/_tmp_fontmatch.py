# -*- coding: utf-8 -*-
import struct
from PIL import Image, ImageDraw, ImageFont

V1 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
CT = V1 + r"\plugins\GTA4.CHS\char_table.dat"
PNG = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work\v1_base.png"
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"

raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
im = Image.open(PNG).convert("RGBA")
a = im.split()[3]

CAND = [
    ("msyhbd", r"C:\Windows\Fonts\msyhbd.ttc", 0),
    ("msyh", r"C:\Windows\Fonts\msyh.ttc", 0),
    ("simhei", r"C:\Windows\Fonts\simhei.ttf", 0),
    ("Dengb", r"C:\Windows\Fonts\Dengb.ttf", 0),
    ("NotoSansSC", r"C:\Windows\Fonts\NotoSansSC-VF.ttf", 0),
]

TEST = ["吸", "幻", "容", "歇", "口", "啊"]


def cellmask(ch):
    idx = cps.index(ord(ch))
    row, col = idx // 64, idx % 64
    y0, x0 = 17 + row * 66, col * 64
    c = a.crop((x0, y0, x0 + 64, y0 + 66))
    bb = c.getbbox()
    return c.crop(bb), bb


def score(cell, font, ch):
    # 在 64x64 里按 bbox 高缩放渲染，再与 cell 逐像素比对（均缩放至 48x48）
    img = Image.new("L", (96, 96), 0)
    dr = ImageDraw.Draw(img)
    dr.text((8, 4), ch, font=font, fill=255)
    bb = img.getbbox()
    if not bb:
        return -1
    t = img.crop(bb).resize((48, 48), Image.LANCZOS)
    s = cell.resize((48, 48), Image.LANCZOS)
    tp = t.load()
    sp = s.load()
    inter = union = 0
    for y in range(48):
        for x in range(48):
            p1 = tp[x, y] > 100
            p2 = sp[x, y] > 100
            if p1 or p2:
                union += 1
                if p1 and p2:
                    inter += 1
    return inter / union if union else -1


print("字   " + "  ".join("%-11s" % c[0] for c in CAND))
tot = {c[0]: 0 for c in CAND}
for ch in TEST:
    cell, bb = cellmask(ch)
    if bb is None:
        print(ch, "无字形")
        continue
    line = "%-3s " % ch
    for name, path, idxf in CAND:
        f = ImageFont.truetype(path, 72, index=idxf)
        v = score(cell, f, ch)
        tot[name] += v
        line += "  %-11.4f" % v
    print(line)
print("\n平均 IoU:")
for k, v in sorted(tot.items(), key=lambda p: -p[1]):
    print("  %-12s %.4f" % (k, v / len(TEST)))
