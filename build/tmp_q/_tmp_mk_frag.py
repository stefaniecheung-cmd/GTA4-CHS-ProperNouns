# -*- coding: utf-8 -*-
import io
rows = [
("base", "CREDIT", "4C4B8BA7", "I.T.",
 "原文是「I.T.」（Information Technology 缩写，原版带两个点），我方存成了「IT」丢了点。缩写按原样保留，恢复原版写法。"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_frag.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
print("wrote", len(rows))
