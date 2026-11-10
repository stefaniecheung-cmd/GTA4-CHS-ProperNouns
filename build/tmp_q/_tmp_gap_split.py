# -*- coding: utf-8 -*-
"""97 条缺口切分：拍板保留 vs 待决策候选；候选再按原因标注。"""
import csv, io, os, re, collections
csv.field_size_limit(10**9)
B = r"C:\Game\gta4-chs\build"
SRC = os.path.join(B, r"cmp_assets\未译_我方缺口_v10译了.tsv")
OUT = os.path.join(B, r"cmp_assets\待决策缺口.tsv")

CODE = re.compile(r"~[A-Za-z0-9_]+~")
NAME_TOK = {"Niko", "Nicky", "Roman", "Bellic", "B"}
KEEP_EN = {"Rusty Brown", "Eyediditmy Way", "Deadbeats", "Swingers", "Teeker", "BANDIT!"}

def plain(s): return CODE.sub("", s).strip().rstrip(".,!?，。！？ ").strip()

def is_name(zh, en):
    for s in (zh, en):
        toks = re.findall(r"[A-Za-z]+", plain(s))
        if toks and all(t in NAME_TOK for t in toks) and len(plain(s)) <= 20:
            return True
    return False

def is_serbian(zh, en):
    return plain(zh).startswith(("Tvoja", "Moj")) or plain(en).startswith(("Tvoja", "Moj"))

corpus = {}
for ch in ("base", "TLAD", "TBoGT"):
    with io.open(os.path.join(B, r"..\data", f"corpus_{ch}.tsv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            corpus[(ch, r["crc"].upper())] = r["english"]

rows = list(csv.DictReader(io.open(SRC, encoding="utf-8-sig"), delimiter="\t"))
keep, cand = [], []
for r in rows:
    zh = r["我方(英文)"]; en = corpus.get((r["章节"], r["CRC"]), "")
    pl = plain(zh)
    if is_name(zh, en):
        tag = "保留-主角人名(Niko/Roman)"
    elif is_serbian(zh, en):
        tag = "保留-塞语信(白名单)"
    elif pl in KEEP_EN:
        tag = "保留-KEEP_EN专名"
    elif pl == "?":
        tag = "候选-译文占位问号(bug,应补译)"
    elif CODE.sub("", zh).strip() in ("", "~z~", "~z~~s~", "~z~~x~"):
        tag = "候选-原文正文为空(v10脑补,建议不补)"
    else:
        tag = "候选-普通词/粗口/绰号"
    rec = (tag, r, en)
    (keep if tag.startswith("保留") else cand).append(rec)

print("保留合计:", len(keep), " 候选合计:", len(cand))
for k, n in collections.Counter(t for t, _, _ in keep).most_common(): print("  ", k, n)
for k, n in collections.Counter(t for t, _, _ in cand).most_common(): print("  ", k, n)

with io.open(OUT, "w", encoding="utf-8-sig", newline="") as g:
    w = csv.writer(g, delimiter="\t")
    w.writerow(["分类", "章节", "表", "CRC", "我方(英文)", "v10译文", "corpus英文"])
    for tag, r, en in keep + cand:
        w.writerow([tag, r["章节"], r["表"], r["CRC"], r["我方(英文)"], r["v10译文"], en])
print("->", OUT)
print("\n=== 候选明细 ===")
for tag, r, en in cand:
    print(f"[{tag}] {r['章节']} {r['CRC']}")
    print(f"   EN : {en[:70]!r}")
    print(f"   我方: {r['我方(英文)'][:70]!r}")
    print(f"   v10: {r['v10译文'][:70]!r}")
