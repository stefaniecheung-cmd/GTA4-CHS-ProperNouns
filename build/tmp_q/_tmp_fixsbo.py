# -*- coding: utf-8 -*-
import io, shutil
zg = r"C:\Game\gta4-chs\data\zh_global.tsv"
lg = r"C:\Game\gta4-chs\data\review\上游润色_审读日志.tsv"
shutil.copy2(zg, zg + ".bak_before_sbo")
shutil.copy2(lg, lg + ".bak_before_sbo")
old = "~s~~1~~s~~1~:~1~ 前到 SoBoHoe 家。"
new = "~1~:~1~ 前到 SoBoHoe 家。"
def patch(path, crc_col, zh_col, enc):
    with io.open(path, "r", encoding=enc, newline="") as f:
        lines = f.read().split("\n")
    n = 0; out = []
    for ln in lines:
        p = ln.split("\t")
        if len(p) > max(crc_col, zh_col) and p[crc_col].strip() == "1084AEED" and p[zh_col].startswith("~s~~1~~s~"):
            p[zh_col] = new; ln = "\t".join(p); n += 1
        out.append(ln)
    with io.open(path, "w", encoding=enc, newline="\n") as f:
        f.write("\n".join(out))
    return n
print("zg", patch(zg, 0, 1, "utf-8"), "log", patch(lg, 2, 5, "utf-8-sig"))
