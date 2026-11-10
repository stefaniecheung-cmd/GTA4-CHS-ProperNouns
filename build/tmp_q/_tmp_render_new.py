# -*- coding: utf-8 -*-
"""渲染 44 个新 CJK 字到 64x66 alpha 格，过三道闸，落盘 bin + manifest + 对照 PNG。"""
import os, csv, struct, sys
from PIL import Image, ImageFont, ImageDraw

G = r"C:\Game\Grand Theft Auto IV"
FONT = r"C:\Users\yy253\AppData\Local\Microsoft\Windows\Fonts\NotoSansSC-VF.ttf"
SRC = os.path.join(G, "gta4-chs", "build", "cmp_assets", "缺字清单_最新.tsv")
WORK = os.path.join(G, "gta4-chs", "build", "font_work")
GLY = os.path.join(WORK, "glyphs")
os.makedirs(GLY, exist_ok=True)

CW, CH = 64, 66
SIZE = 62
MAX_W, MAX_H = 61, 60

# 读 CJK 缺字
targets = []
with open(SRC, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["类别"] == "CJK":
            targets.append((r["字符"], int(r["码位"].replace("U+",""), 16), r["章节"], r["CRC"]))
print("待渲染 CJK:", len(targets))

font = ImageFont.truetype(FONT, SIZE)
font.set_variation_by_name("Bold")

manifest = []
tiles = []
fail = []
for ch, cp, ch_, crc in targets:
    big = Image.new("L", (160, 160), 0)
    d = ImageDraw.Draw(big)
    d.text((40, 30), ch, font=font, fill=255)
    bb = big.getbbox()
    if not bb:
        fail.append((ch, cp, "空渲染")); continue
    glyph = big.crop(bb)
    gw, gh = glyph.size
    scale = min(MAX_W/gw, MAX_H/gh, 1.0)
    if scale < 1.0:
        glyph = glyph.resize((max(1, round(gw*scale)), max(1, round(gh*scale))), Image.LANCZOS)
        gw, gh = glyph.size
    cell = Image.new("L", (CW, CH), 0)
    x = (CW-gw)//2; y = (CH-gh)//2
    cell.paste(glyph, (x, y))
    ink = sum(1 for v in cell.getdata() if v > 0)
    # 闸：包络 / 墨量 / 触边
    cbb = cell.getbbox()
    cw = cbb[2]-cbb[0]; chh = cbb[3]-cbb[1]
    edge = cbb[0] < 1 or cbb[1] < 1 or cbb[2] > CW-1 or cbb[3] > CH-1
    ok = (cw <= MAX_W and chh <= MAX_H and ink > 0 and not edge)
    if not ok: fail.append((ch, cp, f"w{cw} h{chh} ink{ink} edge{edge}"))
    # 落盘 bin
    arr = list(cell.getdata())
    with open(os.path.join(GLY, f"U+{cp:04X}.bin"), "wb") as f:
        f.write(bytes(arr))
    manifest.append({"cp": cp, "ch": ch, "w": cw, "h": chh, "ink": ink,
                     "x": cbb[0], "y": cbb[1], "ok": "PASS" if ok else "FAIL",
                     "chapter": ch_, "crc": crc})
    tiles.append(cell)

# manifest
with open(os.path.join(WORK, "render_manifest.tsv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["码位","字符","宽","高","墨量","x","y","闸","章节","CRC"])
    for m in manifest:
        w.writerow([f"U+{m['cp']:04X}", m["ch"], m["w"], m["h"], m["ink"], m["x"], m["y"], m["ok"], m["chapter"], m["crc"]])

# 对照 PNG（黑底白字，两行）
cols = 11
rows = (len(tiles)+cols-1)//cols
sheet = Image.new("L", (CW*cols, CH*rows), 0)
for k, t in enumerate(tiles):
    sheet.paste(t, ((k%cols)*CW, (k//cols)*CH))
sheet.save(os.path.join(WORK, "render_preview.png"))

print(f"渲染 {len(manifest)} 字，FAIL {len(fail)}")
for m in manifest:
    if m["ok"] != "PASS":
        print("  FAIL", f"U+{m['cp']:04X}", m["ch"], f"w{m['w']} h{m['h']} ink{m['ink']}")
for x in fail:
    print("  ", x)
print("manifest:", os.path.join(WORK, "render_manifest.tsv"))
print("preview:", os.path.join(WORK, "render_preview.png"))
