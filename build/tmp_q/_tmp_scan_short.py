# -*- coding: utf-8 -*-
import io, csv, re
from collections import defaultdict, Counter
csv.field_size_limit(10**9)
B = r"C:\Game\gta4-chs\build"
CODE = re.compile(r"~[a-zA-Z0-9_]+~")
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")

vals = Counter()
cats = defaultdict(int)
n = 0
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            if re.search(r"[\u4e00-\u9fff]", t) or not t.strip():
                continue
            core = CODE.sub("", t).strip()
            if len(WORD.findall(core)) >= 3 and len(core) > 18:
                continue
            n += 1
            if not core:
                cats["纯控制符"] += 1; continue
            if re.fullmatch(r"[0-9\+\-\.,$%: ]+", core):
                cats["纯数字/符号"] += 1; continue
            if re.fullmatch(r"[A-Z0-9_]+", core):
                cats["全大写键名"] += 1; continue
            if re.search(r"CTRL\+|ALT\+|SHIFT\+|AXIS|F\d+|ESC|TAB|ENTER|SPACE|BACKSPACE|NUM LOCK|CAPS", core):
                cats["按键名"] += 1; continue
            cats["英文单词/短语"] += 1
            vals[core[:46]] += 1

print("短串总数", n, "分类：", dict(cats))
print("\n英文单词/短语出现频次 Top 80：")
for v, c in vals.most_common(80):
    print("   %4d  %s" % (c, v))
print("\n不同取值数", len(vals))
