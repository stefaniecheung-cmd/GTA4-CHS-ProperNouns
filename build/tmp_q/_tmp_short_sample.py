# -*- coding: utf-8 -*-
import csv, io, os, re, random, collections
csv.field_size_limit(10**9)
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
CODE = re.compile(r"~[A-Za-z0-9_]+~")
short = []
for ch in ("base", "TLAD", "TBoGT"):
    with io.open(os.path.join(B, f"src_{ch}_tr.tsv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r["text"]
            if any("\u4e00" <= x <= "\u9fff" for x in t):
                continue
            plain = CODE.sub("", t).strip()
            if 1 <= len(plain) <= 4:
                short.append((ch, r["crc"].upper(), plain))
print("短碎片(1-4字符,非中文)总数:", len(short))
# 形态归类
def kind(p):
    if re.fullmatch(r"[A-Z0-9_]+", p): return "大写代号/缩写"
    if re.fullmatch(r"[A-Za-z]+", p): return "纯字母词"
    if re.fullmatch(r"[0-9.,\-]+", p): return "数字/电话"
    return "其它"
cc = collections.Counter(kind(p) for _, _, p in short)
for k, n in cc.most_common(): print("  ", k, n)
random.seed(3)
print("\n抽样 30 条:")
for ch, c, p in random.sample(short, 30):
    print(f"  {ch:5} {c} {p!r}")
