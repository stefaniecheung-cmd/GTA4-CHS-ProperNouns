# -*- coding: utf-8 -*-
import struct, sys
from PIL import Image

sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

PATCH = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release"
CT = PATCH + r"\plugins\GTA4.CHS\char_table.dat"
PNG = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work\_rel_pc.png"
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"

raw = open(CT, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
cps = [struct.unpack_from("<I", raw, 4 + 4 * i)[0] for i in range(n)]
idx_of = {c: i for i, c in enumerate(cps)}

im = Image.open(PNG).convert("RGBA")
a = im.split()[3]

# 取一句简短的中文
tables, items = parse_gxt(PATCH + r"\update\common\text\american.gxt")
cands = []
for tb, crc, t in items:
    s = t.strip()
    if 6 <= len(s) <= 14 and all(0x4e00 <= ord(c) <= 0x9fff or c in "，。？！" for c in s):
        cands.append(s)
    if len(cands) >= 3:
        break
print("测试文本:", cands)

for mode, name in (("asis", "按 asi 的 idx>>6"), ("off8", "按 idx>>6 再减 8 行")):
    lines = []
    for s in cands[:2]:
        cells = []
        for ch in s:
            idx = idx_of.get(ord(ch))
            if idx is None:
                continue
            row = idx // 64
            col = idx % 64
            if mode == "off8":
                row -= 8
            y0 = 17 + row * 66
            if y0 < 0 or y0 + 64 > im.height:
                continue
            cells.append(a.crop((col * 64, y0, col * 64 + 64, y0 + 60)))
        if cells:
            canvas = Image.new("L", (60 * len(cells), 60), 0)
            for i, c in enumerate(cells):
                canvas.paste(c, (i * 60, 0))
            lines.append(canvas)
    if lines:
        w = max(l.width for l in lines)
        h = sum(l.height for l in lines)
        canvas = Image.new("L", (w, h), 0)
        y = 0
        for l in lines:
            canvas.paste(l, (0, y))
            y += l.height
        canvas = canvas.resize((w * 2, h * 2), Image.NEAREST)
        p = OUT + "\\_probe_%s.png" % mode
        canvas.save(p)
        print("saved", p, canvas.size, "|", name)
