# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","555B588D","~z~~x~为了活下去，那些破事你不得不干，兄弟。","do that shit to survive 是「为了活命不得不干那些破事」，原译「那样搞的」把 shit 虚化"),
("base","MAIN","5DEAC486","~z~~x~我就爱把屁股往陌生人身上蹭。","rubbing my ass on strangers 是「把屁股蹭在陌生人身上」，原译「摩擦摩擦」丢了具体部位"),
("base","MAIN","7772096E","~z~~x~嘿，喜欢让我的奶子贴你脸上吗？","原译「洗面奶」是中文网络黄梗，不是原文内容；原文直说 tits in your face"),
("base","MAIN","7ACF5842","~z~哦哦。Insurgiscan 上又有动静了。","Insurgiscan 是设备专名，按口径保留英文，原译「叛乱扫描仪」把专名意译"),
("base","MAIN","7F33465E","~z~~x~放低点看清楚些，NB。","Take it down for a better look 是「放低看更清楚」，原译「下降一些视角」把动作译成视角参数"),
("base","MAIN","66F26D1C","~z~哟，我这拉斯塔法里兄弟要闪了。回见。","rasta 是「拉斯塔法里信徒」的自称，原译「老兄」把这个身份词抹掉了"),
("base","MAIN","C34B807E","~z~~x~要是真要谈公平，谈飞机，","aeroplanes 是「飞机」，原译「空运」把名词译成行业"),
("base","MAIN","C4E0B1FD","~z~~x~真是的，何不呢？我们正用得上这笔钱。","We could use the money 是「我们正好用得上这笔钱」，原译「有钱就好」换了意思"),
("base","MAIN","D76A224A","~z~~x~可以掐了，先生…","cut that 在这里是「掐掉（音乐/声音）」，原译「音乐可以切了」是把上下文补了出来但并不准确"),
("base","MAIN","DE199A4A","~z~~x~嘿，进来吧，坐沙发上。","sit on the couch 是「坐沙发上」，原译「超长沙发」把 couch 当成了尺寸描述"),
("base","MAIN","0941C360","~z~~x~恕我直言，亲爱的，你这身打扮太丑了！","that outfit 是「这一身打扮」，原译「外套」缩小了范围；sweetie 是「亲爱的」"),
("base","MAIN","11871D0D","~z~~x~这就是我堂弟说的美国奶子。","cousin 按全库口径统一「堂弟」，原译「堂兄」"),
]
with io.open(r"C:\Game\Grand Theft Auto IV\gta4-chs\build\tmp_q\fixes_p1_06366.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
