# -*- coding: utf-8 -*-
import io
rows = [
("TLAD","MAIN","6C9C4410","特里和克莱正在赶来支援你。小地图上的~b~~BLIP_95~~s~和~b~~BLIP_96~~s~就是他们俩。","on their way 是「正在赶来」，原译「表示他们当前的位置」把行进状态说成静态标记"),
("TLAD","MAIN","E72EAF82","谢谢你在俱乐部里给我和姑娘们留出空间。你真是把我的气氛全搅没了，老兄。回头再出来聚，行吧？","thanks for giving me space 是「谢谢留空间」，原译「这样真的太扫兴了」把感谢与吐槽接反，且 ladies 被误读成「妹妹」"),
("TLAD","MAIN","C068260A","强尼！我跟你朋友吉姆聊过了，他说你在找活干。他还会派一个叫 Malc 的朋友过去。来我公寓找我。 - 莉兹","He's sending a friend of his 是「他会派个朋友来」，原译「他还带了个朋友过来」把吉姆的动作说成 Liz 自己带人"),
("TLAD","MAIN","1E22D3EA","~s~用~INPUT_PHONE_TAKE_OUT~和~INPUT_PHONE_PUT_AWAY~浏览手机菜单。","navigate the phone menu 是「浏览手机菜单」，原译「切换选项」把范围缩小成选项切换"),
("base","MAIN","0D05C245","有玩家没有这个章节，因此你无法游玩本章节的任何游戏。","原译「由于存在不具有此章节的玩家…来自这一章节的游戏」双重从句且指代混乱，改顺句"),
("base","MAIN","1A18D884","尼克，收到你那位小男友的消息了吗？去 TW@ 网咖查查你的邮箱。罗曼","Niko 按口径统一「尼克」；have you heard from 是「有没有收到消息」"),
("base","MAIN","3D7D0B78","按~INPUT_FRONTEND_ACCEPT~查看可用优惠。","offers 在这里是商店折扣/优惠，原译「可用物品」把促销信息译成商品"),
("base","MAIN","468C7256","尼克兄弟，你跑哪去了？是不是又跟哪个妞鬼混去了？行啊你。就这样 - LJ","Niko 按口径统一「尼克」；ketchy chubby wit some dawta 是跟姑娘鬼混"),
("base","MAIN","9D7FFE40","尼克，兄弟。你把我丢下了。希望你没出什么事。就这样 - LJ","Niko 按口径统一「尼克」"),
("base","MAIN","BB7C3248","尼克，好久没你的消息了。你是被人做了，还是进局子了，还是怎么着？","Niko boy 统一「尼克」；sent to the can 是进监狱/局子，原译「进棺材」与 iced 语义重复"),
("base","MAIN","CE8CFC8D","尼克，我的兄弟。咱俩得出去办点事。给我来个电话，懂？就这样 - LJ。","Niko 按口径统一「尼克」"),
("base","MAIN","E59E30E0","尼克，我搭上了一条电话引爆炸弹的线，能帮你大忙——给我打个电话。","Niko boy 统一「尼克」；got a line on 是「搭上线/找到货源」"),
("base","MAIN","05CFEB12","尼克兄弟，你在哪儿呢？咱们该找点事干了，懂？就这样 - LJ","Niko star 里的 Niko 统一「尼克」"),
("base","MAIN","172CE9A8","你最近都在忙什么，尼克？我吗？喝酒、操妞、抢劫、吸粉。咱们好好聚一次。","Niko 按口径统一「尼克」"),
("base","MAIN","2241EA42","尼克，我明天要结婚了。多睡会儿——上午十点你得赶到教堂。罗曼","Niko 按口径统一「尼克」；Get lots of sleep 是让对方多睡"),
("base","MAIN","584FA812","已安装的游戏文件已损坏，游戏即将关闭。你必须删除已安装的游戏并重新安装，才能游玩本作。","原译「删除游戏再次安装以游玩本作」缺主语且动词连缀，改顺句"),
("base","MAIN","8465577F","这辆小 Faggio 一直停在唐人街的 Dragon Heart Plaza，就在 Diamond Street 上。","Faggio 是车型专名，按口径保留英文，原译「费甲欧」为自造名；Dragon Heart Plaza 与街名为地名，保留原文"),
("base","MAIN","8B1FFF77","尼克，能不能拜托你别再打给我了。我这阵子都没空。不过我们很快就会聊的。 xx","Niko 按口径统一「尼克」"),
("base","MAIN","E61307A5","帅哥。卡门现在真的很忙。你怎么不花几天时间想想她有多特别，然后再打给她。","call her 是「打给她」，原译「再来找我」把第三人称改成第一人称"),
("base","MAIN","0AD7FEBD","给我打个电话，尼克。我很想听听你在忙什么。你可以对我坦白，知道吗。xx","Niko 按口径统一「尼克」"),
("base","MAIN","1A0D5A97","太不地道了，NB。太他妈不地道了。说好来医院接我，就得准时来。 - B","when you say you will 是「说好什么时候就什么时候」，原译「谢谢」与句意无关"),
("base","MAIN","9D8EA450","给我打电话，尼克。我们再出去约一次吧。我真的很想多了解你一点。xx","Niko 按口径统一「尼克」"),
]
with io.open(r"C:\Game\gta4-chs\build\tmp_q\fixes_p2_0101.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
