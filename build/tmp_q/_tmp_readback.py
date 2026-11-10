# -*- coding: utf-8 -*-
import io, os, csv
csv.field_size_limit(10**9)
ROOT = r"C:\Game\gta4-chs"
CH = {"base":"base","TLAD":"TLAD","TBoGT":"TBoGT"}
TARGET = {
    "base": ["2C924360","9AF702B1","BF73CBAA","D3CE008D","92984525","FB0B04EC"],
    "TLAD": ["4C6144A0","4FC055AF","E8506E8D"],
    "TBoGT": ["B558BA99","9603CE32","A8889735"],
}
for ch, crcs in TARGET.items():
    p = os.path.join(ROOT, "build", f"src_{ch}_tr.tsv")
    want = set(crcs)
    found = {}
    with io.open(p, encoding="utf-8-sig") as f:
        head = f.readline().rstrip("\n").split("\t")
        ic = head.index("crc"); it = head.index("text")
        for line in f:
            q = line.rstrip("\n").split("\t")
            if len(q) != len(head): continue
            if q[ic].strip().upper() in want:
                found[q[ic].strip().upper()] = q[it]
    for c in crcs:
        print(f"[{ch} {c}] {found.get(c,'<缺失!>')!r}")
    missing = want - set(found)
    if missing: print("  !! 缺失:", missing)
