# -*- coding: utf-8 -*-
import struct, zlib, os, sys
from PIL import Image
sys.path.insert(0, r"C:\Game\Grand Theft Auto IV\gta4-chs\build\tmp_q")
from _tmp_atlas_cells import open_wtd, parse_textures, decode_alpha, CW, CH, COLS

G = r"C:\Game\Grand Theft Auto IV"
CT = os.path.join(G, "plugins", "GTA4.CHS", "char_table.dat")
WTD = os.path.join(G, "update", "pc", "textures", "fonts.wtd")
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"
os.makedirs(OUT, exist_ok=True)

# 字表
b = open(CT, "rb").read()
n = struct.unpack("<I", b[:4])[0]
cps = [struct.unpack("<I", b[4+i*4:8+i*4])[0] for i in range(n)]
idx = {c: i for i, c in enumerate(cps)}

raw, data, texs = open_wtd(WTD)
t = [x for x in texs if "font_chs" in x["name"]][0]
W, H, off = t["w"], t["h"], t["off"]
print("font_chs", W, H, "off", off)

probe = "的是我你人了不在有他这中大为上时个到说们子得就"
tiles = []
for ch in probe:
    o = ord(ch)
    if o not in idx:
        print(f"  {ch} U+{o:04X} 不在表")
        continue
    i = idx[o]
    col, row = i % COLS, i // COLS
    x0, y0 = col*CW, row*CH
    a = decode_alpha(data, off, W, H, x0, y0, min(W,x0+CW), min(H,y0+CH))
    bw, bh = CW, CH
    # 包络
    cols = [x for y in range(bh) for x in range(bw) if a[y*bw+x] > 0]
    rows = [y for y in range(bh) for x in range(bw) if a[y*bw+x] > 0]
    if cols:
        minx, maxx, miny, maxy = min(cols), max(cols), min(rows), max(rows)
        ink = len(cols)
        print(f"  {ch} idx={i} 包络 x[{minx},{maxx}] y[{miny},{maxy}] w={maxx-minx+1} h={maxy-miny+1} ink={ink}")
    else:
        print(f"  {ch} idx={i} 空")
    im = Image.new("L", (bw, bh), 0)
    im.putdata(a)
    tiles.append((ch, im))

# 拼对照图：一行
if tiles:
    sheet = Image.new("L", (CW*len(tiles), CH), 0)
    for k, (ch, im) in enumerate(tiles):
        sheet.paste(im, (k*CW, 0))
    sheet.save(os.path.join(OUT, "calib_existing.png"))
    print("写出 calib_existing.png", sheet.size)
