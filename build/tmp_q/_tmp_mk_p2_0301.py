# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","3040169E","尼克，你错过我们的约会了。出什么事了？希望你没卷进什么麻烦。打给我。xx","Niko 按口径统一「尼克」"),
("base","MAIN","697B88F1","我还以为你会罩着我，老弟。德维恩没有别人愿意陪他了，只能自己从医院走回家。操。","ain't got no one else who wants to hang with him 是「没有别人愿意陪他」，原译「没有别人好找了」把意愿译成可选性"),
("base","MAIN","268103EA","我很气，尼克。我气自己爱你太深。告诉我你在哪儿。你现在在哪儿？","Niko 按口径统一「尼克」"),
("base","MAIN","269D16C4","尼克，你开这玩意儿简直跟职业选手一样，行吧？你跟我一样是赢家，兄弟。","Nicky 按口径统一「尼克」"),
("base","MAIN","2C97F610","干得漂亮，尼克。你是赢家，跟布鲁斯一样。我没说错吧，女士们？","Nicky 按口径统一「尼克」"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p2_0301.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
