# -*- coding: utf-8 -*-
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


md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = False

fo = v2f(0x100057E0)
print("=" * 78)
print("格位函数 0x100057E0 完整（找 sepcial-case 分支）")
print("=" * 78)
for ins in md.disasm(d[fo:fo + 0x110], 0x100057E0):
    print("  0x%08X  %-22s %s %s" % (ins.address, ins.bytes.hex(" ")[:22], ins.mnemonic, ins.op_str))
