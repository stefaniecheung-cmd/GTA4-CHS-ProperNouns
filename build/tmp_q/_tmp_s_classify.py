# -*- coding: utf-8 -*-
"""对 ~s~ 出入做位置分级：句尾重置=低风险；句中彩色段=串色风险。"""
import csv, io, os, re, collections
csv.field_size_limit(10**9)
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\cmp_assets"
SRC = os.path.join(B, "风险_控制符_en基准.tsv")

CODE = re.compile(r"~[A-Za-z0-9_]+~")
# 非白彩色码：其后直到重置码之间的文字是彩色段
COLOR_SET = {"~b~", "~r~", "~y~", "~c~", "~x~", "~a~", "~m~", "~g~", "~e~",
             "~w~", "~k~", "~l~", "~d~", "~f~", "~h~", "~i~", "~j~", "~o~",
             "~p~", "~q~", "~t~", "~u~", "~v~", "~1~", "~2~", "~3~", "~4~"}

def segments(s):
    """返回 [(code_or_None, plain)] 交替段。"""
    out, last = [], 0
    for m in CODE.finditer(s):
        if m.start() > last:
            out.append((None, s[last:m.start()]))
        out.append((m.group(), ""))
        last = m.end()
    if last < len(s):
        out.append((None, s[last:]))
    return out

def strip_ctrl(s):
    return CODE.sub("", s).strip()

rows = list(csv.DictReader(io.open(SRC, encoding="utf-8-sig"), delimiter="\t"))
color_rows = [r for r in rows if r["类别"] == "颜色/说话人码"]
grade = collections.Counter()
out_rows = []
for r in color_rows:
    en, zh = r["英文原文"], r["我方定稿"]
    lost = [x for x in r["我方缺失"].split(",") if x and x != "-"]
    extra = [x for x in r["我方多出"].split(",") if x and x != "-"]
    kind = "其它"
    if extra == ["~z~"]:
        kind = "说话人码重复(真问题)"
    elif lost == ["~s~"] and extra == []:
        # 我方缺一个 s：判断 en 里被丢的 s 是否句尾闭合
        # en 最后一个非空明文段之后是否还有彩色段
        en_segs = segments(en)
        # 找 en 中最后一个彩色码位置
        last_color = max((i for i, (c, _) in enumerate(en_segs) if c in COLOR_SET), default=-1)
        if last_color < 0:
            kind = "缺s-无彩色段(低)"
        else:
            tail = "".join(p for _, p in en_segs[last_color+1:]).strip()
            kind = "缺s-句尾闭合(低)" if tail == "" else "缺s-句中未闭合(串色风险)"
    elif extra == ["~s~"] and lost == []:
        zh_segs = segments(zh)
        # 多加的 s 在 zh 末尾？
        last_idx = max((i for i, (c, _) in enumerate(zh_segs) if c == "~s~"), default=-1)
        tail = "".join(p for _, p in zh_segs[last_idx+1:]).strip() if last_idx >= 0 else ""
        kind = "多s-句尾(低)" if tail == "" else "多s-句中切断(串色风险)"
    grade[kind] += 1
    out_rows.append({**r, "分级": kind})

print("=== 分级统计 ===")
for k, n in grade.most_common():
    print(f"  {k}: {n}")

with io.open(os.path.join(B, "风险_s码_分级.tsv"), "w", encoding="utf-8-sig", newline="") as g:
    w = csv.writer(g, delimiter="\t")
    w.writerow(["章节", "表", "CRC", "分级", "英文原文", "我方定稿", "我方缺失", "我方多出"])
    for r in out_rows:
        w.writerow([r["章节"], r["表"], r["CRC"], r["分级"], r["英文原文"],
                    r["我方定稿"], r["我方缺失"], r["我方多出"]])

print("\n=== 串色风险明细 ===")
for r in out_rows:
    if "串色" in r["分级"] or "真问题" in r["分级"]:
        print(f"[{r['章节']} {r['表']} {r['CRC']} {r['分级']}]")
        print(f"   EN : {r['英文原文'][:80]}")
        print(f"   我方: {r['我方定稿'][:80]}")
