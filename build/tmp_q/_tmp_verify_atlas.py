# -*- coding: utf-8 -*-
"""图集离线校验：新包 vs 旧包。
用法: python _tmp_verify_atlas.py <pc|TLAD|TBoGT>
"""
import os, sys, csv, struct, zlib, statistics

G = r"C:\Game\Grand Theft Auto IV"
WORK = os.path.join(G, "gta4-chs", "build", "font_work")
GLY = os.path.join(WORK, "glyphs")
OLD = {"pc":"fonts_pc.wtd","TLAD":"fonts_TLAD.wtd","TBoGT":"fonts_TBoGT.wtd"}
DEP_TAB = os.path.join(G, "plugins", "GTA4.CHS", "char_table.dat")
NEW_TAB = os.path.join(WORK, "char_table_new.dat")

CW, CH, COLS = 64, 66, 64
VTABLE = 0xb6f0ee97

def parse_textures(d):
    out=[]
    for o in range(0,0x1000-0x50+1,4):
        if struct.unpack_from("<I",d,o)[0]!=VTABLE: continue
        namePtr=struct.unpack_from("<I",d,o+0x14)[0]
        wh=struct.unpack_from("<I",d,o+0x1c)[0]
        fourcc=d[o+0x20:o+0x24].decode("latin1")
        dataPtr=struct.unpack_from("<I",d,o+0x48)[0]
        name=""
        if 0x50000000<=namePtr<0x50000000+0x1000:
            no=namePtr-0x50000000; e=no
            while e<0x1000 and d[e]!=0: e+=1
            name=d[no:e].decode("latin1")
        if dataPtr<0x60000000: continue
        out.append({"name":name,"w":wh&0xffff,"h":(wh>>16)&0xffff,
                    "off":dataPtr-0x60000000+0x1000})
    return out

def alpha_palette(a0,a1):
    p=[0]*8; p[0],p[1]=a0,a1
    if a0>a1:
        for k in range(1,7): p[1+k]=((7-k)*a0+k*a1)//7
    else:
        for k in range(1,6): p[1+k]=((5-k)*a0+k*a1)//5
        p[6],p[7]=0,255
    return p

def decode_cell(data,off,W,H,i):
    col=i%COLS; row=i//COLS
    x0=col*CW; y0=row*CH; x1=min(W,x0+CW); y1=min(H,y0+CH)
    BW=W//4; rw=x1-x0; rh=y1-y0; out=[0]*(rw*rh)
    for by in range(y0//4,(y1-1)//4+1):
        for bx in range(x0//4,(x1-1)//4+1):
            o=off+(by*BW+bx)*16
            pal=alpha_palette(data[o],data[o+1])
            bits=int.from_bytes(data[o+2:o+8],"little")
            for p in range(16):
                px=bx*4+(p&3); py=by*4+(p>>2)
                if px<x0 or px>=x1 or py<y0 or py>=y1: continue
                out[(py-y0)*rw+(px-x0)]=pal[(bits>>(3*p))&7]
    return out

def load(path):
    raw=open(path,"rb").read()
    data=zlib.decompress(raw[12:])
    return raw, data, parse_textures(data)

def read_table(path):
    b=open(path,"rb").read(); n=struct.unpack("<I",b[:4])[0]
    return list(struct.unpack("<%dI"%n,b[4:4+n*4]))

def main(ch):
    old_raw,old_data,old_tex=load(os.path.join(WORK,"backup_deploy",OLD[ch]))
    new_raw,new_data,new_tex=load(os.path.join(WORK,f"fonts_{ch}_new.wtd"))
    print(f"[{ch}] 旧解压 {len(old_data)}B  新解压 {len(new_data)}B  长度一致: {len(old_data)==len(new_data)}")

    # 贴图清单对齐
    for a,b in zip(old_tex,new_tex):
        same=a["name"]==b["name"] and a["off"]==b["off"] and a["w"]==b["w"] and a["h"]==b["h"]
        print(f"   贴图 {a['name']!r} off={a['off']} {a['w']}x{a['h']} 结构一致: {same}")

    old_tab=read_table(DEP_TAB); new_tab=read_table(NEW_TAB)
    old_idx={c:i for i,c in enumerate(old_tab)}

    old_chs=[t for t in old_tex if "font_chs" in t["name"]][0]
    new_chs=[t for t in new_tex if "font_chs" in t["name"]][0]
    W,H=old_chs["w"],old_chs["h"]

    # B. 非 chs 贴图段逐字节一致
    print("\n-- 非中文字图未改校验 --")
    for t in old_tex:
        if "font_chs" in t["name"]: continue
        seg_old=old_data[t["off"]:t["off"]+old_chs["off"] if False else len(old_data)]
        # 用下一张贴图 off 界定区间更稳；这里直接比同 off 同尺寸段
        sz=(t["w"]//4)*(t["h"]//4)*16
        so=bytes(old_data[t["off"]:t["off"]+sz])
        sn=bytes(new_data[t["off"]:t["off"]+sz])
        print(f"   {t['name']!r} 段 {sz}B 一致: {so==sn}")

    # C. 表末全空 + 前 N 非空
    ncell=COLS*(H//CH)
    print(f"\n-- 格分布 (总格 {ncell}, 新表 {len(new_tab)}) --")
    inks_new=[]
    for i in range(ncell):
        a=decode_cell(new_data,new_chs["off"],W,H,i)
        inks_new.append(sum(1 for v in a if v>0))
    tail=inks_new[len(new_tab):]
    print(f"   表末 {len(tail)} 格全空: {all(v==0 for v in tail)}  末格墨量: {tail[:5]}")
    head=inks_new[:len(new_tab)]
    empty_head=[i for i,v in enumerate(head) if v==0]
    print(f"   前 {len(new_tab)} 格空槽: {len(empty_head)} {empty_head[:10]}")

    # E. 旧字搬格一致性
    print("\n-- 旧字搬格一致性(新包新索引 vs 旧包旧索引) --")
    diffs=[]; maxdiff=0; nbad=0
    for j,cp in enumerate(new_tab):
        if cp not in old_idx: continue
        oi=old_idx[cp]
        ao=decode_cell(old_data,old_chs["off"],W,H,oi)
        an=decode_cell(new_data,new_chs["off"],W,H,j)
        md=max(abs(x-y) for x,y in zip(ao,an))
        nz=sum(1 for x,y in zip(ao,an) if x!=y)
        diffs.append(md); maxdiff=max(maxdiff,md)
        if md>20: nbad+=1
    print(f"   比对旧字 {len(diffs)}  最大像素差 {maxdiff}  超阈(>20) {nbad}")
    if diffs:
        print(f"   差分布: 0={diffs.count(0)} 1-5={sum(1 for d in diffs if 1<=d<=5)} 6-20={sum(1 for d in diffs if 6<=d<=20)} >20={sum(1 for d in diffs if d>20)}")

    # D. 44 新字墨量与 bin 比对
    print("\n-- 新字校验 --")
    man={}
    with open(os.path.join(WORK,"render_manifest.tsv"),encoding="utf-8-sig") as f:
        for r in csv.DictReader(f,delimiter="\t"):
            man[int(r["码位"].replace("U+",""),16)]=r
    bad=0
    for cp,r in man.items():
        j=new_tab.index(cp)
        an=decode_cell(new_data,new_chs["off"],W,H,j)
        bin_a=list(open(os.path.join(GLY,f"U+{cp:04X}.bin"),"rb").read())
        md=max(abs(x-y) for x,y in zip(an,bin_a))
        ink=sum(1 for v in an if v>0)
        if md>20 or ink==0:
            bad+=1; print(f"   异常 U+{cp:04X} {r['字符']} 格{j} ink{ink} maxdiff{md}")
    print(f"   新字 {len(man)}  异常 {bad}")

if __name__=="__main__":
    main(sys.argv[1])
