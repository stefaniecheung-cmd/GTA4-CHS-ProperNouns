# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","89EAD930","尼克，这次的事你办得很好。终于有个能信得过的人，这很好。 - 福斯汀","Niko 按口径统一「尼克」"),
("base","MAIN","9BEE08CF","你需要登录 Xbox LIVE 才能使用 Xbox LIVE 的游戏功能。","game play features 是「游戏功能」，原译「特性」笼统"),
("base","MAIN","CCCD4FBA","好吧，尼克。我以为我们有约，就一直在等你。你倒是去忙什么了？","Niko 按口径统一「尼克」"),
("base","MAIN","D6893445","干得好，尼克。你要是手头紧，就把车弄给我们，我们给你弄个好价。","Niko 按口径统一「尼克」；bring cars to us 是「把车送来」"),
("base","MAIN","E87617AF","尼克，出什么事了？你怎么放我鸽子？贩毒和杀人比陪家人还重要吗？罗曼","Niko 按口径统一「尼克」"),
("base","MAIN","04A2D694","都铎港码头边、Liberty State Delivery 有个家伙开这辆 Rancher。把车弄来。","Rancher 是车型专名，按口径保留英文，原译「蓝彻」为自造名；Liberty State Delivery 为公司名，保留原文"),
("base","MAIN","30E417BD","柬埔寨。那场干得漂亮。波尔布特。他杀了十万人。而那就是他威胁的分量。","that was his threat 指「他威胁要杀的就是这个数」，原译「他吓唬人的说法」把威胁力度说成吹牛"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p2_0201.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
