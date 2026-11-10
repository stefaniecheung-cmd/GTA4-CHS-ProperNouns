# -*- coding: utf-8 -*-
"""补充统计：我方独有键、我方 vs 英文基线新译量、控制码守恒抽检。"""
import sys, os, re, collections
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
MINE = os.path.join(G, "gta4-chs", "build")
BK = os.path.join(G, "_chs_backup_20261110")
V10 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"

CHAPS = [
    ("本体",  os.path.join(MINE, "zchs_base_tr.gxt"),
              os.path.join(V10, "update", "common", "text", "american.gxt"),
              os.path.join(BK, "update", "common", "text", "american.gxt")),
    ("TLAD",  os.path.join(MINE, "zchs_TLAD_tr.gxt"),
              os.path.join(V10, "update", "TLAD", "common", "text", "american.gxt"),
              os.path.join(BK, "update", "TLAD", "common", "text", "american.gxt")),
    ("TBoGT", os.path.join(MINE, "zchs_TBoGT_tr.gxt"),
              os.path.join(V10, "update", "TBoGT", "common", "text", "american.gxt"),
              os.path.join(BK, "update", "TBoGT", "common", "text", "american.gxt")),
]
def has_cjk(s): return any('\u4e00' <= c <= '\u9fff' for c in s)
def load(p):
    _, es, d = None, None, {}
    tables, entries = parse_gxt(p)
    for t, crc, txt in entries:
        d[(t, crc)] = txt
    return d

CTRL = re.compile(r"~[a-zA-Z0-9_]+~|%[sd]")
for tag, mp, v10p, enp in CHAPS:
    M, V, E = load(mp), load(v10p), load(enp)
    only_m = [k for k in M if k not in V]
    print("=" * 70)
    print(f"【{tag}】我方独有键 {len(only_m)}")
    for t, crc in only_m[:30]:
        print(f"  [{t}] {crc:08X}  {M[(t,crc)][:60]}")
    # 我方 vs 英文基线
    new_from_en = 0
    both_cjk = 0
    mine_cjk = sum(1 for x in M.values() if has_cjk(x))
    for k, m in M.items():
        e = E.get(k)
        if e is None: continue
        if not has_cjk(e) and has_cjk(m): new_from_en += 1
        elif has_cjk(e) and has_cjk(m): both_cjk += 1
    print(f"  我方含中文 {mine_cjk}；其中原版无中文→我方译出 {new_from_en}；原版已有中文基底→我方沿用/润色 {both_cjk}")
    # 控制码守恒抽检（我方 vs v10 不同条目）
    bad = 0; checked = 0
    for k, m in M.items():
        v = V.get(k)
        if v is None or m == v: continue
        checked += 1
        if collections.Counter(CTRL.findall(v)) != collections.Counter(CTRL.findall(m)):
            bad += 1
    print(f"  控制码/占位符守恒：抽检 {checked} 条差异，多重集不一致 {bad} 条")
