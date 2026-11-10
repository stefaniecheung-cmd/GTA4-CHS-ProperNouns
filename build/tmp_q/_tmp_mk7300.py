# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","2B768893","嗨，宝贝，不如我们找个更……私密点的地方？","somewhere a little more private 是「更私密一点的地方」，原译「稍微里面点」把 private 当成方位"),
("base","MAIN","50241305","啊啊，我觉得我心脏停了！！我左半边脸没知觉了。","check your pulse 是「摸脉搏」，此处为原译「心率」，改回脉搏"),
("base","MAIN","65DC34F0","尼克，你先别打电话来一阵子。我需要一点自己的时间。 xx","Niko 按口径统一「尼克」"),
("base","MAIN","6FB15D09","贴着那座塔低空掠过。让她们见识下懂行的人是怎么过日子的。","those who know how 是「懂行的人」，原译「有品味的人」换了描述"),
("base","MAIN","7CB4A66D","虽然他们一开始也联系不上他，知道吗……？","getting hold of him 是「联系上他」，原译「抓牢他」按字面直译"),
("base","MAIN","8F728A0F","被警察缴械时，按~INPUT_SPRINT~挣脱。","break out 是「挣脱」，原译「抗捕」扩大了含义（此处是被缴械时的挣脱动作）"),
("base","MAIN","9C2D405B","在这胸脯之下，我的心脏正在为你跳动，尼克。 xoxo","Niko 按口径统一「尼克」"),
("base","MAIN","A61E10B5","为了这次巡演，我还得先去做个体检……呃，","for this tour 是「为了这次巡演」，原译漏掉这个动机"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p1_07300.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
