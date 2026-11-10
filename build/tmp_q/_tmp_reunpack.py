# -*- coding: utf-8 -*-
import os, zlib, struct, subprocess
from PIL import Image

BASE = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\update"
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"
TEX = r"C:\Game\_tools\texconv.exe"

DDS_HDR = bytearray(128)
DDS_HDR[0:4] = b"DDS "
struct.pack_into("<I", DDS_HDR, 4, 124)
struct.pack_into("<I", DDS_HDR, 8, 0x81007)
struct.pack_into("<I", DDS_HDR, 12, 4096)
struct.pack_into("<I", DDS_HDR, 16, 4096)
struct.pack_into("<I", DDS_HDR, 20, 4096 * 4096 // 2)
struct.pack_into("<I", DDS_HDR, 28, 1)
struct.pack_into("<I", DDS_HDR, 76, 32)
struct.pack_into("<I", DDS_HDR, 80, 0x4)
DDS_HDR[84:88] = b"DXT5"
struct.pack_into("<I", DDS_HDR, 108, 0x1000)

for ch in ("pc", "TLAD", "TBoGT"):
    src = BASE + "\\" + ch + "\\textures\\fonts.wtd"
    raw = open(src, "rb").read()
    print(ch, "file", len(raw), raw[:12].hex())
    body = zlib.decompress(raw[0xC:])
    print("  decomp", len(body))
    px = body[len(body) - 4096 * 4096:]
    dds = OUT + "\\_rel_%s.dds" % ch
    with open(dds, "wb") as f:
        f.write(DDS_HDR + px)
    subprocess.run([TEX, "-y", "-ft", "png", "-o", OUT, dds],
                   capture_output=True)
    print("  ->", os.path.exists(OUT + "\\_rel_%s.png" % ch))
