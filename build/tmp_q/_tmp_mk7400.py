# -*- coding: utf-8 -*-
import io
rows = [
("base","MAIN","6C937648","她说：「不行，因为肥……」呃，她原话是，","Well, she actually went 是句子自我打断，原译「其实是这么说的」把打断当成了复述"),
("base","MAIN","CEE772C9","我搞糊涂了，一直在医院等你。妈的，德维恩有时候真犯蠢。","got confused 是「我自己搞糊涂了」，原译「还很疑惑」把主语与意思都偏了"),
("base","MAIN","D115DDAB","去你妈的，你以为卡门没有别的男人为了约到她连命都可以不要？","would kill to date her 是「为了跟她约会肯杀人」，原译「更愿意约会」把强度削掉了"),
]
with io.open(r"C:\Game\Grand Theft Auto IV\gta4-chs\build\tmp_q\fixes_p1_07400.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
