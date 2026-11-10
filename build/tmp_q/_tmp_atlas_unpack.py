# -*- coding: utf-8 -*-
import struct, zlib, os

BASE = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 FIX\release\update"
OUT  = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"
os.makedirs(OUT, exist_ok=True)

SRC = {
 "base":   os.path.join(BASE, r"pc\textures\fonts.wtd"),
 "TLAD":   os.path.join(BASE, r"TLAD\pc\textures\fonts.wtd"),
 "TBoGT":  os.path.join(BASE, r"TBoGT\pc\textures\fonts.wtd"),
}

for ch, p in SRC.items():
    raw = open(p, "rb").read()
    print("==", ch, "文件", len(raw), "head", raw[:16].hex())
    start = raw.find(b"\x78\xda")
    if start < 0:
        start = raw.find(b"\x78\x9c")
    print("   zlib @", hex(start) if start >= 0 else "未找到")
    dec = None
    if start >= 0:
        try:
            dec = zlib.decompress(raw[start:])
        except Exception as e:
            for trim in range(1, 257):
                try:
                    dec = zlib.decompress(raw[start:len(raw)-trim])
                    print("   ok trim", trim)
                    break
                except Exception:
                    dec = None
    if dec is None:
        print("   解压失败")
        continue
    print("   解压后", len(dec), "DDS?", dec[:4])
    if dec[:4] == b"DDS ":
        size, flags, h, w, pitch, depth, mips = struct.unpack_from("<7I", dec, 4)
        fourcc = dec[84:88]
        print(f"   DDS h={h} w={w} pitch={pitch} mips={mips} fourcc={fourcc} 体量={128+h*w}")
    out = os.path.join(OUT, f"atlas_{ch}.dds")
    open(out, "wb").write(dec)
    print("   写出", out, len(dec))
