# -*- coding: utf-8 -*-
import sys, io, os
csv = None
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
BK = os.path.join(G, "_chs_backup_20261110")
V10 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"

def load(p):
    _, es = parse_gxt(p)
    return {(t, "%08X" % c): x for t, c, x in es}

# 1) 7924D022 在各层 TBoGT gxt
print("=== 7924D022 (TBoGT EML111) 各层 ===")
layers = [
    ("备份update TBoGT", os.path.join(BK, "update", "TBoGT", "common", "text", "american.gxt")),
    ("v10 TBoGT", os.path.join(V10, "update", "TBoGT", "common", "text", "american.gxt")),
    ("我方定稿TBoGT", os.path.join(G, "gta4-chs", "build", "zchs_TBoGT_tr.gxt")),
]
for label, p in layers:
    if not os.path.exists(p):
        print(label, "文件不存在", p); continue
    M = load(p)
    hit = [(k, x) for k, x in M.items() if k[1] == "7924D022"]
    print(label, "命中", len(hit))
    for k, x in hit:
        print("   ", k, repr(x[:80]))

# 2) 7EB9E67F 在定稿 base gxt 实际文本
print("\n=== 7EB9E67F (base MAIN) 定稿 gxt 实际文本 ===")
M = load(os.path.join(G, "gta4-chs", "build", "zchs_base_tr.gxt"))
for k, x in M.items():
    if k[1] == "7EB9E67F":
        print(repr(x))
# 相邻键 7EBB7848 / 7ED5768C 文本是否被串改
for c in ("7EBB7848", "7ED5768C"):
    for k, x in M.items():
        if k[1] == c:
            print(c, repr(x[:60]))
