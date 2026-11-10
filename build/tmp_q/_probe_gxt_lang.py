# -*- coding: utf-8 -*-
import os, sys, re, struct
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt
G = r"C:\Game\Grand Theft Auto IV"
cjk = re.compile(r"[一-鿿]")

def gxt_stat(p, label):
    if not os.path.exists(p):
        print(f"{label}: 缺失"); return
    _, es = parse_gxt(p)
    ne = [e for e in es if e[2].strip()]
    zh = [e for e in ne if cjk.search(e[2])]
    zhc = sum(len(cjk.findall(e[2])) for e in ne)
    sample = [e[2].replace('\n',' ')[:30] for e in ne[:4]]
    print(f"{label:40} 条目={len(es):6} 中文条目={len(zh):5} 中文字={zhc}")
    print("    样例:", " | ".join(sample))

print("=== common / DLC 原版层 gxt ===")
gxt_stat(os.path.join(G, r"common\text\american.gxt"), "common 本体 american")
gxt_stat(os.path.join(G, r"TLAD\common\text\american.gxt"), "TLAD 层 american")
gxt_stat(os.path.join(G, r"TBoGT\common\text\american.gxt"), "TBoGT 层 american")

print("\n=== _chs_backup update 层备份（旧汉化?）===")
gxt_stat(os.path.join(G, r"_chs_backup_20261110\update\common\text\american.gxt"), "backup update 本体")
gxt_stat(os.path.join(G, r"_chs_backup_20261110\update\TLAD\common\text\american.gxt"), "backup update TLAD")
gxt_stat(os.path.join(G, r"_chs_backup_20261110\update\TBoGT\common\text\american.gxt"), "backup update TBoGT")

# 多语参照：french 应近 0 中文
gxt_stat(os.path.join(G, r"common\text\french.gxt"), "common french(参照)")
