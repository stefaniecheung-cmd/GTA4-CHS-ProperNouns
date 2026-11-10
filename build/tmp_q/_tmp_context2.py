# -*- coding: utf-8 -*-
import io, os, sys, csv
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt
ROOT = r"C:\Game\Grand Theft Auto IV\gta4-chs"
V10 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"

def gxt_map(p):
    _, es = parse_gxt(p)
    return {("%08X"%c): x for t,c,x in es}

# 4FC055AF 英文（corpus）+ 我方
print("=== 4FC055AF (TLAD) 对照 ===")
with io.open(os.path.join(ROOT,"data","corpus_TLAD.tsv"), encoding="utf-8-sig") as f:
    head=f.readline().rstrip("\n").split("\t"); ix={k:i for i,k in enumerate(head)}
    for line in f:
        q=line.rstrip("\n").split("\t")
        if len(q)!=len(head): continue
        if q[ix["crc"]].strip().upper()=="4FC055AF":
            print("EN:", repr(q[ix["english"]]))
            print("zh_cur:", repr(q[ix["chinese_current"]]))

ours = gxt_map(os.path.join(ROOT,"build","zchs_TLAD_tr.gxt"))
print("我方:", repr(ours.get("4FC055AF")))

# E8506E8D v10 成品链接写法
print("\n=== E8506E8D v10 成品 ===")
v10 = gxt_map(os.path.join(V10,"update","TLAD","common","text","american.gxt"))
print("v10:", repr(v10.get("E8506E8D")))
ours_t = gxt_map(os.path.join(ROOT,"build","zchs_TLAD_tr.gxt"))
print("我方:", repr(ours_t.get("E8506E8D")))

# 同 CRC TBoGT 我方译文（对照已译广告段）
print("\n=== E8506E8D TBoGT 我方 ===")
ours_b = gxt_map(os.path.join(ROOT,"build","zchs_TBoGT_tr.gxt"))
print(repr(ours_b.get("E8506E8D")))
