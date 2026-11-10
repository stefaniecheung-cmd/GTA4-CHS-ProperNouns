# -*- coding: utf-8 -*-
"""我方定稿 gxt  vs  v1.0 第三方成品  vs  英文原版基线，逐章对比出修改摘要。"""
import sys, os, re, json, io, collections
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

def has_cjk(s):
    return any('\u4e00' <= c <= '\u9fff' for c in s)

def load(p):
    if not os.path.exists(p):
        return None, 0, {}
    tables, entries = parse_gxt(p)
    d = {}
    for t, crc, txt in entries:
        d[(t, crc)] = txt
    return len(tables), len(entries), d

out_lines = []
def w(s=""):
    out_lines.append(s)

all_diff_rows = []

for tag, mp, v10p, enp in CHAPS:
    mt, mn, M = load(mp)
    vt, vn, V = load(v10p)
    et, en, E = load(enp)
    w("=" * 78)
    w(f"【{tag}】")
    w(f"  条数: 我方定稿 {mn}  |  v1.0 成品 {vn}  |  英文原版 {en}   (表数 {mt}/{vt}/{et})")

    if M is None or V is None:
        w("  缺文件，跳过"); continue

    keys = set(M) | set(V)
    same = diff = only_m = only_v = 0
    cat = collections.Counter()
    diff_rows = []
    for k in keys:
        m = M.get(k); v = V.get(k)
        if m is None:
            only_v += 1; continue
        if v is None:
            only_m += 1; continue
        if m == v:
            same += 1; continue
        diff += 1
        mc, vc = has_cjk(m), has_cjk(v)
        if not vc and mc:
            c = "英译中(我方新译)"
        elif vc and mc:
            c = "中文改译/润色"
        elif vc and not mc:
            c = "回退英文"
        else:
            c = "纯符号/标点差异"
        cat[c] += 1
        diff_rows.append((k[0], k[1], v, m, c))
        all_diff_rows.append((tag, k[0], "%08X" % k[1], v, m, c))

    w(f"  我方 vs v1.0: 相同 {same}  不同 {diff}  我方独有 {only_m}  v1.0独有 {only_v}")
    w("  差异归类:")
    for c, n in cat.most_common():
        w(f"    - {c}: {n}")

    # 我方 vs 英文基线
    if E:
        mine_cjk = sum(1 for x in M.values() if has_cjk(x))
        en_cjk = sum(1 for x in E.values() if has_cjk(x))
        v10_cjk = sum(1 for x in V.values() if has_cjk(x))
        w(f"  含中文条目: 我方 {mine_cjk}  |  v1.0 {v10_cjk}  |  原版 {en_cjk}")

    w("")
    w("  差异抽样（最多 12 条）:")
    for t, crc, v, m, c in diff_rows[:12]:
        w(f"    [{t} {crc:08X}] {c}")
        w(f"      v1.0 : {v[:70]}")
        w(f"      我方 : {m[:70]}")
    w("")

# 汇总
w("=" * 78)
w("【三章合计差异】")
tot = collections.Counter()
for r in all_diff_rows:
    tot[r[5]] += 1
for c, n in tot.most_common():
    w(f"  - {c}: {n}")
w(f"  差异条目总计: {len(all_diff_rows)}")

# 落盘
outdir = os.path.join(MINE, "cmp_assets")
os.makedirs(outdir, exist_ok=True)
md = os.path.join(outdir, "修改摘要.md")
with io.open(md, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

tsv = os.path.join(outdir, "差异明细.tsv")
with io.open(tsv, "w", encoding="utf-8-sig") as f:
    f.write("章节\t表\tCRC\tv1.0成品\t我方定稿\t归类\n")
    for tag, t, crc, v, m, c in all_diff_rows:
        f.write(f"{tag}\t{t}\t{crc}\t{v.replace(chr(9),' ').replace(chr(10),' ')}\t{m.replace(chr(9),' ').replace(chr(10),' ')}\t{c}\n")

print("\n".join(out_lines))
print("\n摘要 ->", md)
print("明细 ->", tsv, " 共", len(all_diff_rows), "条")
