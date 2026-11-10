# -*- coding: utf-8 -*-
import csv, io, os, glob, sys
csv.field_size_limit(10**9)
ROOT = r"C:\Game\gta4-chs"
DATA = os.path.join(ROOT, "data")
BUILD = os.path.join(ROOT, "build")

TARGETS = {
    ("base", "2C924360"), ("base", "9AF702B1"), ("base", "BF73CBAA"),
    ("base", "D3CE008D"), ("base", "92984525"), ("base", "FB0B04EC"),
    ("TLAD", "E8506E8D"), ("TLAD", "4C6144A0"),
    ("TBoGT", "A8889735"), ("TBoGT", "B558BA99"), ("TBoGT", "9603CE32"),
}

# corpus 英文（物理行解析）
corpus = {}
for ch in ("base", "TLAD", "TBoGT"):
    p = os.path.join(DATA, f"corpus_{ch}.tsv")
    with io.open(p, encoding="utf-8-sig") as f:
        head = f.readline().rstrip("\n").split("\t")
        idx = {k: i for i, k in enumerate(head)}
        for line in f:
            if not line.strip(): continue
            q = line.rstrip("\n").split("\t")
            if len(q) != len(head): continue
            corpus[(ch, q[idx["crc"]].strip().upper())] = {
                "en": q[idx["english"]], "zh_cur": q[idx["chinese_current"]],
                "de": q[idx.get("german", -1)] if "german" in idx else "",
                "fr": q[idx.get("french", -1)] if "french" in idx else "",
            }

# 现有覆盖表取值：zh_global + 分片
def load_overrides(ch):
    ov = {}
    files = [os.path.join(DATA, "zh_global.tsv")] + sorted(glob.glob(os.path.join(DATA, f"zh_{ch}_*.tsv")))
    for p in files:
        if not os.path.exists(p): continue
        with io.open(p, encoding="utf-8") as f:
            head = f.readline().rstrip("\n").split("\t")
            ic = head.index("crc"); iz = head.index("zh")
            ich = head.index("chapter") if "chapter" in head else None
            for line in f:
                if not line.strip(): continue
                q = line.rstrip("\n").split("\t")
                if len(q) < len(head): continue
                chv = q[ich].strip() if ich is not None else ""
                if chv and chv != ch: continue
                ov[q[ic].strip().upper()] = (os.path.basename(p), q[iz])
    return ov

for ch in ("base", "TLAD", "TBoGT"):
    ov = load_overrides(ch)
    for (c, crc) in sorted(TARGETS):
        if c != ch: continue
        co = corpus.get((c, crc), {})
        o = ov.get(crc)
        print(f"=== [{c} {crc}] ===")
        print(f"  EN : {co.get('en','<无corpus>')!r}")
        print(f"  DE : {co.get('de','')!r}")
        print(f"  FR : {co.get('fr','')!r}")
        print(f"  zh_cur(corpus) : {co.get('zh_cur','')!r}")
        print(f"  覆盖表: {o[0] if o else '<无条目>'} -> {o[1]!r}" if o else "  覆盖表: <无条目>")
        print()
