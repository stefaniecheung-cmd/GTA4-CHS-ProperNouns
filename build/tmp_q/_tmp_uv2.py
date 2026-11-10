# -*- coding: utf-8 -*-
import struct
from capstone import *

ASI = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS.asi"
d = open(ASI, "rb").read()

# PE 段表
pe = struct.unpack_from("<I", d, 0x3C)[0]
nsec = struct.unpack_from("<H", d, pe + 6)[0]
opt = struct.unpack_from("<H", d, pe + 20)[0]
sec0 = pe + 24 + opt
secs = []
for i in range(nsec):
    o = sec0 + i * 40
    name = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vsize, va, rsize, rptr = struct.unpack_from("<IIII", d, o + 8)
    secs.append((name, va, vsize, rptr, rsize))
    print(name, hex(va), hex(vsize), hex(rptr), hex(rsize))

IB = 0x10000000


def va2off(va):
    r = va - IB
    for name, sva, vs, rp, rs in secs:
        if sva <= r < sva + max(vs, rs):
            return rp + (r - sva)
    return None


def dis(va, n=200, title=""):
    off = va2off(va)
    code = d[off:off + n]
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    print("\n=== %s @ %08X ===" % (title, va))
    for ins in md.disasm(code, va):
        print("  %08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))


dis(0x10006810, 260, "UV func")
