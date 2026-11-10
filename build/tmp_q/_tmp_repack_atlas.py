# -*- coding: utf-8 -*-
"""图集重编：旧字模按新表索引搬格 + 44 新字入格，整平面 BC3/DXT5 重编，repack wtd。
用法: python _tmp_repack_atlas.py <pc|TLAD|TBoGT>
先出 font_work/fonts_<ch>_new.wtd，不覆盖部署。
"""
import os, sys, csv, struct, zlib, time

G = r"C:\Game\Grand Theft Auto IV"
WORK = os.path.join(G, "gta4-chs", "build", "font_work")
GLY = os.path.join(WORK, "glyphs")
DEP = {
    "pc":   os.path.join(G, "update", "pc", "textures", "fonts.wtd"),
    "TLAD": os.path.join(G, "update", "TLAD", "pc", "textures", "fonts.wtd"),
    "TBoGT":os.path.join(G, "update", "TBoGT", "pc", "textures", "fonts.wtd"),
}
NEW_TAB = os.path.join(WORK, "char_table_new.dat")
DEP_TAB = os.path.join(G, "plugins", "GTA4.CHS", "char_table.dat")

CW, CH, COLS = 64, 66, 64
VTABLE = 0xb6f0ee97

# ---------- 移植自仓库 wtd_font.js ----------
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
    BW = W//4; rw=x1-x0; rh=y1-y0
    out = [0]*(rw*rh)
    for by in range(y0//4, (y1-1)//4 + 1):
        for bx in range(x0//4, (x1-1)//4 + 1):
            o = off + (by*BW+bx)*16
            a0, a1 = data[o], data[o+1]
            pal = alpha_palette(a0,a1)
            bits = int.from_bytes(data[o+2:o+8], "little")
            for p in range(16):
                px = bx*4+(p&3); py = by*4+(p>>2)
                if px<x0 or px>=x1 or py<y0 or py>=y1: continue
                out[(py-y0)*rw+(px-x0)] = pal[(bits>>(3*p))&7]
    return out

def encode_alpha_block(vals):
    mn=255; mx=0
    for v in vals:
        if v<mn: mn=v
        if v>mx: mx=v
    out = bytearray(8)
    if mn==mx:
        out[0]=mx; out[1]=mx; return out
    cand = sorted(set(list(vals)+[0,255]))
    if len(cand)>14:
        pick = {cand[0], cand[-1]}
        for i in range(12): pick.add(cand[round(i*(len(cand)-1)/11)])
        cand = sorted(pick)
    best=None
    for a0 in cand:
        for a1 in cand:
            pal=alpha_palette(a0,a1); sse=0; idx=[0]*16
            for p in range(16):
                bd=10**9; bi=0
                for k in range(8):
                    dd=abs(pal[k]-vals[p])
                    if dd<bd: bd=dd; bi=k
                idx[p]=bi; sse+=bd*bd
            if best is None or sse<best[0]: best=(sse,a0,a1,idx)
    _,a0,a1,idx=best
    out[0]=a0; out[1]=a1
    bits=0
    for p in range(16): bits |= idx[p] << (3*p)
    for k in range(6): out[2+k]=(bits>>(8*k))&0xff
    return out

def encode_color_block(alphas):
    out=bytearray(8)
    anyOn=any(v>0 for v in alphas); anyOff=any(v==0 for v in alphas)
    if not anyOn: return out
    if not anyOff:
        struct.pack_into("<HH", out, 0, 0xffff, 0xffff); return out
    struct.pack_into("<HH", out, 0, 0xffff, 0x0000)
    idx=0
    for p in range(16):
        if alphas[p]==0: idx |= 1 << (2*p)
    struct.pack_into("<I", out, 4, idx)
    return out

def read_table(path):
    b=open(path,"rb").read(); n=struct.unpack("<I",b[:4])[0]
    return list(struct.unpack("<%dI"%n, b[4:4+n*4]))

def main(ch):
    t0=time.time()
    src=DEP[ch]
    raw=open(src,"rb").read()
    assert raw[:4]==b"RSC\x05", "非 RSC5"
    flags=struct.unpack("<I",raw[4:8])[0]
    sizes=struct.unpack("<I",raw[8:12])[0]
    data=bytearray(zlib.decompress(raw[12:]))
    texs=parse_textures(data)
    print(f"[{ch}] 解压 {len(data)}B  贴图 {len(texs)}")
    for t in texs:
        print(f"   {t['name']!r} {t['w']}x{t['h']} {t['fourcc']} off={t['off']}")
    chs=[t for t in texs if "font_chs" in t["name"]]
    assert len(chs)==1, "font_chs 不唯一"
    t=chs[0]; W,H=t["w"],t["h"]; off=t["off"]

    old_cps=read_table(DEP_TAB)
    new_cps=read_table(NEW_TAB)
    old_idx={c:i for i,c in enumerate(old_cps)}
    print(f"   旧表 {len(old_cps)}  新表 {len(new_cps)}")

    # 新字 bin 映射
    glyph_bin={}
    man=os.path.join(WORK,"render_manifest.tsv")
    with open(man,encoding="utf-8-sig") as f:
        for r in csv.DictReader(f,delimiter="\t"):
            glyph_bin[int(r["码位"].replace("U+",""),16)]=r["字符"]

    # 构建 alpha 平面（初始全 0）
    plane=bytearray(W*H)
    BW=W//4
    moved=0; added=0
    for j,cp in enumerate(new_cps):
        col=j%COLS; row=j//COLS
        x0=col*CW; y0=row*CH
        x1=min(W,x0+CW); y1=min(H,y0+CH)
        if cp in old_idx:
            # 旧字：按旧表索引 oi 的坐标解码旧包字模
            oii=old_idx[cp]
            ocol=oii%COLS; orow=oii//COLS
            ox0=ocol*CW; oy0=orow*CH
            ox1=min(W,ox0+CW); oy1=min(H,oy0+CH)
            a=decode_alpha(data,off,W,H,ox0,oy0,ox1,oy1)
            moved+=1
        else:
            p=os.path.join(GLY,f"U+{cp:04X}.bin")
            a=list(open(p,"rb").read())
            added+=1
        # 写入平面（新格 j 坐标）
        rw=x1-x0; rh=y1-y0
        for y in range(rh):
            base=(y0+y)*W+x0
            plane[base:base+rw]=a[y*CW:y*CW+rw]
    print(f"   搬格旧字 {moved}  新字 {added}  平面 {W}x{H}")

    # 整平面 BC3 编码覆盖 off 段
    t1=time.time()
    for by in range(H//4):
        for bx in range(W//4):
            vals=[0]*16
            for p in range(16):
                px=bx*4+(p&3); py=by*4+(p>>2)
                vals[p]=plane[py*W+px]
            o=off+(by*BW+bx)*16
            data[o:o+8]=encode_alpha_block(vals)
            data[o+8:o+16]=encode_color_block(vals)
    print(f"   BC3 编码 {time.time()-t1:.1f}s")

    # repack
    body=zlib.compress(bytes(data),9)
    out=bytearray(12+len(body))
    out[0:4]=b"RSC\x05"
    struct.pack_into("<I",out,4,flags)
    struct.pack_into("<I",out,8,sizes)
    out[12:]=body
    dst=os.path.join(WORK,f"fonts_{ch}_new.wtd")
    open(dst,"wb").write(out)
    print(f"   写出 {dst}  {len(out)}B  总耗时 {time.time()-t0:.1f}s")

if __name__=="__main__":
    main(sys.argv[1])
