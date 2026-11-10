# -*- coding: utf-8 -*-
import io
rows = [
("TBoGT","E2BCLA","2BB5C8D7",
 "~z~你可真冷血。",
 "前一条英文是「我事儿很多，给不了你需要的关注」，本条 Cold man. 是女方对这句的评语。意语 Che tristezza（真可悲）/ 法语 C'est bas（真下作）/ 西语 Hombre frío（冷血男）三语一致指向责备；原译「好冷酷啊」语气偏旁观感叹，改成当面评语。"),
("TBoGT","E2BG1CA","5B2EBAE5",
 "~z~去。把音响轰起来！",
 "意语 Pompa il volume（把音量开大）/ 法语 Fais péter le son（把音响炸响）/ 西语 Dale caña（加把劲猛干）三语都把 roll 解成「开音响、放起来」，不是「登场」；原译「闪亮登场」无原文依据。"),
]
with io.open(r"C:\Game\Grand Theft Auto IV\gta4-chs\build\tmp_q\fixes_p2_hold2.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
