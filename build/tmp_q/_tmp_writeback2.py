# -*- coding: utf-8 -*-
import io, os, csv
csv.field_size_limit(10**9)
GP = r"C:\Game\gta4-chs\data\zh_global.tsv"
NEW = "~z~这是我抛头露面的马甲。~n~我还是希望你称呼我「名人终结者」。"
CRC = "C12FFF32"; CH = "TBoGT"

with io.open(GP, encoding="utf-8") as f:
    lines = f.readlines()
head = lines[0].rstrip("\n").split("\t")
idx = {k:i for i,k in enumerate(head)}
hit = False
out = [lines[0]]
for line in lines[1:]:
    if not line.strip(): out.append(line); continue
    q = line.rstrip("\n").split("\t")
    while len(q)<5: q.append("")
    if q[idx["crc"]].strip().upper()==CRC and q[idx["chapter"]].strip()==CH:
        print("旧:", repr(q[idx["zh"]]))
        q[idx["zh"]] = NEW; q[idx["was"]] = "Celebinator 绰号与 B558BA99 统一译「名人终结者」"
        hit = True
    out.append("\t".join(q)+"\n")
if not hit:
    out.append("\t".join([CRC, NEW, CH, "", "Celebinator 绰号统一"]) + "\n")
    print("新增行")
with io.open(GP, "w", encoding="utf-8", newline="\n") as g:
    g.writelines(out)
print("新:", repr(NEW), " hit=", hit)
