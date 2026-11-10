# -*- coding: utf-8 -*-
import struct
CT = r"C:\Users\yy253\Desktop\GTA4汉化补丁2026-11-09\release\plugins\GTA4.CHS\char_table.dat"
data = open(CT, "rb").read()
n = struct.unpack("<I", data[:4])[0]
cps = [struct.unpack("<I", data[4 + i*4:8 + i*4])[0] for i in range(n)]

# 找候选间隔符/中点/空格
for target in (0x00B7, 0xFF65, 0x30FB, 0x2022, 0x3000, 0x0020, 0xFF0F, 0x2122, 0x00A9, 0x00AE, 0x00AC, 0x2014, 0x2013):
    if target in cps:
        print("有 U+%04X %r  @索引 %d" % (target, chr(target), cps.index(target)))
    else:
        print("无 U+%04X %r" % (target, chr(target)))

# ASCII 覆盖情况
ascii_n = [c for c in cps if c < 0x80]
print("\nASCII 码点个数:", len(ascii_n))
print("ASCII 内容:", "".join(chr(c) for c in sorted(ascii_n)))

# 全角标点区块
fw = [c for c in cps if 0xFF00 <= c <= 0xFFEF]
print("\n全角区块字符:", "".join(chr(c) for c in sorted(fw)))

# 前 200 / 2000 个附近
print("\n索引 1950-2010:", "".join(chr(c) for c in cps[1950:2010]))
print("索引 3000-3060:", "".join(chr(c) for c in cps[3000:3060]))
