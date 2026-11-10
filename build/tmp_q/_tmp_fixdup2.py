# -*- coding: utf-8 -*-
import io, shutil
zg = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\zh_global.tsv"
lg = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\review\上游润色_审读日志.tsv"
shutil.copy2(zg, zg + ".bak_before_p1dup2")
shutil.copy2(lg, lg + ".bak_before_p1dup2")
crcs = ["4B1ACD1D","24B2FD47","F777A5C4"]
def patch(path, crc_col, zh_col, enc):
    with io.open(path, "r", encoding=enc, newline="") as f:
        lines = f.read().split("\n")
    n = 0; out = []
    for ln in lines:
        p = ln.split("\t")
        if len(p) > max(crc_col, zh_col) and p[crc_col].strip() in crcs and p[zh_col].startswith("~z~~x~~z~~x~"):
            p[zh_col] = p[zh_col].replace("~z~~x~~z~~x~", "~z~~x~", 1); ln = "\t".join(p); n += 1
        out.append(ln)
    with io.open(path, "w", encoding=enc, newline="\n") as f:
        f.write("\n".join(out))
    return n
print("zg", patch(zg, 0, 1, "utf-8"), "log", patch(lg, 2, 5, "utf-8-sig"))
