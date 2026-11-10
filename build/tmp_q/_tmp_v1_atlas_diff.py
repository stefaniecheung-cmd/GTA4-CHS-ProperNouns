# -*- coding: utf-8 -*-
import struct, zlib, os, subprocess
from PIL import Image, ImageChops

W = r"C:\Game\gta4-chs\build\atlas_work"
os.makedirs(W, exist_ok=True)
Z = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
tc = r"C:\Game\_tools\texconv.exe"


def dds_hdr(w, h, fourcc=b"DXT5"):
    hdr = bytearray()
    hdr += b"DDS " + struct.pack("<I", 124)
    hdr += struct.pack("<I", 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000)
    hdr += struct.pack("<I", h) + struct.pack("<I", w)
    hdr += struct.pack("<I", 0) + struct.pack("<I", 0) + struct.pack("<I", 1)
    hdr += b"\x00" * 44 + struct.pack("<I", 32) + struct.pack("<I", 0x4) + fourcc
    hdr += struct.pack("<I", 0) * 5 + struct.pack("<I", 0x1000 | 0x8 | 0x80000)
    hdr += struct.pack("<I", 0) * 4
    return bytes(hdr)


def unwrap(p, tag):
    d = open(p, "rb").read()
    raw = zlib.decompress(d[12:])
    px = raw[-4096 * 4096:]
    out = os.path.join(W, f"{tag}.dds")
    open(out, "wb").write(dds_hdr(4096, 4096) + px)
    r = subprocess.run([tc, "-y", "-ft", "png", "-o", W, out], capture_output=True)
    print(tag, "原始", len(raw), "->", out, "texconv", r.returncode)


pairs = [
    (r"update\pc\textures\fonts.wtd", "v1_base"),
    (r"update\TLAD\pc\textures\fonts.wtd", "v1_tlad"),
    (r"update\TBoGT\pc\textures\fonts.wtd", "v1_tbogt"),
]
for rel, tag in pairs:
    unwrap(os.path.join(Z, rel), tag)

# 差异
print("\n==== 图集差异 ====")
for tag, base in (("v1_base", "atlas_base_px"), ("v1_tlad", "atlas_TLAD_px"), ("v1_tbogt", "atlas_TBoGT_px")):
    a = Image.open(os.path.join(W, base + ".png")).convert("RGBA")
    b = Image.open(os.path.join(W, tag + ".png")).convert("RGBA")
    diff = ImageChops.difference(a, b)
    bbox = diff.getbbox()
    print(tag, "vs", base, "差异包围盒:", bbox)
    if bbox:
        # 差异像素统计
        nz = sum(1 for p in diff.getdata() if p[0] or p[1] or p[2] or p[3])
        print("   差异像素数:", nz)
        diff.convert("RGB").point(lambda v: 255 if v > 8 else 0)
        d2 = diff.convert("L").point(lambda v: 255 if v > 8 else 0)
        d2.save(os.path.join(W, f"diffmask_{tag}.png"))
