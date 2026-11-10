# -*- coding: utf-8 -*-
import struct, sys, io

P1 = r"C:\Users\yy253\Desktop\GTA4汉化补丁2026-11-09\release\update\common\text\american.gxt"
P2 = r"C:\Game\gta4-chs\build\zchs_base_tr.gxt"
P3 = r"C:\Game\Grand Theft Auto IV\common\text\american.gxt"

def hdr(p, label):
    b = open(p, "rb").read(16)
    sig, tcount = struct.unpack("<4sI", b[:8])
    print(f"{label}: 大小={len(open(p,'rb').read())} sig={sig!r} 表数={tcount} 头8字节={b[:8].hex()}")

hdr(P1, "补丁")
hdr(P2, "我方")
hdr(P3, "原版")

def parse(p):
    data = open(p, "rb").read()
    sig, tcount = struct.unpack("<4sI", data[:8])
    cells = []
    off = 8
    for _ in range(tcount):
        raw = data[off:off+12]
        cells.append(struct.unpack("<8sI", raw))
        off += 12
    return sig, tcount, cells, data

print()
for p, label in ((P1, "补丁"), (P2, "我方")):
    sig, n, cells, data = parse(p)
    print(f"\n== {label} 表目录 ==")
    print("  第一表:", cells[0])
    # 表名大小写统计
    up = sum(1 for nm, _ in cells if nm.isupper())
    print(f"  表名全大写的数量: {up}/{n}")
    # 条目数
    total = 0
    for i, (nm, o) in enumerate(cells):
        if i + 1 < len(cells):
            # 条目数来自表头：读表起始 8 字节
            cnt = struct.unpack("<I", data[o:o+4])[0]
            total += cnt
    print("  目录推算总条目:", total)
    print("  样例前5表名:", [nm for nm, _ in cells[:5]])
