# -*- coding: utf-8 -*-
import os, struct, zlib, sys
from PIL import Image
G=r"C:\Game\Grand Theft Auto IV"
WORK=os.path.join(G,"gta4-chs","build","font_work")
CW,CH,COLS=64,66,64
VTABLE=0xb6f0ee97

def parse(d):
    out=[]
    for o in range(0,0x1000-0x50+1,4):
        if struct.unpack_from("<I",d,o)[0]!=VTABLE: continue
        nP=struct.unpack_from("<I",d,o+0x14)[0]; wh=struct.unpack_from("<I",d,o+0x1c)[0]
        dP=struct.unpack_from("<I",d,o+0x48)[0]
        if dP<0x60000000: continue
        out.append({"name":d[o+0x20:o+0x24].decode("latin1"),"w":wh&0xffff,"h":(wh>>16)&0xffff,
                    "off":dP-0x60000000+0x1000})
    return out
def pal(a0,a1):
    p=[0]*8;p[0],p[1]=a0,a1
    if a0>a1:
        for k in range(1,7):p[1+k]=((7-k)*a0+k*a1)//7
    else:
        for k in range(1,6):p[1+k]=((5-k)*a0+k*a1)//5
        p[6],p[7]=0,255
    return p
def cell(d,off,W,H,i):
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
    raw=open(p,"rb").read();return zlib.decompress(raw[12:]),parse(zlib.decompress(raw[12:]))
def rtab(p):
    b=open(p,"rb").read();n=struct.unpack("<I",b[:4])[0]
    return list(struct.unpack("<%dI"%n,b[4:4+n*4]))

old_d,old_t=load(os.path.join(WORK,"backup_deploy","fonts_pc.wtd"))
new_d,new_t=load(os.path.join(WORK,"fonts_pc_new.wtd"))
old_tab=rtab(os.path.join(G,"plugins","GTA4.CHS","char_table.dat"))
new_tab=rtab(os.path.join(WORK,"char_table_new.dat"))
oi={c:i for i,c in enumerate(old_tab)}
ot=[t for t in old_t if t["off"]==4096][0]
nt=[t for t in new_t if t["off"]==4096][0]
W,H=ot["w"],ot["h"]

def save(a,path):
    im=Image.new("L",(CW,CH),0)
    im.putdata(a);im.save(path)

# 样本: 新表尾旧字 j=3580, 3623; 未顺移 j=100; 顺移旧字; 新字
samples=[]
for j in [0,100,593,594,1000,3580,3623]:
    cp=new_tab[j]; samples.append((f"j{j}_{hex(cp)}", cp, j, oi.get(cp)))
for tag,cp,j,oo in samples:
    an=cell(new_d,nt["off"],W,H,j)
    ink_n=sum(1 for v in an if v>0)
    line=f"{tag} 新包格{j} ink={ink_n}"
    if oo is not None:
        ao=cell(old_d,ot["off"],W,H,oo)
        line+=f" 旧包格{oo} ink={sum(1 for v in ao if v>0)}"
    print(line)
    save(an,os.path.join(WORK,f"diag_new_{tag}.png"))
    if oo is not None:
        save(ao,os.path.join(WORK,f"diag_old_{tag}.png"))
