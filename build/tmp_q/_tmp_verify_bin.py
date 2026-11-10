# -*- coding: utf-8 -*-
"""二值笔画一致性：旧字/新字 mask 的 IoU、丢失像素、冒墨像素。"""
import os, sys, csv, struct, zlib
from PIL import Image
G=r"C:\Game\Grand Theft Auto IV"
WORK=os.path.join(G,"gta4-chs","build","font_work")
GLY=os.path.join(WORK,"glyphs")
OLD={"pc":"fonts_pc.wtd","TLAD":"fonts_TLAD.wtd","TBoGT":"fonts_TBoGT.wtd"}
DEP_TAB=os.path.join(G,"plugins","GTA4.CHS","char_table.dat")
NEW_TAB=os.path.join(WORK,"char_table_new.dat")
CW,CH,COLS=64,66,64; VTABLE=0xb6f0ee97

def parse(d):
    out=[]
    for o in range(0,0x1000-0x50+1,4):
        if struct.unpack_from("<I",d,o)[0]!=VTABLE: continue
        dP=struct.unpack_from("<I",d,o+0x48)[0]
        if dP<0x60000000: continue
        wh=struct.unpack_from("<I",d,o+0x1c)[0]
        out.append({"w":wh&0xffff,"h":(wh>>16)&0xffff,"off":dP-0x60000000+0x1000})
    return out
def pal(a0,a1):
    p=[0]*8;p[0],p[1]=a0,a1
    if a0>a1:
        for k in range(1,7):p[1+k]=((7-k)*a0+k*a1)//7
    else:
        for k in range(1,6):p[1+k]=((5-k)*a0+k*a1)//5
        p[6],p[7]=0,255
    return p
def dec(d,off,W,H,i):
    col=i%COLS;row=i//COLS;x0=col*CW;y0=row*CH;x1=min(W,x0+CW);y1=min(H,y0+CH)
    BW=W//4;rw=x1-x0;rh=y1-y0;o=[0]*(rw*rh)
    for by in range(y0//4,(y1-1)//4+1):
        for bx in range(x0//4,(x1-1)//4+1):
            q=off+(by*BW+bx)*16;pl=pal(d[q],d[q+1]);bits=int.from_bytes(d[q+2:q+8],"little")
            for p in range(16):
                px=bx*4+(p&3);py=by*4+(p>>2)
                if px<x0 or px>=x1 or py<y0 or py>=y1:continue
                o[(py-y0)*rw+(px-x0)]=pl[(bits>>(3*p))&7]
    return o
def load(p):
    raw=open(p,"rb").read();d=zlib.decompress(raw[12:]);return d,parse(d)
def rtab(p):
    b=open(p,"rb").read();n=struct.unpack("<I",b[:4])[0]
    return list(struct.unpack("<%dI"%n,b[4:4+n*4]))

def main(ch):
    od,ot=load(os.path.join(WORK,"backup_deploy",OLD[ch]))
    nd,nt=load(os.path.join(WORK,f"fonts_{ch}_new.wtd"))
    old=rtab(DEP_TAB);new=rtab(NEW_TAB);oi={c:i for i,c in enumerate(old)}
    otc=[t for t in ot if t["off"]==4096][0];ntc=[t for t in nt if t["off"]==4096][0]
    W,H=otc["w"],otc["h"]

    def mask(a): return [1 if v>0 else 0 for v in a]
    worst=[]
    iou_min=1.0; loss_max=0; ink_old_tot=0; ink_new_tot=0
    n=0
    for j,cp in enumerate(new):
        an=dec(nd,ntc["off"],W,H,j)
        if cp in oi:
            ao=dec(od,otc["off"],W,H,oi[cp])
        else:
            ao=list(open(os.path.join(GLY,f"U+{cp:04X}.bin"),"rb").read())
        mo,mn=mask(ao),mask(an)
        inter=sum(x&y for x,y in zip(mo,mn))
        union=sum(x|y for x,y in zip(mo,mn))
        loss=sum(1 for x,y in zip(mo,mn) if x and not y)
        add=sum(1 for x,y in zip(mo,mn) if y and not x)
        ink_old_tot+=sum(mo); ink_new_tot+=sum(mn)
        iou=inter/union if union else 1.0
        iou_min=min(iou_min,iou); loss_max=max(loss_max,loss)
        worst.append((iou,loss,add,cp,j))
        n+=1
    worst.sort(key=lambda r:r[0])
    print(f"[{ch}] 比对 {n} 字")
    print(f"  笔画墨量 旧 {ink_old_tot} 新 {ink_new_tot}  偏差 {abs(ink_new_tot-ink_old_tot)/ink_old_tot*100:.2f}%")
    print(f"  最低 IoU {iou_min:.4f}  单字最大丢失像素 {loss_max}")
    print("  IoU 最低 12 字:")
    for iou,loss,add,cp,j in worst[:12]:
        print(f"    U+{cp:04X} IoU={iou:.3f} 丢失{loss} 冒墨{add} 格{j}")
    # 存最差 4 字新旧对照
    prev=os.path.join(WORK,"verify_preview");os.makedirs(prev,exist_ok=True)
    for k,(iou,loss,add,cp,j) in enumerate(worst[:4]):
        an=dec(nd,ntc["off"],W,H,j)
        if cp in oi: ao=dec(od,otc["off"],W,H,oi[cp])
        else: ao=list(open(os.path.join(GLY,f"U+{cp:04X}.bin"),"rb").read())
        im=Image.new("L",(CW*2,CH),0)
        im.putdata(ao+an)
        im.save(os.path.join(prev,f"worst{k}_U+{cp:04X}.png"))
    print("  对照图:",prev)

if __name__=="__main__":
    main(sys.argv[1])
