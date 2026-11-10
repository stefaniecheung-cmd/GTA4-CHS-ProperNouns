# -*- coding: utf-8 -*-
import io, os, shutil, csv, sys
csv.field_size_limit(10**9)
ROOT = r"C:\Game\Grand Theft Auto IV\gta4-chs"
GP = os.path.join(ROOT, "data", "zh_global.tsv")
BK = os.path.join(ROOT, "build", "tmp_q", "backup_zh_global_20261110.tsv")

# (crc, chapter) -> (new_zh, was备注)
UPD = {
    ("2C924360", "base"): ("~z~因为他们卖出的枪支流到了这边的街头。", "补译：原译文占位问号"),
    ("9AF702B1", "base"): ("~z~你妈的！", "粗口译中文脏话"),
    ("BF73CBAA", "base"): ("~z~傻逼！", "粗口译中文脏话"),
    ("D3CE008D", "base"): ("~z~我操。", "粗口译中文脏话"),
    ("92984525", "base"): ("~z~操他妈的。", "粗口译中文脏话"),
    ("FB0B04EC", "base"): ("~z~同志们！", "Comrades 译"),
    ("4C6144A0", "TLAD"): ("~z~废物！废物！废物！", "Deadbeats 译，与 4FC055AF 统一"),
    ("4FC055AF", "TLAD"): ("~z~干掉那群废物，比利。", "Deadbeats 译，与 4C6144A0 统一"),
    ("E8506E8D", "TLAD"): (
        "我们能够快速消灭你的债务，没有任何痛苦，并且不会影响你的个人征信。我们卖的是财务自由。"
        "也许你已经毁掉了自己的一生，并且再也无法恢复，但我们可以帮你！买东西为什么还要付钱？"
        "赊出你的新未来。今天是你负债生活的第一天。 "
        '<a href="www.killdebtdead.com">www.killdebtdead.com</a>',
        "补译：原仅残留网址"),
    ("B558BA99", "TBoGT"): ("~z~「名人终结者」？", "Celebrinator 绰号译"),
    ("9603CE32", "TBoGT"): ("~z~嘿，你好吗，伙计？", "删重复 ~z~"),
}

# 备份
shutil.copy2(GP, BK)
print("已备份:", BK)

with io.open(GP, encoding="utf-8") as f:
    lines = f.readlines()

head = lines[0].rstrip("\n").split("\t")
assert head == ["crc", "zh", "chapter", "english", "was"], head
idx = {k: i for i, k in enumerate(head)}

updated = set()
out = [lines[0]]
for line in lines[1:]:
    if not line.strip():
        out.append(line); continue
    q = line.rstrip("\n").split("\t")
    while len(q) < 5: q.append("")
    key = (q[idx["crc"]].strip().upper(), q[idx["chapter"]].strip())
    if key in UPD:
        new_zh, was = UPD[key]
        old = q[idx["zh"]]
        q[idx["zh"]] = new_zh
        q[idx["was"]] = was
        updated.add(key)
        print(f"[改] {key[1]} {key[0]}\n     旧: {old!r}\n     新: {new_zh!r}")
    out.append("\t".join(q) + "\n")

# 新增未命中的条目（9603CE32）
for key, (new_zh, was) in UPD.items():
    if key not in updated:
        crc, ch = key
        out.append("\t".join([crc, new_zh, ch, "", was]) + "\n")
        print(f"[增] {ch} {crc}\n     新: {new_zh!r}")

with io.open(GP, "w", encoding="utf-8", newline="\n") as g:
    g.writelines(out)

print("\n更新/新增条目数:", len(updated), "+", len(UPD)-len(updated))
print("总数据行:", len(out)-1)
