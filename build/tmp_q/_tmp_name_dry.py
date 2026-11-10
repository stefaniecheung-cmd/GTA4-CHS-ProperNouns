# -*- coding: utf-8 -*-
import io, csv, re
from collections import Counter
csv.field_size_limit(10**9)
ZG = r"C:\Game\gta4-chs\data\zh_global.tsv"

pat = re.compile(r"(尼克|尼科|罗曼)")
follow_cjk = Counter()
odd = []
with io.open(ZG, encoding="utf-8", newline="") as f:
    rd = csv.reader(f, delimiter="\t")
    next(rd, None)
    for p in rd:
        if len(p) < 2:
            continue
        z = p[1]
        for m in pat.finditer(z):
            nxt = z[m.end():m.end()+1]
            # 后接汉字或间隔符 → 可能是构词（如 尼克･贝利克 / 尼克仔 / 尼克兄弟）
            if nxt and (re.match(r"[\u4e00-\u9fff]", nxt) or nxt in "･·"):
                follow_cjk[(m.group(0), z[m.end():m.end()+3])] += 1
                if len(odd) < 400:
                    s = z[max(0, m.start()-14):m.end()+20].replace("\n", " ")
                    odd.append((m.group(0), s, p[0]))

print("名字后接汉字/间隔符的组合（全部）：")
for k, v in follow_cjk.most_common():
    print("   %4d  %s" % (v, k))

print("\n=== 这些上下文逐条（最多 400）===")
for name, s, crc in odd:
    print("  [%s] %s" % (name, s))
