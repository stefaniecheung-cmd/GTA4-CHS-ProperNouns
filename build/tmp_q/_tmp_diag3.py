# -*- coding: utf-8 -*-
import os, struct, zlib, csv
G=r"C:\Game\Grand Theft Auto IV"
WORK=os.path.join(G,"gta4-chs","build","font_work")
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
def dec(d,off,W,H,x0,y0,x1,y1):
    BW=W//4;rw=x1-x0;rh=y1-y0;o=[0]*(rw*rh)
    for by in range(y0//4,(y1-1)//4+1):
        for bx in range(x0//4,(x1-1)//4+1):
            q=off+(by*BW+bx)*16;pl=pal(d[q],d[q+1]);bits=int.from_bytes(d[q+2:q+8],"little")
            for p in range(16):
                px=bx*4+(p&3);py=by*4+(p>>2)
                if px<x0 or px>=x1 or py<y0 or py>=y1:continue
                o[(py-y0)*rw+(px-x0)]=pl[(bits>>(3*p))&7]
    return o
def rtab(p):
    b=open(p,"rb").read();n=struct.unpack("<I",b[:4])[0]
    return list(struct.unpack("<%dI"%n,b[4:4+n*4]))

raw=open(os.path.join(WORK,"backup_deploy","fonts_pc.wtd"),"rb").read()
data=zlib.decompress(raw[12:]); tex=parse(data)
chs=[t for t in tex if t["off"]==4096][0]; W,H=chs["w"],chs["h"]; off=chs["off"]
old=rtab(os.path.join(G,"plugins","GTA4.CHS","char_table.dat"))
new=rtab(os.path.join(WORK,"char_table_new.dat"))
oi={c:i for i,c in enumerate(old)}

plane=bytearray(W*H)
empty=[]
for j,cp in enumerate(new):
    col=j%COLS;row=j//COLS;x0=col*CW;y0=row*CH;x1=min(W,x0+CW);y1=min(H,y0+CH)
    if cp in oi:
        a=dec(data,off,W,H,x0,y0,x1,y1)
    else:
        a=list(open(os.path.join(WORK,"glyphs",f"U+{cp:04X}.bin"),"rb").read())
    rw=x1-x0;rh=y1-y0
    for y in range(rh):
        base=(y0+y)*W+x0
        plane[base:base+rw]=a[y*CW:y*CW+rw]
    ink=sum(1 for v in a if v>0)
    if ink==0: empty.append((j,hex(cp),"old" if cp in oi else "new"))

print("平面构建完成, 空槽:",len(empty))
for e in empty[:50]: print("  ",e)

# 直接看平面格 3580 墨量
def plane_ink(i):
    col=i%COLS;row=i//COLS;x0=col*CW;y0=row*CH;x1=min(W,x0+CW);y1=min(H,y0+CH)
    s=0
    for y in range(y1-y0):
        for x in range(x1-x0):
            if plane[(y0+y)*W+x0+x]>0:s+=1
    return s
print("\n平面格墨量抽样: 3579=",plane_ink(3579)," 3580=",plane_ink(3580)," 3600=",plane_ink(3600)," 3623=",plane_ink(3623))
print("W,H=",W,H,"plane len=",len(plane))
