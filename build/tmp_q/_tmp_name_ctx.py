# -*- coding: utf-8 -*-
import io, csv, re
from collections import Counter
csv.field_size_limit(10**9)
ZG = r"C:\Game\gta4-chs\data\zh_global.tsv"

pat = re.compile(r"(尼克|尼科|罗曼)")
suf = Counter()
pre = Counter()
rows = []
with io.open(ZG, encoding="utf-8", newline="") as f:
    rd = csv.reader(f, delimiter="\t")
    next(rd, None)
    for p in rd:
        if len(p) < 2:
            continue
        z = p[1]
        if not pat.search(z):
            continue
        rows.append(p)
        for m in pat.finditer(z):
            i, j = m.start(), m.end()
            suf[z[j:j+2]] += 1
            pre[z[max(0,i-2):i]] += 1

print("含目标名的行数：", len(rows))
print("\n后接 2 字符 Top 30：")
for k, v in suf.most_common(30):
    print("   %4d  %r" % (v, k))
print("\n前邻 2 字符 Top 30：")
for k, v in pre.most_common(30):
    print("   %4d  %r" % (v, k))

print("\n『尼科』样例 15 条：")
n = 0
for p in rows:
    if "尼科" in p[1]:
        print("   ", p[0], "|", p[1][:100])
        n += 1
        if n >= 15: break

print("\n『罗曼』样例 15 条：")
n = 0
for p in rows:
    if "罗曼" in p[1]:
        print("   ", p[0], "|", p[1][:100])
        n += 1
        if n >= 15: break

print("\n『尼克』非「尼克，/尼克。」形态的样例 20 条：")
n = 0
for p in rows:
    if "尼克" in p[1] and not re.search(r"尼克[，。！？…]", p[1]):
        print("   ", p[0], "|", p[1][:100])
        n += 1
        if n >= 20: break
