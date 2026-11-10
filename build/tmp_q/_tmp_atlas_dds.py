# -*- coding: utf-8 -*-
import struct, os, subprocess

W = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\atlas_work"

def dds_hdr(w, h, fourcc=b"DXT5", size=0):
    hdr = bytearray()
    hdr += b"DDS "
    hdr += struct.pack("<I", 124)                 # dwSize
    hdr += struct.pack("<I", 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000)  # caps|height|width|pixelformat|linear
    hdr += struct.pack("<I", h)                   # height
    hdr += struct.pack("<I", w)                   # width
    hdr += struct.pack("<I", size)                # pitchOrLinearSize
    hdr += struct.pack("<I", 0)                   # depth
    hdr += struct.pack("<I", 1)                   # mipMapCount
    hdr += b"\x00" * 44                           # reserved
    hdr += struct.pack("<I", 32)                  # pf size
    hdr += struct.pack("<I", 0x4)                 # DDPF_FOURCC
    hdr += fourcc
    hdr += struct.pack("<I", 0) * 5               # rgbBitCount + masks
    hdr += struct.pack("<I", 0x1000 | 0x8 | 0x80000)  # caps
    hdr += struct.pack("<I", 0) * 4
    return bytes(hdr)

for ch in ("base", "TLAD", "TBoGT"):
    src = os.path.join(W, f"atlas_{ch}.dds")
    raw = open(src, "rb").read()
    px = 4096 * 4096                        # 16,777,216
    tail = raw[-px:]
    out = os.path.join(W, f"atlas_{ch}_px.dds")
    open(out, "wb").write(dds_hdr(4096, 4096) + tail)
    print(ch, "原始", len(raw), "头部长", len(raw) - px, "写出", out, os.path.getsize(out))

# texconv 转 PNG
tc = r"C:\Game\_tools\texconv.exe"
for ch in ("base", "TLAD", "TBoGT"):
    d = os.path.join(W, f"atlas_{ch}_px.dds")
    r = subprocess.run([tc, "-y", "-ft", "png", "-o", W, d], capture_output=True, text=True)
    print(ch, "texconv rc=", r.returncode, (r.stdout or "")[-200:], (r.stderr or "")[-200:])
print("\n目录内容：")
for f in sorted(os.listdir(W)):
    print("   %12d  %s" % (os.path.getsize(os.path.join(W, f)), f))
