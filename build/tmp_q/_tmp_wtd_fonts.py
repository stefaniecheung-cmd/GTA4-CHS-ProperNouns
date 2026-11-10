# -*- coding: utf-8 -*-
import struct, os, zlib

OUT = r"C:\Game\gta4-chs\build\atlas_work"
WTD = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\update\pc\textures\fonts.wtd"
raw = open(WTD, "rb").read()
dec = zlib.decompress(raw[raw.find(b"\x78\xda"):])
open(os.path.join(OUT, "p0_fonts_dec.bin"), "wb").write(dec)


def dds_hdr(w, h, fourcc=b"DXT5"):
    hdr = bytearray(128)
    hdr[0:4] = b"DDS "
    struct.pack_into("<I", hdr, 4, 124)
    struct.pack_into("<I", hdr, 8, 0x81007)
    struct.pack_into("<I", hdr, 12, h)
    struct.pack_into("<I", hdr, 16, w)
    struct.pack_into("<I", hdr, 20, w * h // 2 if h > 1 else 0)
    struct.pack_into("<I", hdr, 24, 0)
    struct.pack_into("<I", hdr, 28, 0)
    struct.pack_into("<I", hdr, 76, 32)
    struct.pack_into("<I", hdr, 80, 0x4)
    hdr[84:88] = fourcc
    struct.pack_into("<I", hdr, 108, 0x1000)
    return bytes(hdr)


for i, off in enumerate((4096, 4096 + 1_048_576)):
    px = dec[off: off + 1_048_576]
    p = OUT + ("\\p0_font%d.dds" % (i + 1))
    open(p, "wb").write(dds_hdr(1024, 1024) + px)
    print("written", p, os.path.getsize(p))
