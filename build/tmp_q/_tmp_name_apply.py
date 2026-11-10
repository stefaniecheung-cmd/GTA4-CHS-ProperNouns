# -*- coding: utf-8 -*-
import io, csv, shutil, os, re, sys
csv.field_size_limit(10**9)

ZG = r"C:\Game\gta4-chs\data\zh_global.tsv"
LG = r"C:\Game\gta4-chs\data\review\上游润色_审读日志.tsv"
BK = r"C:\Game\gta4-chs\assets_backup"
os.makedirs(BK, exist_ok=True)
DRY = "--apply" not in sys.argv

# 全名先换（含两种间隔符 · / ･）
FULL = [
    (re.compile(r"尼克[\u00b7\uff65]贝利克"), "Niko Bellic"),
    (re.compile(r"尼科[\u00b7\uff65]贝利克"), "Niko Bellic"),
    (re.compile(r"罗曼[\u00b7\uff65]贝利克"), "Roman Bellic"),
]
# 单名（排除「尼克·兰开斯特」这位报纸专栏作者，是另一个人）
SINGLE = [
    (re.compile(r"尼克(?![\u00b7\uff65]兰开斯特)"), "Niko"),
    (re.compile(r"尼科"), "Niko"),
    (re.compile(r"罗曼"), "Roman"),
]

def convert(s):
    for pat, rep in FULL:
        s = pat.sub(rep, s)
    for pat, rep in SINGLE:
        s = pat.sub(rep, s)
    return s

# --- 统计/改写 zh_global ---
rows = []
changed = 0
samples = []
with io.open(ZG, encoding="utf-8", newline="") as f:
    for line in f.read().split("\n"):
        if not line:
            rows.append(line)
            continue
        p = line.split("\t")
        if len(p) >= 2:
            nz = convert(p[1])
            if nz != p[1]:
                changed += 1
                if len(samples) < 8:
                    samples.append((p[0], p[1][:70], nz[:70]))
                p[1] = nz
        rows.append("\t".join(p))

print("zh_global 改写行数：", changed)
for s in samples:
    print("   ", s[0], "|", s[1], "=>", s[2])

if DRY:
    print("\n[dry-run] 未写入。加 --apply 执行。")
    sys.exit(0)

shutil.copy2(ZG, os.path.join(BK, "覆盖表_zh_global_20261109_namerule.tsv"))
shutil.copy2(LG, os.path.join(BK, "审读日志_20261109_namerule.tsv"))
io.open(ZG, "w", encoding="utf-8", newline="\n").write("\n".join(rows))

# --- 同步改写日志 zh_new（p[2]=crc, p[5]=zh_new）---
log_rows = []
lc = 0
with io.open(LG, encoding="utf-8-sig", newline="") as f:
    for line in f.read().split("\n"):
        if not line:
            log_rows.append(line)
            continue
        p = line.split("\t")
        if len(p) >= 6:
            nz = convert(p[5])
            if nz != p[5]:
                lc += 1
                p[5] = nz
        log_rows.append("\t".join(p))
io.open(LG, "w", encoding="utf-8-sig", newline="\n").write("\n".join(log_rows))
print("日志改写行数：", lc)
print("备份：", os.path.join(BK, "覆盖表_zh_global_20261109_namerule.tsv"))
