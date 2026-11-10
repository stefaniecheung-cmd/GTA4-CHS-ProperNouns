# -*- coding: utf-8 -*-
import io, csv, re
csv.field_size_limit(10**9)
B = r"C:\Game\gta4-chs\build"
CODE = re.compile(r"~[a-zA-Z0-9_]+~")
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")

want = {("base","FCB3AU"),("base","GCMC1AU"),("base","EMAILBK"),("base","EYESRCH"),
        ("TLAD","E1FCJ3A"),("TLAD","GWAUD"),("TLAD","RACESAU"),("base","GCADCAU")}
show = {k: [] for k in want}
for ch in ["base","TLAD","TBoGT"]:
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            if re.search(r"[\u4e00-\u9fff]", t) or not t.strip():
                continue
            core = CODE.sub("", t).strip()
            if len(WORD.findall(core)) < 3 or len(core) <= 18:
                continue
            k = (ch, r.get("table",""))
            if k in want and len(show[k]) < 6:
                show[k].append(core[:160])

for k, v in show.items():
    if not v:
        continue
    print("=" * 70)
    print(k)
    for s in v:
        print("   -", s)
