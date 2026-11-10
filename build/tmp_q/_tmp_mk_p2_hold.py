# -*- coding: utf-8 -*-
import io
rows = [
("TBoGT","E2Y1Aud","E50E2243",
 "~z~等我完事儿，她们会像被拖过他妈一片沙漠一样惨。",
 "完整原文已导出：dragged through the fucking desert，是「被拖着穿过沙漠」的惨状比喻；原译「变成沙漠遇难的脱水人干」属自创意象。fucking 按原意译出不做净化。"),
("TBoGT","E2Y3AUD","CC495487",
 "~z~你现在就能买了？",
 "Can you now? 是对对方当下能力的反诘惊叹（「你现在就能了？」），原译「能买到吗」既丢了 now 的时点，也把肯定语气改成疑问。"),
("TBoGT","E2Y3AUD","1AEDA761",
 "~z~当一本书的名字叫「枪炮，",
 "原文本身就是断句串：When a book is called \"Guns,（引号未闭合，下一条接书名后半），非导出截断；译文保持同一断点，只是把误读成顿号的引号还原为中文引号。"),
("TLAD","E1HPAUD","96E75BE0",
 "~z~对话缺失",
 "DIALOGUE MISSING 是配音缺失的占位符而非台词，游戏内不显示；与 5D478FFD 统一为「对话缺失」，「丢失」改「缺失」避免像事件报告。"),
("TLAD","E1S1AUD","BBC92791",
 "~z~啊，他是人民公仆，是个大善人，是个牛皮大王，偶尔还当个男宠，",
 "完整原文末尾是 catamite（被包养的男宠/娈童），原译「小受」属圈内用语且与讽刺政客的语境不合；原文以逗号结尾（本条被切成两句显示），译文保留逗号。"),
("TLAD","E1SAAUD","5D478FFD",
 "~z~对话缺失",
 "同上条 96E75BE0 的占位符，两处统一口径。"),
]
with io.open(r"C:\Game\Grand Theft Auto IV\gta4-chs\build\tmp_q\fixes_p2_hold.tsv","w",encoding="utf-8",newline="\n") as f:
    f.write("chapter\ttable\tcrc\t新译正文\t理由\n")
    for r in rows:
        f.write("\t".join(r)+"\n")
print("wrote", len(rows))
