# -*- coding: utf-8 -*-
"""以英文原文为基准，核对最终定稿 src_*_tr.tsv 的控制符/占位符守恒；查独有键。"""
import sys, os, re, csv, io, collections
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
B = os.path.join(G, "gta4-chs", "build")
D = os.path.join(G, "gta4-chs", "data")
BK = os.path.join(G, "_chs_backup_20261110")
V10 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
OUT = os.path.join(B, "cmp_assets")
os.makedirs(OUT, exist_ok=True)

CODE = re.compile(r"~[A-Za-z0-9_]+~")
PLACE = re.compile(r"%[sd]")
# 颜色/说话人/重置码（非按键、非占位、非换行）
COLOR = {"~s~", "~z~", "~b~", "~r~", "~y~", "~c~", "~x~", "~a~", "~m~", "~g~",
         "~e~", "~w~", "~k~", "~l~", "~d~", "~f~", "~h~", "~i~", "~j~", "~o~",
         "~p~", "~q~", "~t~", "~u~", "~v~", "~1~", "~2~", "~3~", "~4~"}

CHAPS = [
    ("base",  os.path.join(B, "src_base_tr.tsv"),
              os.path.join(V10, "update", "common", "text", "american.gxt"),
              os.path.join(BK, "common", "text", "american.gxt")),
    ("TLAD",  os.path.join(B, "src_TLAD_tr.tsv"),
              os.path.join(V10, "update", "TLAD", "common", "text", "american.gxt"),
              os.path.join(BK, "update", "TLAD", "common", "text", "american.gxt")),
    ("TBoGT", os.path.join(B, "src_TBoGT_tr.tsv"),
              os.path.join(V10, "update", "TBoGT", "common", "text", "american.gxt"),
              os.path.join(BK, "update", "TBoGT", "common", "text", "american.gxt")),
]

def load_corpus(ch):
    m = {}
    p = os.path.join(D, f"corpus_{ch}.tsv")
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            m[r["crc"].upper()] = r.get("english", "")
    return m

def load_gxt(p):
    _, es = parse_gxt(p)
    return {(t, int(c)): x for t, c, x in es}

def cc(s): return collections.Counter(CODE.findall(s))
def pc(s): return collections.Counter(PLACE.findall(s))

risk_rows, orphan_rows = [], []
lost_all, extra_all = collections.Counter(), collections.Counter()
by_kind = collections.Counter()

for ch, src_p, v10p, enp in CHAPS:
    corp = load_corpus(ch)
    V = load_gxt(v10p); E = load_gxt(enp)
    en_keys = {(t, c) for t, c in E}
    v10_keys = {(t, c) for t, c in V}
    rows = []
    with open(src_p, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows.append((r["table"], int(r["crc"], 16), r["text"]))
    print(f"【{ch}】定稿 {len(rows)}；corpus {len(corp)}；原版键 {len(en_keys)}；v10 键 {len(v10_keys)}")
    for t, crc, zh in rows:
        key = (t, crc)
        if key not in en_keys:
            orphan_rows.append((ch, t, "%08X" % crc, zh,
                                "v10有" if key in v10_keys else "v10无",
                                corp.get("%08X" % crc, "")))
        en = corp.get("%08X" % crc, "")
        if not en: continue
        ce, cz = cc(en), cc(zh)
        cz_n = cz.copy()
        extra_n = cz_n["~n~"] - ce["~n~"]
        if extra_n > 0:
            for _ in range(extra_n): cz_n["~n~"] -= 1
        pe, pz = pc(en), pc(zh)
        if ce != cz_n or pe != pz:
            lost = list((ce - cz_n).elements()); extra = list((cz_n - ce).elements())
            lost_p = list((pe - pz).elements()); extra_p = list((pz - pe).elements())
            lost_all.update(lost + lost_p); extra_all.update(extra + extra_p)
            if lost_p or extra_p: kind = "占位符"
            elif any("INPUT" in x or "PAD" in x for x in lost+extra): kind = "按键图标"
            else: kind = "颜色/说话人码"
            by_kind[kind] += 1
            risk_rows.append((ch, t, "%08X" % crc, kind, en, V.get(key, ""), zh,
                              ",".join(lost+lost_p) or "-", ",".join(extra+extra_p) or "-"))

print("\n=== 风险分类 ===", dict(by_kind))
print("=== 缺失码 Top ===", lost_all.most_common(20))
print("=== 多出码 Top ===", extra_all.most_common(20))

with io.open(os.path.join(OUT, "风险_控制符_en基准.tsv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["章节", "表", "CRC", "类别", "英文原文", "v1.0成品", "我方定稿", "我方缺失", "我方多出"])
    w.writerows(risk_rows)
with io.open(os.path.join(OUT, "风险_独有键.tsv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["章节", "表", "CRC", "我方定稿", "v10是否有", "corpus英文"])
    w.writerows(orphan_rows)

print("\n风险条目:", len(risk_rows), " 独有键:", len(orphan_rows))

# 按键/占位符全量打印；颜色码只打非 ~s~ 的
print("\n--- 按键/占位符风险（全量）---")
for r in risk_rows:
    if r[3] != "颜色/说话人码":
        print(f"  [{r[0]} {r[1]} {r[2]} {r[3]}] 缺:{r[7]} 多:{r[8]}")
        print(f"     EN : {r[4][:70]}")
        print(f"     v10: {r[5][:70]}")
        print(f"     我方: {r[6][:70]}")
print("\n--- 颜色码非 ~s~ 出入（抽样）---")
n = 0
for r in risk_rows:
    if r[3] == "颜色/说话人码" and ("~s~" not in r[7] or "~s~" not in r[8] or r[7] != "-" and r[8] != "-"):
        if r[7] == "~s~" and r[8] == "-" or r[7] == "-" and r[8] == "~s~": continue
        print(f"  [{r[0]} {r[1]} {r[2]}] 缺:{r[7]} 多:{r[8]} | EN {r[4][:40]} | 我方 {r[6][:40]}")
        n += 1
        if n >= 25: break
