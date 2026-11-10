# -*- coding: utf-8 -*-
import io, sys, collections
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
ORIG = {
    "base":  G + r"\_chs_backup_20261110\common\text\american.gxt",
    "TLAD":  G + r"\TLAD\common\text\american.gxt",
    "TBoGT": G + r"\TBoGT\common\text\american.gxt",
}
eng = {}
for ch, p in ORIG.items():
    tables, items = parse_gxt(p)
    for tb, crc, t in items:
        eng[(ch, tb, crc)] = t

TARGET = "厩唠啵喏嘀噗囔墩姘娄岬惭抡拣捋撬撵擞槌沤泞渥璀璨疵瘀瘆砌砺簸粝纭肏肓芋蔓虱辄遢邋酝钾韧颚髋"
SYM = "™é¬®áÉç／Èàèúñü"

rows = []
for ch, f in (("base", "src_base_tr.tsv"), ("TLAD", "src_TLAD_tr.tsv"), ("TBoGT", "src_TBoGT_tr.tsv")):
    with io.open(f, encoding="utf-8-sig", newline="") as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            tb, crc, txt = parts[0], parts[1], parts[2]
            hit = set(c for c in txt if c in TARGET or c in SYM)
            if hit:
                rows.append((ch, tb, crc, txt, eng.get((ch, tb, int(crc, 16)), ""), hit))

print("命中条目数", len(rows))
cnt = collections.Counter()
for r in rows:
    for c in r[5]:
        cnt[c] += 1

print("\n=== 逐字出现条目数 ===")
for i, c in enumerate(TARGET):
    print("  %s%3d" % (c, cnt.get(c, 0)), end="")
    if (i + 1) % 10 == 0:
        print()
print()
print("\n=== 符号 ===")
for c in SYM:
    if cnt.get(c):
        print("  %s(U+%04X) %3d条" % (c, ord(c), cnt.get(c, 0)))

print("\n=== 例句（每字最多2条） ===")
shown = collections.Counter()
for ch, tb, crc, txt, orig, hit in rows:
    for c in sorted(hit):
        if shown[c] >= 2:
            continue
        shown[c] += 1
        print("")
        print("[%s] %s %s %s" % (c, ch, tb, crc))
        print("    EN: " + orig[:200])
        print("    ZH: " + txt[:200])
