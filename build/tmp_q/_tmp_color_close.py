# -*- coding: utf-8 -*-
"""全量扫描定稿 gxt：找出中文译文里"句中彩色段未闭合"的潜在串色条目。
对照 corpus 英文与 v10 成品。物理行/parse_gxt 全量，不走 DictReader。"""
import sys, os, re, csv, io, collections
csv.field_size_limit(10**9)
sys.path.insert(0, r"C:\Game\_tools")
from gxt_extract import parse_gxt

G = r"C:\Game\Grand Theft Auto IV"
B = os.path.join(G, "gta4-chs", "build")
D = os.path.join(G, "gta4-chs", "data")
V10 = r"C:\Users\yy253\Desktop\GTA4 简中补丁之补丁（含AI翻译）v1.0"
OUT = os.path.join(B, "cmp_assets")

CODE = re.compile(r"~[A-Za-z0-9_]+~")
# 真正的字母颜色码；~a~玩家名槽位 ~e~章节占位 ~1~-~4~数字占位 不算颜色
COLOR = {"~b~","~r~","~y~","~g~","~c~","~x~","~m~","~w~","~k~","~l~",
         "~d~","~f~","~h~","~i~","~j~","~o~","~p~","~q~","~t~","~u~","~v~"}
RESET = "~s~"; SPEAKER = "~z~"; NL = "~n~"
# 占位/变量/按键码：不染色、不打断彩色段
PLACEHOLDER = re.compile(r"~(a|e|1|2|3|4|COL_NET_\d|BLIP_\d+|PAD_[A-Z_]+|INPUT_[A-Z0-9_]+)~")

CHAPS = [
    ("base",  os.path.join(B, "zchs_base_tr.gxt"),  os.path.join(V10,"update","common","text","american.gxt")),
    ("TLAD",  os.path.join(B, "zchs_TLAD_tr.gxt"),  os.path.join(V10,"update","TLAD","common","text","american.gxt")),
    ("TBoGT", os.path.join(B, "zchs_TBoGT_tr.gxt"), os.path.join(V10,"update","TBoGT","common","text","american.gxt")),
]

def load_corpus(ch):
    m = {}
    with open(os.path.join(D, f"corpus_{ch}.tsv"), encoding="utf-8-sig") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {k:i for i,k in enumerate(head)}
        for line in f:
            q = line.rstrip("\n").split("\t")
            if len(q)!=len(head): continue
            m[q[ix["crc"]].strip().upper()] = q[ix["english"]]
    return m

def segs(s):
    out, last = [], 0
    for m in CODE.finditer(s):
        if m.start()>last: out.append((None, s[last:m.start()]))
        out.append((m.group(), "")); last = m.end()
    if last<len(s): out.append((None, s[last:]))
    return out

def analyze(zh):
    """返回未闭合彩色段描述列表：段内明文 + 段后是否还有普通明文。"""
    sg = segs(zh)
    issues = []
    i = 0
    n = len(sg)
    while i < n:
        code, plain = sg[i]
        if code in COLOR:
            j = i+1; seg_text = ""; closed = False; switched = False; tail_plain = ""
            while j < n:
                c2, p2 = sg[j]
                if c2 == RESET:
                    closed = True; break
                if c2 in COLOR:
                    switched = True; break
                if c2 == SPEAKER:
                    break
                # NL 换行、占位/变量/按键码不打断彩色段
                seg_text += p2
                j += 1
            k = j
            if closed: k = j+1
            while k < n:
                c3, p3 = sg[k]
                if c3 in (COLOR, RESET, SPEAKER): k+=1; continue
                tail_plain += p3; k+=1
            issues.append({"color":code, "seg":seg_text.strip(), "closed":closed,
                           "switched":switched, "tail":tail_plain.strip()})
            i = j
        else:
            i += 1
    return issues

rows = []
for ch, zp, vp in CHAPS:
    corp = load_corpus(ch)
    _, ze = parse_gxt(zp)
    _, ve = parse_gxt(vp)
    vmap = {("%08X"%c): x for t,c,x in ve}
    for t, c, zh in ze:
        crc = "%08X"%c
        iss = analyze(zh)
        # 真嫌疑：彩色段未闭合(closed=False) 且 段后还有普通明文(tail 非空) => 后续文字会被染色
        suspects = [x for x in iss if not x["closed"] and not x["switched"] and x["tail"]]
        if suspects:
            en = corp.get(crc, "")
            rows.append((ch, t, crc, en, vmap.get(crc,""), zh,
                         " || ".join(f'{x["color"]}[{x["seg"]}]尾部:{x["tail"]}' for x in suspects)))

print("潜在未闭合彩色段条目:", len(rows))
bych = collections.Counter(r[0] for r in rows)
print(dict(bych))

with io.open(os.path.join(OUT, "风险_彩色段未闭合_全量.tsv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["章节","表","CRC","英文原文","v10成品","我方定稿","未闭合段"])
    for r in rows: w.writerow(r)

for r in rows[:60]:
    print(f"\n[{r[0]} {r[1]} {r[2]}]")
    print(f"  EN : {r[3][:75]}")
    print(f"  v10: {r[4][:75]}")
    print(f"  我方: {r[5][:75]}")
    print(f"  段 : {r[6][:80]}")
