# -*- coding: utf-8 -*-
import io, csv, re
csv.field_size_limit(10**9)
B = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
WORD = re.compile(r"[A-Za-z][A-Za-z_'-]*")
CODE = re.compile(r"~[a-zA-Z0-9_]+~")

for ch in ["base", "TLAD", "TBoGT"]:
    tot = 0
    en_sentence = 0
    key_like = 0
    samples = []
    by_table = {}
    with io.open(rf"{B}\src_{ch}_tr.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            t = r.get("text") or ""
            tot += 1
            if re.search(r"[\u4e00-\u9fff]", t) or not t.strip():
                continue
            core = CODE.sub("", t).strip()
            words = WORD.findall(core)
            if len(words) >= 3 and len(core) > 18:
                en_sentence += 1
                tb = r.get("table", "")
                by_table[tb] = by_table.get(tb, 0) + 1
                if len(samples) < 8:
                    samples.append((len(core), core[:100]))
            else:
                key_like += 1
    print("==", ch, "总", tot, "| 疑似未译英文句", en_sentence, "| 键名/短串", key_like)
    print("   样本：")
    for n, s in samples:
        print("    (%d) %s" % (n, s))
    top = sorted(by_table.items(), key=lambda x: -x[1])[:10]
    print("   分表前10：", top)
