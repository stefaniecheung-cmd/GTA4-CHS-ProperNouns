# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","223A2A17","尼克，格里一直在找你，是有你女人的事。去号子里见他。","Niko 按口径统一「尼克」"),
("base","MAIN","24780912","自动载入内容中。请不要关闭您的系统。","原文无 ~n~，原译多插了换行标签"),
("base","MAIN","25B1914D","我自个儿从医院走回家了。你可真帮了大忙啊，堂弟。罗曼","A lot of good you are 是反讽「你真帮大忙了」，原译「你真是给好人」把反讽译成褒扬"),
("base","MAIN","2EC07DE6","分镜板：把片段拖到这里就能创建视频。","Storyboard 是「分镜板」，与全库其它分镜板条目保持一致"),
("base","MAIN","346DAEC5","NB，既然你没空来接我，那一定是忙着杀人吧。我还奇怪急诊室怎么没塞满你的受害者。罗曼","原译只译了前半句，I'm surprised the ER wasn't full of your victims 整句漏掉"),
("base","MAIN","7F626FDE","他用蜡笔在碟上写了个名字，随手就甩给你了。","in crayon 是「用蜡笔」，原译「写个名字」把蜡笔漏掉"),
("base","MAIN","8B577DFE","Playboy X 现在不在。请在晚上十点到凌晨两点之间找他。","Playboy 是角色名 Playboy X，与其它条目统一保留英文"),
("base","MAIN","A530F01E","尼克，记住，想赚钱的话可以找我接开出租的活。罗曼","Niko 按口径统一「尼克」"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p1_07100.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
