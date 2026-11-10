# -*- coding: utf-8 -*-
import io, csv, re
from collections import Counter, defaultdict
csv.field_size_limit(10**9)
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
ZG = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\zh_global.tsv"
CODE = re.compile(r"~[a-zA-Z0-9_]+~")

# 1) src 表里含「尼克」/「Niko」的分布
print("== src 表统计 ==")
for ch in ["base", "TLAD", "TBoGT"]:
    nik = rom = 0
    nik_en = rom_en = 0
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            if "尼克" in t: nik += 1
            if "罗曼" in t: rom += 1
            if re.search(r"\bNiko\b", t): nik_en += 1
            if re.search(r"\bRoman\b", t): rom_en += 1
    print(f"  {ch}: 含中文『尼克』{nik} 含『罗曼』{rom} | 含英文 Niko {nik_en} 含 Roman {rom_en}")

# 2) 纯名字条目（去掉控制符后只剩名字+标点）
print("\n== 纯名字条目（无其它文字）==")
NAME_ONLY = []
for ch in ["base", "TLAD", "TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            core = CODE.sub("", t).strip()
            if not core or re.search(r"[\u4e00-\u9fff]", core):
                continue
            if re.fullmatch(r"(Niko|Nick(y|ie)?|Roman|Ray|Lyle|Lee|Boss|Vans|Yours|McReary|T\.?\s?J\.?\s?Barry)[\s，。！？,\.\!\?…]*", core, re.I):
                NAME_ONLY.append((ch, r.get("table"), r.get("crc"), core))
for row in NAME_ONLY:
    print("  ", row)
print("  合计", len(NAME_ONLY))

# 3) 覆盖表里译为「尼克」「罗曼」的行数
print("\n== zh_global 里的中文名字条数 ==")
c_nik = c_rom = c_niko_en = 0
rows = []
with io.open(ZG, encoding="utf-8", newline="") as f:
    rd = csv.reader(f, delimiter="\t")
    next(rd, None)
    for p in rd:
        if len(p) < 2: continue
        if "尼克" in p[1]: c_nik += 1; rows.append(p)
        if "罗曼" in p[1]: c_rom += 1
        if "Niko" in p[1]: c_niko_en += 1
print("  zh 列含『尼克』", c_nik, "| 含『罗曼』", c_rom, "| 含『Niko』", c_niko_en)
print("  前 12 条样例：")
for p in rows[:12]:
    print("   ", p[0], p[1][:80])
