# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","EDD9937A","我是个事业型女人，尼克，不可能把所有时间都花在你身上。我以为你能理解。回头聊。 xoxo","Niko 按口径统一「尼克」"),
("base","MAIN","0907366D","我怎么老见不着你，尼克。你花太多时间追姑娘，还老躲着堂弟。我们出来聚聚吧。罗曼","Niko 按口径统一「尼克」；原译「花在咪咪的时间上太多了」语序错乱，且 cousin 应为「堂弟」"),
("base","MAIN","1283604D","尼克，你这样的冷血斯拉夫杀手该整点玩具了。来个电话引爆的炸弹怎么样。想要就给我打电话。","Niko 按口径统一「尼克」"),
("base","MAIN","63117BC0","你去哪儿了，尼克？该被天主教负罪感折磨的人是我才对。估计你是有人要杀吧。回见。","Niko boy 统一「尼克」；原译「该遭天主教的罪恶的报应的人」缺谓语且语义断裂"),
("base","MAIN","8A1EE1F9","你们两位根本没心思看这些东西吧。满脑子都是我的胸肌，对不对？我们回去吧，尼克。","Nicky 按口径统一「尼克」"),
("base","MAIN","04A0ACE8","~z~只需 39,999 美元就能拯救地球。Karin Dilettante。坏加好，等于对大家都更好。","Dilettante 是车型专名，按口径保留英文，原译「半吊子」把车名意译；Kirin 系 Karin 品牌误拼，按原文品牌统一"),
("base","MAIN","6F20029D","尼克，我正坐救护车去医院。你不管我的电话，他们就把我揍了一顿。他们还说以后还来找我。","Niko 按口径统一「尼克」；ignored my call 是「没接我的电话」"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p2_0601.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
