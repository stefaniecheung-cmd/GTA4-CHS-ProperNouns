# -*- coding: utf-8 -*-
import io, csv, re
from collections import defaultdict
csv.field_size_limit(10**9)
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
CODE = re.compile(r"~[a-zA-Z0-9_]+~")
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")
KEYLIKE = re.compile(r"^[A-Za-z0-9_.\-]+$")

CAT = defaultdict(int)
ROWS = []
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            if re.search(r"[\u4e00-\u9fff]", t) or not t.strip():
                continue
            core = CODE.sub("", t).strip()
            if len(WORD.findall(core)) < 3 or len(core) <= 18:
                continue
            # 键名式：全大写字母数字下划线（配音/资源键）
            if re.fullmatch(r"[A-Z0-9_]+", core):
                CAT["资源键名(全大写下划线)"] += 1; continue
            if re.match(r"^[A-Z][A-Z0-9_]*_[A-Z0-9_]*", core) and "_" in core and core.count("_") >= 1:
                CAT["资源键名(带下划线)"] += 1; continue
            if "THIS LABEL NEEDS TO BE HERE" in core:
                CAT["占位符"] += 1; continue
            if re.search(r"<a href", core, re.I):
                CAT["HTML链接"] += 1; continue
            if re.fullmatch(r"[A-Za-z0-9@\.\-_/:]+", core) and ("@" in core or core.lower().startswith("www") or ".com" in core.lower() or ".net" in core.lower() or ".info" in core.lower()):
                CAT["网址/邮箱"] += 1; continue
            if r.get("table","").upper().startswith("CREDIT"):
                CAT["制作名单"] += 1; continue
            CAT["其余"] += 1
            ROWS.append((ch, r.get("table",""), r.get("crc"), core))

print("分类：")
for k, v in sorted(CAT.items(), key=lambda x: -x[1]):
    print("  ", k, v)
print("\n其余（需人工判性质）共", len(ROWS))
bt = defaultdict(int)
for row in ROWS:
    bt[row[0]] += 1
print("按章：", dict(bt))
print("\n样本 60 条：")
for row in ROWS[:60]:
    print("  ", row[0], row[1], row[2], "|", row[3][:120])
