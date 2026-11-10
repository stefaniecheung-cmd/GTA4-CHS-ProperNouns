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


md = Cs(CS_ARCH_X86, CS_MODE_32)
for START, LEN, NOTE in [(0x1001C840, 0x180, "加载 whm -> gta_whm 对象"),
                         (0x10005870, 0x120, "加载 char_table 后的处理")]:
    fo = v2f(START)
    print("\n" + "=" * 70)
    print("%s  VA 0x%08X" % (NOTE, START))
    print("=" * 70)
    for ins in md.disasm(d[fo:fo + LEN], START):
        print("  0x%08X  %-24s %-7s %s" % (ins.address, ins.bytes.hex(" ")[:24], ins.mnemonic, ins.op_str))
