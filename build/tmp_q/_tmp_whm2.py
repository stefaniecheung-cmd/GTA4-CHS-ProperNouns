# -*- coding: utf-8 -*-
import struct, zlib, io

P = r"C:\Users\yy253\Desktop\汉化补丁+FUSIONFIX5.1.2+Solitude 3 Fix\release\plugins\GTA4.CHS\whm_table.dat"
raw = open(P, "rb").read()
n = struct.unpack_from("<I", raw, 0)[0]
ts = 4 + n * 8
print("whm 条目数 =", n, " 文件", len(raw), " 文本区起 =", ts, " 文本区长度 =", len(raw) - ts)
entries = [struct.unpack_from("<II", raw, 4 + i * 8) for i in range(n)]
print("\n前 12 条 (hash, offset):")
for i in range(12):
    print("  %8d  0x%08X  0x%08X" % (i, entries[i][0], entries[i][1]))

offs = [e[1] for e in entries]
hs = [e[0] for e in entries]
print("\noffset 单调递增?", all(offs[i] <= offs[i + 1] for i in range(n - 1)), " 最大 offset:", max(offs))
print("hash 单调递增?", all(hs[i] <= hs[i + 1] for i in range(n - 1)))

print("\n== 文本区前 8 条 ==")
out = io.StringIO()
for i in range(8):
    o = entries[i][1]
    seg = raw[ts + o: ts + o + 32]
    ch = None
    ln_ch = 0
    for ln in (1, 2, 3, 4):
        try:
            c = seg[:ln].decode("utf-8")
            if len(c) == 1:
                ch = c
                ln_ch = ln
                break
        except Exception:
            pass
    out.write("  [%d] hash=0x%08X off=%d bytes=%s" % (i, entries[i][0], o, seg.hex(" ")))
    if ch:
        out.write("  -> %r 其后: %s" % (ch, seg[ln_ch:].hex(" ")))
    out.write("\n")
print(out.getvalue())


def crc32(b):
    return zlib.crc32(b) & 0xFFFFFFFF


print("== hash 算法猜测 ==")
for i in range(8):
    o = entries[i][1]
    seg = raw[ts + o: ts + o + 16]
    ch = None
    for ln in (1, 2, 3):
        try:
            c = seg[:ln].decode("utf-8")
            if len(c) == 1:
                ch = c
                break
        except Exception:
            pass
    if not ch:
        continue
    h = entries[i][0]
    c1 = crc32(ch.encode("utf-8"))
    c2 = crc32(struct.pack("<H", ord(ch)))
    c3 = crc32(struct.pack("<I", ord(ch)))
    print("  [%d] %r h=0x%08X crc_utf8=0x%08X crc_u16=0x%08X crc_u32=0x%08X" % (i, ch, h, c1, c2, c3))
