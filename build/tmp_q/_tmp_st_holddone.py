# -*- coding: utf-8 -*-
import io, shutil, os, json, hashlib

RV = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\review"
HOLD = os.path.join(RV, "挂起待拍板.tsv")
DONE = os.path.join(RV, "挂起待拍板_已处理_20261109.tsv")

shutil.copy2(HOLD, HOLD + ".bak_before_p2hold")

# 已处理 8 条
done = [
("TBoGT","E2Y1Aud","E50E2243",
 "After I've finished with them, they'll look like they've been dragged through the fucking desert.",
 "等我完事儿，她们会像被拖过他妈一片沙漠一样惨。",
 "原文其实完整（dragged through the fucking desert 是「被拖着穿过沙漠」的惨状比喻），只是导出预览截断；原译「沙漠遇难的脱水人干」为自创意象。fucking 按原意译出。"),
("TBoGT","E2Y3AUD","CC495487",
 "Can you now?",
 "你现在就能买了？",
 "Can you now? 是对对方当下能力的反诘惊叹，原译「能买到吗」丢了 now 的时点并把肯定语气改成疑问。"),
("TBoGT","E2Y3AUD","1AEDA761",
 'When a book is called "Guns,',
 "当一本书的名字叫「枪炮，",
 "原文本身就在书名中途断句（引号未闭合，下一条接书名后半），确认为原始文本而非导出截断；译文保持同一断点，把原译误当顿号的引号还原成中文引号。"),
("TLAD","E1HPAUD","96E75BE0",
 "DIALOGUE MISSING",
 "对话缺失",
 "DIALOGUE MISSING 是配音缺失的占位符，不是台词；与 5D478FFD 统一为「对话缺失」，「丢失」改「缺失」避免像事件报告。"),
("TLAD","E1S1AUD","BBC92791",
 "Ah, he was a man of the people, a philanthropist, a pompous windbag and an occasional catamite,",
 "啊，他是人民公仆，是个大善人，是个牛皮大王，偶尔还当个男宠，",
 "原文完整（catamite＝被包养的男宠/娈童），只是预览截断；原译「小受」属圈内用语且不合讽刺政客的语境；原文以逗号结尾（本条被切成两句显示），译文保留逗号。"),
("TLAD","E1SAAUD","5D478FFD",
 "DIALOGUE MISSING",
 "对话缺失",
 "同 96E75BE0 的占位符，两处统一。"),
("TBoGT","E2BCLA","2BB5C8D7",
 "Cold man.",
 "你可真冷血。",
 "前一条是「我事儿很多，给不了你需要的关注」，本条是女方对这句的评语；意语 Che tristezza / 法语 C'est bas / 西语 Hombre frío 三语一致指向责备。原译「好冷酷啊」偏旁观感叹。"),
("TBoGT","E2BG1CA","5B2EBAE5",
 "Go. Roll the bitch!",
 "去。把音响轰起来！",
 "意语 Pompa il volume / 法语 Fais péter le son / 西语 Dale caña 三语都把 roll 解成「开音响、放起来」；原译「闪亮登场」无原文依据。"),
]
# 结案不改
closed = [
("TBoGT","E2BCLA","DB14B1D9","E mio.","是我。",
 "意大利语「(这)是我的」，法/意原文都保留 E mio，官方西语译作 Soy yo（是我）；中文「是我。」已准确，不改。"),
]
# 仍保留
remain = [
("TLAD","MAIN","62F4C1EF",
 "Something about faked terrorist acts gets me all excited, Klebitz. You can either take out the chopper as it lands or deal with the convoy as it makes its way out of the airport. By the way, I've got a man at the Southwest gate who can help you if you're locked into the runway area. - TS III",
 "伪造恐怖袭击让我很兴奋，克雷比兹。你可以轰烂正在降落的直升机，也可以袭击离开机场的车队。对了，万一你被困在机场里面，西南门有我的人可以帮你出去。 - TS III",
 "跨章 crc 冲突：TBoGT|MAIN 同 crc 的原文是「秃鹰直升机在西河」（Yu$uf），覆盖表按 crc 单键只能存一条，现存 TBoGT 版。TLAD 这条是原译、语义基本到位、未改。要修需覆盖表支持复合键或分章存（结构性改动，需用户拍板）。"),
]

with io.open(DONE, "w", encoding="utf-8-sig", newline="\n") as f:
    f.write("chapter\ttable\tcrc\tenglish\tzh_new\tresolution\n")
    for r in done: f.write("\t".join(r) + "\n")
    for r in closed: f.write("\t".join(r) + "\n")

with io.open(HOLD, "w", encoding="utf-8-sig", newline="\n") as f:
    f.write("chapter\ttable\tcrc\tenglish\tzh_now\tdoubt\tsuggest\n")
    for r in remain: f.write("\t".join(r) + "\n")

print("done", len(done), "closed", len(closed), "remain", len(remain))

# 断点 JSON 刷新
P = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\review\润色线-断点.json"
d = json.loads(io.open(P, encoding="utf-8").read())
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
ZG = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\zh_global.tsv"
LG = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\review\上游润色_审读日志.tsv"

def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest().upper()[:16]

d["updated"] = "2026-11-09 23:58:00"
d["counts"] = {
    "zh_global_rows": sum(1 for l in io.open(ZG, encoding="utf-8") if l.strip()) - 1,
    "review_log_rows": sum(1 for l in io.open(LG, encoding="utf-8-sig") if l.strip()) - 1,
    "qa": "合计：检查 14125 条，错误 0，警告 17",
}
for ch, fn in (("gxt_base_tr","zchs_base_tr.gxt"), ("gxt_TLAD_tr","zchs_TLAD_tr.gxt"), ("gxt_TBoGT_tr","zchs_TBoGT_tr.gxt")):
    p = os.path.join(B, fn)
    d["build"][ch] = {"bytes": os.path.getsize(p), "sha256_16": sha16(p)}
d["build"]["applied"] = {"base": 9717, "TLAD": 2500, "TBoGT": 2830}
d["artifacts_sha256"] = {
    "zh_global": hashlib.sha256(open(ZG,"rb").read()).hexdigest(),
    "review_log": hashlib.sha256(open(LG,"rb").read()).hexdigest(),
    "zchs_gxt": d["build"]["gxt_base_tr"]["sha256_16"],
}
d["notes_log"].append({
    "at": "2026-11-09 23:58:00",
    "offset": 1113,
    "note": "挂起 8 条结案（挂起表 6 条全处理 + 语义待定 3 条中 2 条改、1 条确认原译正确）；EULA 8 条统一口径（删第三方署名行、Microsoft 商标句、标点）；打码/自加符号 6 条（〇逼→那个 C 字、去掉自加星号与括注、sandwich maker 误译改正）；顺带清理覆盖表 5 行 chapter 空的重复旧行。base 9,717 / TLAD 2,500 / TBoGT 2,830，qa 14,125 条 0 错 17 警。覆盖表备份 assets_backup\\覆盖表_zh_global_20261109_p2hold.tsv",
})
shutil.copy2(P, P + ".bak_before_p2hold")
io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=2))
print("counts", d["counts"])
print("gxt", d["build"]["gxt_base_tr"]["bytes"], d["build"]["gxt_TLAD_tr"]["bytes"], d["build"]["gxt_TBoGT_tr"]["bytes"])
