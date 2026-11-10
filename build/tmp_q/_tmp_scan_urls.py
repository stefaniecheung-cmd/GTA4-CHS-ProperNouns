# -*- coding: utf-8 -*-
import os, re, io
REL = r"C:\Game\gta4-chs\release\GTA4-CHS-zh"
url = re.compile(r"https?://[^\s()）】\]]+")
exts = {".txt", ".md", ".tsv", ".json", ".ini", ".bat", ".cfg"}
for root, _, files in os.walk(REL):
    for fn in files:
        p = os.path.join(root, fn)
        ext = os.path.splitext(fn)[1].lower()
        if ext not in exts:
            continue
        raw = open(p, "rb").read()
        for enc in ("utf-8-sig", "gbk", "utf-16"):
            try:
                t = raw.decode(enc)
                break
            except Exception:
                t = None
        if t is None:
            continue
        for u in url.findall(t):
            print(os.path.relpath(p, REL), "->", u)
print("=== 扫描完成 ===")
