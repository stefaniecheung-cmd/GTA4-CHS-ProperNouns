# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","E9DE925B","好吧，先生……我说了别再放那一首了。","原文是「我说了别再放了」，原译「好了，谢谢」把 sir 误读成 thank you"),
("base","MAIN","EB77B662","尼克。有空一起出去玩玩，懂？就这样 - LJ","Niko 按口径统一「尼克」"),
("base","MAIN","F8800BC7","结果她把一天十份馅饼配薯条全打成了糊。","liquidized 是「打成流食」，原译「照样十顿，全做成流食」把一句拆成两句且主语丢"),
("base","MAIN","FF5BDDCE","要让相机离角色更远，先把镜头朝向角色所在的方向。","原译「以将其向远处移动」指代不明且句子不成句"),
("base","MAIN","12F16FCD","你是真正的绅士，尼克。爱你，宝贝。","Nicky 按口径统一「尼克」"),
("base","MAIN","1F5DDB9C","尼克，姑娘们和我都很感谢你，兄弟。","Nicky 按口径统一「尼克」"),
("base","MAIN","25B4416A","那条线划在哪儿，五尺五？五尺六？","cut the line 是「划线（划定标准）」，原译「多少以下才算」把划线译成下限判断；five foot five 是五尺五"),
("base","MAIN","2ABF8614","我是说它现在越来越厉害了，不是吗？","gone from strength to strength 是「不断壮大」，原译「不可同日而语」换了成语方向"),
("base","MAIN","3C2220F4","噢，你现在都湿透了……刚才真爽。","that was fun 是「刚才真爽」，原译「我很满意」把主语换成说话人"),
("base","MAIN","48E91EA3","那个不是马龙！附近还有另一伙人吗？ - the X","another group near by 是「附近还有另一伙」，原译「人群聚集」把 group 译成群体集合"),
("base","MAIN","701D6419","再飞高点，尼克。姑娘们想看看这玩意儿。","Nicky 统一「尼克」；this thing 指眼前的东西，原译「看得清楚些」把宾语换了"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p1_07000.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
