# -*- coding: utf-8 -*-
import os, sys
from PIL import Image, ImageFont, ImageDraw

FONT = r"C:\Users\yy253\AppData\Local\Microsoft\Windows\Fonts\NotoSansSC-VF.ttf"
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"
os.makedirs(OUT, exist_ok=True)

probe = "的是我你人中大个"
# 基准包络（成品图集解码）: w 53-60, h 54-60, x 3-62, y 1-60
for size in (62, 66, 70, 74):
    font = ImageFont.truetype(FONT, size)
    try:
        font.set_variation_by_axes([700])
    except Exception as e:
        print("VF wght 失败:", e)
    print(f"\n=== size {size} Bold ===")
    for ch in probe:
        im = Image.new("L", (128, 128), 0)
        d = ImageDraw.Draw(im)
        d.text((20, 20), ch, font=font, fill=255)
        bbox = im.getbbox()
        if bbox:
            w = bbox[2]-bbox[0]; h = bbox[3]-bbox[1]
            ink = sum(1 for v in im.getdata() if v > 0)
            print(f"  {ch} bbox={bbox} w={w} h={h} ink={ink}")

# 导出 size 66 黑底白字对照格（64x66 居中）
font = ImageFont.truetype(FONT, 66)
try: font.set_variation_by_axes([700])
except Exception: pass
tiles = []
for ch in probe:
    cell = Image.new("L", (64, 66), 0)
    # 大画布渲染裁字面
    big = Image.new("L", (128, 128), 0)
    db = ImageDraw.Draw(big)
    db.text((30, 20), ch, font=font, fill=255)
    bb = big.getbbox()
    glyph = big.crop(bb)
    gw, gh = glyph.size
    x = (64-gw)//2; y = (66-gh)//2
    cell.paste(glyph, (x, y))
    tiles.append(cell)
sheet = Image.new("L", (64*len(tiles), 66), 0)
for k, t in enumerate(tiles):
    sheet.paste(t, (k*64, 0))
sheet.save(os.path.join(OUT, "pil_calib_66.png"))
print("\n写出 pil_calib_66.png", sheet.size)
