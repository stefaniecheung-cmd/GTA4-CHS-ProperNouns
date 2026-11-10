# -*- coding: utf-8 -*-
import zlib, struct

SRC = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\update\pc\textures\fonts.wtd"
raw = open(SRC, "rb").read()
body = zlib.decompress(raw[0xC:])
print("body", len(body))

head = body[:4096]
print("--- head ascii strings ---")
import re
for m in re.finditer(rb"[\x20-\x7e]{4,60}", head):
    print(" ", hex(m.start()), m.group().decode())

print("\n--- head first 64 dwords ---")
for i in range(0, 64, 8):
    print("  %03X:" % i, " ".join("%08X" % v for v in struct.unpack_from("<8I", head, i)))

print("\n--- 4 words before each name ---")
for m in re.finditer(rb"pack:/", head):
    off = m.start()
    print("  name at", hex(off), m.group()[:40])
