# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
MINE = os.path.join(G, "gta4-chs", "build")
BK = os.path.join(G, "_chs_backup_20261110")

chaps = [
    ("base",  os.path.join(G, "update", "common", "text", "american.gxt"),
              os.path.join(MINE, "zchs_base_tr.gxt"),
              os.path.join(BK, "update", "common", "text", "american.gxt")),
    ("TLAD",  os.path.join(G, "update", "TLAD", "common", "text", "american.gxt"),
              os.path.join(MINE, "zchs_TLAD_tr.gxt"),
              os.path.join(BK, "update", "TLAD", "common", "text", "american.gxt")),
    ("TBoGT", os.path.join(G, "update", "TBoGT", "common", "text", "american.gxt"),
              os.path.join(MINE, "zchs_TBoGT_tr.gxt"),
              os.path.join(BK, "update", "TBoGT", "common", "text", "american.gxt")),
]

def load(p):
    tables, entries = parse_gxt(p)
    d = {}
    for t, crc, txt in entries:
        d[(t, crc)] = txt
    return len(tables), len(entries), d

for tag, dep, mine, bk in chaps:
    print("=" * 70)
    print("章节", tag)
    for label, p in (("deploy", dep), ("mine ", mine), ("pristine", bk)):
        if not os.path.exists(p):
            print("  %s 缺失 %s" % (label, p)); continue
        nt, ne, d = load(p)
        print("  %s 表=%-4d 条=%-6d  %s" % (label, nt, ne, os.path.basename(p)))
    if not (os.path.exists(dep) and os.path.exists(mine)):
        continue
    _, _, D = load(dep)
    _, _, M = load(mine)
    only_m = [k for k in M if k not in D]
    only_d = [k for k in D if k not in M]
    diff = [k for k in M if k in D and M[k] != D[k]]
    print("  差异: mine独有=%d  deploy独有=%d  文本不同=%d" % (len(only_m), len(only_d), len(diff)))
    for k in diff[:6]:
        print("    [%s] %08X" % (k[0], k[1]))
        print("      deploy: %s" % D[k][:60])
        print("      mine  : %s" % M[k][:60])
