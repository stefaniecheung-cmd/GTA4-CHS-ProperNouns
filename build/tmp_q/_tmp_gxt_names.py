# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

P1 = r"C:\Users\yy253\Desktop\GTA4汉化补丁2026-11-09\release\update\common\text\american.gxt"
P2 = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\zchs_base_tr.gxt"
P3 = r"C:\Game\Grand Theft Auto IV\common\text\american.gxt"

def names(p):
    tables, items = parse_gxt(p)
    if isinstance(tables, dict):
        return [k[0] if isinstance(k, tuple) else k for k in tables.keys()]
    return [t[0] if isinstance(t, tuple) else t for t in tables]

n1 = names(P1)
n2 = names(P2)
n3 = names(P3)
print("表数：补丁", len(n1), "我方", len(n2), "原版", len(n3))

s1, s2, s3 = set(n1), set(n2), set(n3)
print("\n原版 vs 我方 表名原样差异：", "只在原版", sorted(s3 - s2)[:20], "只在我方", sorted(s2 - s3)[:20])
print("\n原版 vs 补丁 表名原样差异：只在原版", sorted(s3 - s1)[:20], "只在补丁", sorted(s1 - s3)[:20])

# 忽略大小写后比
print("\n忽略大小写：原版 vs 我方", len(set(x.upper() for x in n3) ^ set(x.upper() for x in n2)))
print("忽略大小写：原版 vs 补丁", len(set(x.upper() for x in n3) ^ set(x.upper() for x in n1)))

# 找出具体大小写不同的表
low2 = {}
for x in n2: low2.setdefault(x.upper(), []).append(x)
low3 = {}
for x in n3: low3.setdefault(x.upper(), []).append(x)
diff = []
for k in set(low2) & set(low3):
    if low2[k] != low3[k]:
        diff.append((k, low3[k], low2[k]))
print("\n大小写不一致的表（原版 vs 我方）：", len(diff))
for d in diff:
    print("   ", d)
