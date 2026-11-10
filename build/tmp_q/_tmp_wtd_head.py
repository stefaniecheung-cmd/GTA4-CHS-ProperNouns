# -*- coding: utf-8 -*-
import struct, zlib, os, re

P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\update\pc\textures\fonts.wtd"
OUT = r"C:\Game\gta4-chs\build\atlas_work"
raw = open(P, "rb").read()
start = raw.find(b"\x78\xda")
dec = zlib.decompress(raw[start:])
print("decompressed", len(dec), "head:", dec[:16].hex(" "))

# 打印前 4096 字节的可读字符串
head = dec[:4096]
strs = re.findall(rb"[\x20-\x7e]{4,}", head)
print("\n== 头区字符串 ==")
for s in strs[:40]:
    print("  ", s.decode("latin-1"))

# 打印头部 u32
print("\n== 前 16 个 u32 ==")
for i in range(16):
    print("  +0x%02X = 0x%08X (%d)" % (i * 4, struct.unpack_from("<I", dec, i * 4)[0], struct.unpack_from("<I", dec, i * 4)[0]))

# 假设 4096² 在末尾
TAIL = 16_777_216
print("\n末尾块起点 =", len(dec) - TAIL, " 头区=", len(dec) - TAIL)
print("头区 / 1048576 =", (len(dec) - TAIL) / 1_048_576)
