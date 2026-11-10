# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","9C056DC3","按~INPUT_FRONTEND_ACCEPT~跳过观光。","tour 是「观光」，原译「旅途」与睡眠/journey 条目混用"),
("base","MAIN","FD1F893A","这位小恶魔从十一岁生日起就统治着自由城的夜生活，已经两年了。","原文有 since her 11th birthday 与 two years 两个时间点，原译把后半句的两年与生日整段漏掉"),
("base","MAIN","0EA62C47","我现在就在撸。撸得飞快。克洛伊和吉尔･冯･克拉斯滕堡是闺蜜。","Von Crastenburg 按口径统一「冯･克拉斯滕堡」"),
("base","MAIN","1168D9B6","你他妈人呢，尼克？我不允许你把我当你那些低端妓女对待。","Niko 按口径统一「尼克」"),
("base","MAIN","4BFFD3E8","和纯爷们混就是这种感觉，玩得够猛。可以回去了，尼克。","hitting it hard 是「玩得猛」，原译「超稳健」方向反；Nicky 统一「尼克」"),
("base","MAIN","588DF684","好家伙，Sully's 这儿有台好车给你。帝王。快得吓人。","The emperor 是车型名 Emperor，原译「皇霸天」自造名与全库车型口径不符"),
("base","MAIN","9C8AF7B4","当心，尼克。咱俩这样的猛男坠机身亡可是个大悲剧，太蠢了。","Nicky 按口径统一「尼克」"),
("base","MAIN","A648AACA","平整的台面用来铺轨道，还有丛林秋千——全都装在轮子上——超有档次。","laying out rails 是「铺轨道」，原译「摆线」把 rails 误读成线缆"),
("base","MAIN","A8290EF1","我只想说这歌很牛逼，就这意思。我是说它样样都好用。","good for everything 是「什么都好用」，原译「好处很多」把适用范围扩大成优点罗列"),
]
with io.open(r"C:\Game\Grand Theft Auto IV\gta4-chs\build\tmp_q\fixes_p1_07800.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
