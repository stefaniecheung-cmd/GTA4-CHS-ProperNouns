# -*- coding: utf-8 -*-
import io, csv, re
from collections import Counter, defaultdict
csv.field_size_limit(10**9)
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
CODE = re.compile(r"~[a-zA-Z0-9_]+~")
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")
KEY = re.compile(r"^[A-Za-z0-9_]{5,}$")

vals = Counter()
rows = []
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            if re.search(r"[\u4e00-\u9fff]", t) or not t.strip():
                continue
            tb = r.get("table", "")
            if tb.upper().startswith("CREDIT"):
                continue
            core = CODE.sub("", t).strip()
            if not core:
                continue
            if re.fullmatch(r"[0-9\+\-\.,$%: ]+", core):
                continue
            if re.fullmatch(r"[A-Z0-9_]+", core) or KEY.match(core.replace(" ", "")):
                continue
            if re.search(r"CTRL\+|ALT\+|SHIFT\+|AXIS|F\d|ESC|TAB|ENTER|SPACE|BACKSPACE", core):
                continue
            vals[core[:50]] += 1
            rows.append((ch, tb, r.get("crc"), core))

print("非 CREDIT 的英文短串：", len(rows), "种数", len(vals))
print("\n全部取值（最多 200）：")
for v, c in vals.most_common(200):
    print("   %3d  %s" % (c, v))
