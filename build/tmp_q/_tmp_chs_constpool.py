# -*- coding: utf-8 -*-
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS.asi"
d = open(P, "rb").read()
SECT = [(".text", 0x1000, 0x2DD98, 0x2DE00, 0x400),
        (".rdata", 0x2F000, 0xC0DA, 0xC200, 0x2E200),
        (".data", 0x3C000, 0x599C, 0x4A00, 0x3A400)]
IMG = 0x10000000


def v2f(va):
    for n, sva, vsz, rsz, rp in SECT:
        if IMG + sva <= va < IMG + sva + vsz:
            return rp + (va - (IMG + sva))
    return None


print("== 常量池 0x1002F4B0..0x1002F540 ==")
f0 = v2f(0x1002F4B0)
for i in range(0, 0x90, 4):
    va = 0x1002F4B0 + i
    u = struct.unpack_from("<I", d, f0 + i)[0]
    fl = struct.unpack_from("<f", d, f0 + i)[0]
    note = ""
    if abs(fl) > 1e-6 and abs(fl) < 1e6:
        note = "   按float=%.9g" % fl
    print("  0x%08X  0x%08X%s" % (va, u, note))

# 找引用 0x1002F4F0 (66.0f) 的代码
print("\n== 引用 0x1002F4F0 的位置 ==")
pat = struct.pack("<I", 0x1002F4F0)
s = 0
hits = []
while True:
    i = d.find(pat, s)
    if i == -1:
        break
    hits.append(i); s = i + 1
print("  ", ["0x%06X(VA 0x%08X)" % (h, (IMG + 0x1000 + (h - 0x400)) if 0x400 <= h < 0x2E200 else 0) for h in hits[:10]])

md = Cs(CS_ARCH_X86, CS_MODE_32)
for h in hits[:6]:
    uva = IMG + 0x1000 + (h - 0x400)
    if not (0x400 <= h < 0x2E200):
        continue
    st = uva - 0x60
    fo = v2f(st)
    print("\n---- 引用处 0x%08X，向前 0x60 字节上下文 ----" % uva)
    code = d[fo:fo + 0xA0]
    n = 0
    for ins in md.disasm(code, st):
        mark = "  <<<" if ins.address == uva else ""
        print("  0x%08X  %-20s %-7s %s%s" % (ins.address, ins.bytes.hex(" ")[:20], ins.mnemonic, ins.op_str, mark))
        n += 1
        if n > 40:
            break
