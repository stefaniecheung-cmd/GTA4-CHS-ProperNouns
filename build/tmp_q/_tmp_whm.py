# -*- coding: utf-8 -*-
import struct, os

P = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0\plugins\GTA4.CHS\whm_table.dat"
if not os.path.exists(P):
    P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS\whm_table.dat"
d = open(P, "rb").read()
print("文件", P)
print("大小", len(d))

print("\n前 128 字节 hex:")
for i in range(0, 128, 16):
    print("  %3d: %s" % (i, " ".join("%02x" % b for b in d[i:i + 16])))

print("\n前 48 个 4字节小端 int:")
for i in range(0, 48):
    v = struct.unpack("<I", d[i * 4:i * 4 + 4])[0]
    print("  [%2d] %10d  0x%08x" % (i, v, v), end="")
    if (i + 1) % 4 == 0:
        print()
    else:
        print("   ", end="")
print()

print("\n前 48 个 2字节小端:")
vals = [struct.unpack("<H", d[i * 2:i * 2 + 2])[0] for i in range(48)]
print("  ", vals)

print("\n前 48 个 1字节:")
print("  ", list(d[:48]))

# 试几种条目宽度的整除
n = len(d)
print("\n整除检查:")
for w in (2, 3, 4, 6, 8, 10, 12, 16, 18, 20, 24, 28, 32, 36, 40, 44, 48, 56, 64, 72, 96, 144, 222, 148, 152):
    if n % w == 0:
        print("   %d B/条目 -> %d 条" % (w, n // w))
print("   n-4 =", n - 4)
for w in (12, 16, 20, 24, 28, 32, 144, 148, 152):
    if (n - 4) % w == 0:
        print("   (n-4)=%d, %d B/条目 -> %d 条" % (n - 4, w, (n - 4) // w))
