# -*- coding: utf-8 -*-
import os, struct, zlib, sys
G=r"C:\Game\Grand Theft Auto IV"
WORK=os.path.join(G,"gta4-chs","build","font_work")
sys.path.insert(0,r"C:\Game\gta4-chs\build\tmp_q")

def read_table(p):
    b=open(p,"rb").read(); n=struct.unpack("<I",b[:4])[0]
    return list(struct.unpack("<%dI"%n,b[4:4+n*4]))

old=read_table(os.path.join(G,"plugins","GTA4.CHS","char_table.dat"))
new=read_table(os.path.join(WORK,"char_table_new.dat"))
oi={c:i for i,c in enumerate(old)}
print("旧",len(old),"新",len(new))
print("\n新表尾 44 (索引 3580..3623) 归属:")
tail=new[3580:]
in_old=[c in oi for c in tail]
print("  在旧表:",sum(in_old),"  新字:",len(in_old)-sum(in_old))
print("  尾码点:", [hex(c) for c in tail[:6]], "...", [hex(c) for c in tail[-6:]])

# 新字在新表的索引分布
man_new=[c for c in new if c not in oi]
print("\n新字数:",len(man_new),"索引范围:", new.index(man_new[0]), "..", new.index(man_new[-1]))

# 检查旧表最大码点 vs 新表
print("\n旧表最大 5:", [hex(c) for c in old[-5:]])
print("新表最大 5:", [hex(c) for c in new[-5:]])

# 排序后旧字 j 与 oi 的偏移样本
print("\n旧字 j vs oi 偏移样本(前20个在新表中的旧字):")
cnt=0
for j,c in enumerate(new):
    if c in oi:
        if cnt<20: print(f"  j={j} oi={oi[c]} delta={j-oi[c]} {hex(c)}")
        cnt+=1
