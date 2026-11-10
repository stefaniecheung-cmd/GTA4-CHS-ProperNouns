# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

P1 = r"C:\Users\yy253\Desktop\GTA4汉化补丁2026-11-09\release\update\common\text\american.gxt"
P2 = r"C:\Game\gta4-chs\build\zchs_base_tr.gxt"
P3 = r"C:\Game\Grand Theft Auto IV\common\text\american.gxt"

def info(p, label):
    try:
        tables, items = parse_gxt(p)
        tnames = [t for t in tables]
        print(f"\n== {label} ==")
        print("  表数", len(tables) if not isinstance(tables, dict) else len(tables))
        print("  条目数", len(items))
        if isinstance(tables, dict):
            print("  表名样例", list(tables.keys())[:8])
        else:
            print("  表名样例", tnames[:8])
        cjk = sum(1 for _, _, tx in items if any('\u4e00' <= ch <= '\u9fff' for ch in str(tx)))
        print("  含中文字符串条目", cjk)
        print("  前 3 条", [(t, c, str(x)[:60]) for t, c, x in items[:3]])
        return tables, items
    except Exception as e:
        print(f"\n== {label} == 解析失败: {e}")
        return None, None

t1, i1 = info(P1, "补丁 american.gxt")
t2, i2 = info(P2, "我方 zchs_base_tr.gxt")
t3, i3 = info(P3, "原版 american.gxt")

if i1 and i2:
    n1 = set((tb, (c if isinstance(c,int) else int(c,16))) for tb,c,_ in i1)
    n2 = set((tb, (c if isinstance(c,int) else int(c,16))) for tb,c,_ in i2)
    print("\n键集合完全相同？", n1 == n2, "| 只在补丁有", len(n1-n2), "| 只在我方有", len(n2-n1))
    if n1-n2:
        print("  只在补丁有样例", list(n1-n2)[:8])
    if n2-n1:
        print("  只在我方有样例", list(n2-n1)[:8])
