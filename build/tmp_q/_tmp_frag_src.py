# -*- coding: utf-8 -*-
import io, csv, re, sys
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
CODE = re.compile(r"~[a-zA-Z0-9_]+~")
# 碎片形态：去掉控制符后只有 1-3 个纯小写字母（或残缺音节）
FRAG = re.compile(r"^[A-Za-z]{1,3}$")

frags = []
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            if re.search(r"[\u4e00-\u9fff]", t):
                continue
            core = CODE.sub("", t).strip()
            if FRAG.match(core):
                frags.append((ch, r.get("table"), r.get("crc"), t, core))

print("碎片形态条目数：", len(frags))
from collections import Counter
print("按表：", Counter((f[0], f[1]) for f in frags).most_common(20))
print()
for f in frags:
    print("  ", f[0], f[1], f[2], "| 原文=", repr(f[3]))

# 对比原版 gxt
print("\n=== 对照原版 american.gxt ===")
SRC = {
 "base": r"C:\Game\Grand Theft Auto IV\common\text\american.gxt",
 "TLAD": r"C:\Game\Grand Theft Auto IV\TLAD\common\text\american.gxt",
 "TBoGT": r"C:\Game\Grand Theft Auto IV\TBoGT\common\text\american.gxt",
}
idx = {}
for ch, p in SRC.items():
    try:
        _, items = parse_gxt(p)
        d = {}
        for tb, c, txt in items:
            k = c if isinstance(c, int) else int(c, 16)
            d[(tb, k)] = txt
        idx[ch] = d
        print("  ", ch, "原版条目", len(d))
    except Exception as ex:
        print("  ", ch, "读取失败", ex)

print()
for f in frags:
    ch, tb, crc, t, core = f
    k = int(crc, 16)
    orig = idx.get(ch, {}).get((tb, k), "<未找到>")
    same = "同" if orig == t else "异"
    print("  [%s] %s %s | 我们=%r | 原版=%r | %s" % (ch, tb, crc, t[:40], str(orig)[:40], same))
