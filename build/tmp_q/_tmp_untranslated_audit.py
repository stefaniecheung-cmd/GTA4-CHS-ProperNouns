# -*- coding: utf-8 -*-
"""全量未译盘点：src_*_tr.tsv 非中文条目按 qa_gate 白名单分类，输出疑似真未译清单。"""
import csv, io, os, re, collections, sys
csv.field_size_limit(10**9)

BUILD = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
OUT = r"C:\Game\Grand Theft Auto IV\gta4-chs\build\cmp_assets\未译_分类.tsv"
CODE = re.compile(r"~[a-zA-Z0-9_]+~")
RAW_OK = re.compile(
    r"(CTRL\+[A-Z]|ALT\+[A-Z]|SHIFT\+[A-Z]|CAPS LOCK|NUM LOCK|SYSRQ|MEDIA SEL|PRTSC"
    r"|AXIS [0-9A-Za-z ]+|AXIS SLIDER \d+|Param \d+|F\d+|ESC|TAB|ENTER|SPACE|BACKSPACE"
    r"|\$[0-9,]+)")
KEEP_EN = ["ZiT!", "MS X", "MS Y", "BANDIT!",
           "Tvoja voljena majka.", "Moj dragi sine,", "Swingers", "Teeker", "Deadbeats",
           "Eyediditmy Way", "Rusty Brown"]
NAME_ONLY = {"Niko", "Niko.", "Roman", "Roman.", "Niko!", "Roman!",
             "Niko...", "Roman...", "Niko..", "Roman..",
             "Niko Bellic", "Roman Bellic", "Niko Bellic.", "Roman Bellic."}

def classify(text):
    t = text.strip()
    plain = CODE.sub("", t).strip()
    if plain == "":
        return "纯控制符"
    if t in NAME_ONLY or plain in NAME_ONLY:
        return "人名保留(Niko/Roman)"
    if t in KEEP_EN:
        return "专名保留"
    if RAW_OK.fullmatch(t):
        return "按键/价格码"
    if re.fullmatch(r"[\$0-9., ]+", t):
        return "数字价格"
    if len(plain) <= 4:
        return "短碎片<=4"
    if re.search(r"[A-Za-z]", plain):
        return "疑似真未译"
    return "其它非中文"

counts = collections.Counter()
suspect = []
for ch in ("base", "TLAD", "TBoGT"):
    p = os.path.join(BUILD, f"src_{ch}_tr.tsv")
    with io.open(p, encoding="utf-8-sig") as f:
        rd = csv.DictReader(f, delimiter="\t")
        for r in rd:
            text = r["text"]
            has_cjk = any("\u4e00" <= x <= "\u9fff" for x in text)
            if has_cjk:
                continue
            cat = classify(text)
            counts[(ch, cat)] += 1
            if cat == "疑似真未译":
                suspect.append((ch, r["table"], r["crc"].upper(), text))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8-sig", newline="") as g:
    g.write("章节\t表\tCRC\t英文原文\n")
    for ch, t, c, x in suspect:
        g.write(f"{ch}\t{t}\t{c}\t{x}\n")

print("=== 各章非中文分类 ===")
for ch in ("base", "TLAD", "TBoGT"):
    print(f"\n[{ch}]")
    tot = 0
    for cat in ("人名保留(Niko/Roman)", "专名保留", "按键/价格码", "数字价格",
                "短碎片<=4", "纯控制符", "其它非中文", "疑似真未译"):
        n = counts[(ch, cat)]
        tot += n
        if n:
            print(f"  {cat:16} {n}")
    print(f"  {'非中文合计':16} {tot}")
print("\n疑似真未译总数:", len(suspect), "->", OUT)
