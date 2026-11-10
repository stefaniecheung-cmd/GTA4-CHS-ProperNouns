# -*- coding: utf-8 -*-
import io
rows = [
("TLAD","E1CCAUD","DCFE1114",
 "「亲爱的，呃，厨房里那个杯架，还记得吧？」",
 "原文的 eh - 是口头的迟疑（呃——），中文省略号会被 apply_zh 的 CHAR_MAP 转成三个半角点显示成「......」，改用「呃，」更干净且不丢语气。"),
("TBoGT","E2CM1AU","9D2C1F60",
 "「亲爱的，呃，厨房里那个杯架，还记得吧？」",
 "同上条 DCFE1114，两章同源统一写法。"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p2_code2.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
