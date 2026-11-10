# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","E76C1C27","开着这辆 Turismo 的阔佬从来不把它停车库里。他家在韦斯代克的猫头鹰溪大道。","Turismo 是车型专名，按口径保留英文，原译「远途」为意译自造名"),
("base","MAIN","0BDB49AD","尼克，我想有必要把这张照片发你，你堂弟眼下好像遇上点麻烦。你的朋友，迪米特里。","Niko 按口径统一「尼克」；cousin 统一「堂弟」，原译「堂兄」关系错"),
("base","MAIN","628F68AB","尼克，兄弟。咱们他妈就是赢家。我们可不想被人当傻逼水手看待，行吧？","Nicky 按口径统一「尼克」"),
("base","MAIN","7AFC1039","不过我要是有个堂弟，要钱给我钱、要车就派车，我恐怕也不会去工作的。","my cousin 指 Niko 的堂弟，按口径统一「堂弟」，原译「堂兄」关系错"),
("base","MAIN","9193DAEC","你怎么没来赴约，尼克。是不是警察找你麻烦？他们这样对待移民真让人震惊。 xoxo","Niko 按口径统一「尼克」；hassling 是「刁难/找麻烦」"),
("base","MAIN","94647251","这一趟开得真野啊，尼克。不过没两位女士待会儿的经历野。总之，谢了兄弟。","Nicky 按口径统一「尼克」"),
("base","MAIN","A0EDE638","尼克，记得查查你的邮箱。布鲁斯可能有活给你。咱们也能像他那样穿金戴银吗？！罗曼","Niko 按口径统一「尼克」"),
("base","MAIN","C77EF43D","擦！你把我一个人扔俱乐部里了，尼克。不过我挺喜欢那些妞的，算了。就这样 - LJ","Niko 按口径统一「尼克」"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p2_0501.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
