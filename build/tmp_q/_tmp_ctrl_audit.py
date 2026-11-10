# -*- coding: utf-8 -*-
"""细分控制码不一致：区分允许的 ~n~ 增减 与 占位符/按键图标丢失。"""
import sys, os, re, collections
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
MINE = os.path.join(G, "gta4-chs", "build")
BK = os.path.join(G, "_chs_backup_20261110")
V10 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
CHAPS = [
    ("本体",  os.path.join(MINE, "zchs_base_tr.gxt"), os.path.join(V10, "update", "common", "text", "american.gxt"), os.path.join(BK, "update", "common", "text", "american.gxt")),
    ("TLAD",  os.path.join(MINE, "zchs_TLAD_tr.gxt"), os.path.join(V10, "update", "TLAD", "common", "text", "american.gxt"), os.path.join(BK, "update", "TLAD", "common", "text", "american.gxt")),
    ("TBoGT", os.path.join(MINE, "zchs_TBoGT_tr.gxt"), os.path.join(V10, "update", "TBoGT", "common", "text", "american.gxt"), os.path.join(BK, "update", "TBoGT", "common", "text", "american.gxt")),
]
def load(p):
    d = {}
    _, es = parse_gxt(p)
    for t, crc, txt in es: d[(t, crc)] = txt
    return d
CTRL = re.compile(r"~[a-zA-Z0-9_]+~|%[sd]")
PLACE = re.compile(r"%[sd]|~INPUT_[A-Z0-9_]+~|~PAD_[A-Z0-9_]+~")

grand = collections.Counter()
risk_rows = []
for tag, mp, v10p, enp in CHAPS:
    M, V, E = load(mp), load(v10p), load(enp)
    cat = collections.Counter()
    for k, m in M.items():
        v = V.get(k)
        if v is None or m == v: continue
        cv, cm = collections.Counter(CTRL.findall(v)), collections.Counter(CTRL.findall(m))
        if cv == cm: continue
        pv, pm = collections.Counter(PLACE.findall(v)), collections.Counter(PLACE.findall(m))
        only_n = (cv - cm == collections.Counter()) or (cm - cv == collections.Counter())
        # 把非 n~ 的差集剥离
        dv, dm = cv.copy(), cm.copy()
        dv.pop("~n~", None); dm.pop("~n~", None)
        if pv != pm:
            c = "占位符/按键图标不一致"
            risk_rows.append((tag, k[0], "%08X" % k[1], v[:50], m[:50], "+".join(pm-pv) or "-", "+".join(pv-pm) or "-"))
        elif dv != dm:
            c = "颜色/说话人码不一致"
        elif only_n:
            c = "仅换行 ~n~ 增减(允许)"
        else:
            c = "其它控制码不一致"
        cat[c] += 1; grand[c] += 1
    print(f"【{tag}】", dict(cat))

print("\n三章合计:", dict(grand))
print("\n占位符/按键图标不一致样例(前 25):")
for r in risk_rows[:25]:
    print(" ", r[0], r[1], r[2], "| v10:", r[3], "| 我方:", r[4], "| 我方多:", r[5], " v10多:", r[6])
print("\n占位符/按键图标不一致总数:", len(risk_rows))
