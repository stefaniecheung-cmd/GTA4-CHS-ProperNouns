# -*- coding: utf-8 -*-
"""对照 v10 成品，复核我方"多 s-句中切断"条目：v10 同句是否也在该处闭合。"""
import sys, os, re, csv, io, collections
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt
G = r"C:\Game\Grand Theft Auto IV"
B = os.path.join(G, "gta4-chs", "build")
V10 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
CODE = re.compile(r"~[A-Za-z0-9_]+~")

def gxt_map(p):
    _, es = parse_gxt(p)
    return {("%08X"%c): x for t,c,x in es}

V = {"base": gxt_map(os.path.join(V10,"update","common","text","american.gxt")),
     "TLAD": gxt_map(os.path.join(V10,"update","TLAD","common","text","american.gxt")),
     "TBoGT": gxt_map(os.path.join(V10,"update","TBoGT","common","text","american.gxt"))}
Z = {"base": gxt_map(os.path.join(B,"zchs_base_tr.gxt")),
     "TLAD": gxt_map(os.path.join(B,"zchs_TLAD_tr.gxt")),
     "TBoGT": gxt_map(os.path.join(B,"zchs_TBoGT_tr.gxt"))}

p = os.path.join(B, "cmp_assets", "风险_s码_分级.tsv")
rows = list(csv.DictReader(io.open(p, encoding="utf-8-sig"), delimiter="\t"))
cut = [r for r in rows if r["分级"] in ("多s-句中切断(串色风险)", "缺s-句中未闭合(串色风险)")]
print("句中出入 旧分级条数:", len(cut))

# 我方与 v10 的 s 数量对比
same, z_more, v10_more, v10_no = 0, 0, 0, 0
diff_rows = []
for r in cut:
    ch = r["章节"]; crc = r["CRC"]
    zv = Z[ch].get(crc, ""); vv = V[ch].get(crc)
    zs = zv.count("~s~"); vs = (vv or "").count("~s~")
    if vv is None: v10_no += 1; continue
    if zs == vs: same += 1
    elif zs > vs: z_more += 1; diff_rows.append((ch, crc, zv, vv, zs, vs))
    else: v10_more += 1

print(f"v10无此键: {v10_no}；我方与v10的s数相同: {same}；我方s更多: {z_more}；v10 s更多: {v10_more}")
print("\n=== 我方 s 比 v10 多的条目（疑似多余切断）===")
for ch, crc, zv, vv, zs, vs in diff_rows:
    print(f"\n[{ch} {crc}] 我方s={zs} v10s={vs}")
    print(f"  我方: {zv[:80]!r}")
    print(f"  v10 : {vv[:80]!r}")
