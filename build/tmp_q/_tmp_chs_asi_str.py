# -*- coding: utf-8 -*-
import re, struct

P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS.asi"
d = open(P, "rb").read()
print("大小", len(d))

# 提取可打印 ASCII 串（>=4）
pat = re.compile(rb"[ -~]{4,}")
hits = []
for m in pat.finditer(d):
    s = m.group().decode("latin-1")
    hits.append((m.start(), s))

KW = ("char_table", "whm", "fonts", "wtd", "gxt", "CHS", "dat", "ini", "log")
print("\n== 关键字串 ==")
for off, s in hits:
    if any(k.lower() in s.lower() for k in KW):
        print("  0x%06X  %s" % (off, s[:120]))

print("\n== PE 段表 ==")
e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
print("  e_lfanew = 0x%X" % e_lfanew)
nsec = struct.unpack_from("<H", d, e_lfanew + 6)[0]
print("  段数", nsec)
opt = struct.unpack_from("<H", d, e_lfanew + 20)[0]
print("  OptionalHeaderSize", opt)
sh = e_lfanew + 24 + opt
for i in range(nsec):
    base = sh + i * 40
    name = d[base:base + 8].rstrip(b"\x00").decode("latin-1")
    vsz, va, rsz, raw = struct.unpack_from("<IIII", d, base + 8)
    print("  %-8s VA=0x%08X VSize=0x%06X RawSize=0x%06X RawPtr=0x%06X" % (name, va, vsz, rsz, raw))
imgbase = struct.unpack_from("<I", d, e_lfanew + 24 + 28)[0]
print("  ImageBase = 0x%08X" % imgbase)
