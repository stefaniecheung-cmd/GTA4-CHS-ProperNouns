# -*- coding: utf-8 -*-
import struct, zlib, os, sys, collections

G = r"C:\Game\Grand Theft Auto IV"
REF = os.path.join(G, "gta4-chs", "reference", "第三方补完包v1.0")

CW, CH, COLS = 64, 66, 64
VTABLE = 0xb6f0ee97

def open_wtd(path):
    raw = open(path, "rb").read()
    if raw[:4] != b"RSC\x05":
        raise SystemExit("不是 RSC5: " + path)
    data = zlib.decompress(raw[12:])
    texs = parse_textures(data)
    return raw, data, texs

def parse_textures(d):
    out = []
    for o in range(0, 0x1000 - 0x50 + 1, 4):
        if struct.unpack_from("<I", d, o)[0] != VTABLE: continue
        namePtr = struct.unpack_from("<I", d, o+0x14)[0]
        wh = struct.unpack_from("<I", d, o+0x1c)[0]
        fourcc = d[o+0x20:o+0x24].decode("latin1")
        dataPtr = struct.unpack_from("<I", d, o+0x48)[0]
        name = ""
        if 0x50000000 <= namePtr < 0x50000000 + 0x1000:
            no = namePtr - 0x50000000
            e = no
            while e < 0x1000 and d[e] != 0: e += 1
            name = d[no:e].decode("latin1")
        if dataPtr < 0x60000000: continue
        out.append({"at":o,"name":name,"w":wh&0xffff,"h":(wh>>16)&0xffff,
                    "fourcc":fourcc,"dataPtr":dataPtr,
                    "off":dataPtr-0x60000000+0x1000})
    return out

def alpha_palette(a0, a1):
    p = [0]*8
    p[0], p[1] = a0, a1
    if a0 > a1:
        for k in range(1,7): p[1+k] = ((7-k)*a0 + k*a1)//7
    else:
        for k in range(1,6): p[1+k] = ((5-k)*a0 + k*a1)//5
        p[6], p[7] = 0, 255
    return p

def decode_alpha(data, off, W, H, x0,y0,x1,y1):
    BW = W//4; out = [0]*((y1-y0)*(x1-x0))
    for by in range(y0//4, (y1-1)//4 + 1):
        for bx in range(x0//4, (x1-1)//4 + 1):
            o = off + (by*BW+bx)*16
            a0, a1 = data[o], data[o+1]
            pal = alpha_palette(a0,a1)
            bits = int.from_bytes(data[o+2:o+8], "little")
            for p in range(16):
                px = bx*4 + (p&3); py = by*4 + (p>>2)
                if px<x0 or px>=x1 or py<y0 or py>=y1: continue
                out[(py-y0)*(x1-x0)+(px-x0)] = pal[(bits>>(3*p))&7]
    return out

def cell_ink(data, off, W, H, i):
    col = i % COLS; row = i // COLS
    x0 = col*CW; y0 = row*CH
    x1 = min(W, x0+CW); y1 = min(H, y0+CH)
    a = decode_alpha(data, off, W, H, x0,y0,x1,y1)
    return sum(1 for v in a if v > 0)

def analyze(path, label):
    raw, data, texs = open_wtd(path)
    print(f"\n===== {label}  {os.path.basename(path)}  解压 {len(data)}B =====")
    for t in texs:
        print(f"  贴图 @{t['at']:#x} 名字={t['name']!r} {t['w']}x{t['h']} {t['fourcc']} off={t['off']}")
    chs = [t for t in texs if "font_chs" in t["name"]]
    if not chs:
        print("  无 font_chs"); return
    t = chs[0]; W,H = t["w"], t["h"]
    off = t["off"]
    ncell = COLS * (H//CH)
    inks = [cell_ink(data, off, W, H, i) for i in range(ncell)]
    nonempty = [i for i,v in enumerate(inks) if v > 0]
    print(f"  格数 {ncell}  非空格 {len(nonempty)}  空格 {ncell-len(nonempty)}")
    # 前 512 格
    ne512 = [i for i in range(512) if inks[i] > 0]
    print(f"  前 512 格非空: {len(ne512)}  首 20: {ne512[:20]}")
    # 墨量最大/最小样例
    print(f"  墨量 前32格: {inks[:32]}")
    print(f"  格 442 墨量={inks[442] if 442<ncell else 'NA'}")
    # 连续空格段：找最后一个非空格
    print(f"  最后非空格 idx={nonempty[-1] if nonempty else -1}")
    return inks

if __name__ == "__main__":
    analyze(os.path.join(REF, "_ORIGINAL_fonts_pc.wtd"), "pristine base")
    analyze(os.path.join(G, "update", "pc", "textures", "fonts.wtd"), "部署成品 base")
