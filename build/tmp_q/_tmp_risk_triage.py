# -*- coding: utf-8 -*-
import csv, io, os, collections
csv.field_size_limit(10**9)
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\cmp_assets"

def load(fn):
    p = os.path.join(OUT, fn)
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))

risk = load("风险_控制符_en基准.tsv")
orph = load("风险_独有键.tsv")
print("风险条数", len(risk), " 独有键", len(orph))

# 归一化差异模式
pat = collections.Counter()
by_kind = collections.Counter()
rows = []
for r in risk:
    kind = r["类别"]; by_kind[kind] += 1
    lost = tuple(sorted(x for x in r["我方缺失"].split(",") if x and x != "-"))
    extra = tuple(sorted(x for x in r["我方多出"].split(",") if x and x != "-"))
    pat[(kind, lost, extra)] += 1
    rows.append((r["章节"], r["表"], r["CRC"], kind, lost, extra, r["英文原文"], r["我方定稿"]))

print("\n=== 类别 ===", dict(by_kind))
print("\n=== 差异模式 Top 25（类别 / 缺失 / 多出 / 条数）===")
for (kind, lost, extra), n in pat.most_common(25):
    print(f"  {n:4d}  {kind:8s} 缺={lost} 多={extra}")

# 假阳性排查：EN 为空 / 含 tab / 纯控制符
junk = [r for r in risk if not r["英文原文"].strip() or "\t" in r["英文原文"]]
print("\n疑似假阳性(EN空/含tab):", len(junk))
for r in junk[:10]:
    print("  ", r["章节"], r["表"], r["CRC"], repr(r["英文原文"][:40]), "->", repr(r["我方定稿"][:40]))

# 独有键明细
print("\n=== 独有键明细 ===")
for r in orph:
    print("  ", r["章节"], r["表"], r["CRC"], r["v10是否有"], repr(r["我方定稿"][:50]), "| EN:", repr(r["corpus英文"][:40]))

# 人读精简表落盘
with io.open(os.path.join(OUT, "风险_精简复核.tsv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["章节","表","CRC","类别","我方缺失","我方多出","英文原文","我方定稿"])
    for r in rows:
        w.writerow([r[0],r[1],r[2],r[3],"+".join(r[4]) or "-","+".join(r[5]) or "-",r[6],r[7]])
print("\n精简表已写: 风险_精简复核.tsv")
