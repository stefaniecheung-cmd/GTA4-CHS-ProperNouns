# -*- coding: utf-8 -*-
import io, csv, re
from collections import defaultdict
csv.field_size_limit(10**9)
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")
CODE = re.compile(r"~[a-zA-Z0-9_]+~")

CAT = defaultdict(int)
LEFT = defaultdict(int)
LEFT_ROWS = []
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            if re.search(r"[\u4e00-\u9fff]", t) or not t.strip():
                continue
            core = CODE.sub("", t).strip()
            if len(WORD.findall(core)) < 3 or len(core) <= 18:
                continue
            tb = r.get("table", "")
            low = core.lower()
            if "THIS LABEL NEEDS TO BE HERE" in core:
                CAT["占位符 THIS LABEL..."] += 1; continue
            if re.search(r"\.sc[ )]|- KM\)|\bKM\)", core):
                CAT["开发标注(.sc/- KM)"] += 1; continue
            if tb.upper().startswith("CREDIT"):
                CAT["制作名单 CREDIT"] += 1; continue
            if re.fullmatch(r"[a-z0-9\.\-_/]+\.(com|net|biz|org|tv|edu)[/a-z0-9_\-]*", low) or low.startswith("www.") or low.startswith("http"):
                CAT["网址"] += 1; continue
            CAT["疑似真未译"] += 1
            LEFT[ch] += 1
            LEFT_ROWS.append((ch, tb, r.get("crc"), core))

print("分类计数：")
for k, v in sorted(CAT.items(), key=lambda x: -x[1]):
    print("  ", k, v)
print("\n疑似真未译按章：")
for k, v in LEFT.items():
    print("  ", k, v)
print("  合计", sum(LEFT.values()))

print("\n前 40 条样本（章/表/crc/文本）：")
for row in LEFT_ROWS[:40]:
    print("  ", row[0], row[1], row[2], "|", row[3][:110])

print("\n疑似真未译按表 Top20：")
bt = defaultdict(int)
for row in LEFT_ROWS:
    bt[(row[0], row[1])] += 1
for k, v in sorted(bt.items(), key=lambda x: -x[1])[:20]:
    print("  ", k, v)
