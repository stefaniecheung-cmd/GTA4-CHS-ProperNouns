# -*- coding: utf-8 -*-
import struct, os, zlib

WHM = r"C:\Game\Grand Theft Auto IV\plugins\GTA4.CHS\whm_table.dat"
CHT = r"C:\Game\Grand Theft Auto IV\plugins\GTA4.CHS\char_table.dat"

raw = open(WHM, "rb").read()
print("whm size =", len(raw))
n = struct.unpack_from("<I", raw, 0)[0]
print("n (u32) =", n)
idx_off = 4
ts = idx_off + n * 8
print("index bytes =", n*8, " text region off =", ts, " text len =", len(raw)-ts)

entries = []
for i in range(n):
    h, o = struct.unpack_from("<II", raw, idx_off + i*8)
    entries.append((h, o))

offs = [e[1] for e in entries]
hs = [e[0] for e in entries]
print("offset 单调递增:", all(offs[i] <= offs[i+1] for i in range(n-1)), " max off:", max(offs))
print("hash 单调递增:", all(hs[i] <= hs[i+1] for i in range(n-1)))

# 解析每条文本区：先按变长试，看每条后面紧跟什么数值
def read_entry(i):
    h, o = entries[i]
    start = ts + o
    # 下一条 offset
    end = ts + (offs[i+1] if i+1 < n else (len(raw)-ts))
    seg = raw[start:end]
    # 解码字符（UTF-8 1/2/3/4 字节）
    ch = None; ln=0
    for L in (1,2,3,4):
        try:
            c = seg[:L].decode("utf-8")
            if len(c)==1:
                ch=c; ln=L; break
        except Exception:
            pass
    return h, o, seg, ch, ln

for i in range(10):
    h,o,seg,ch,ln = read_entry(i)
    print("[%2d] h=0x%08X off=%d seg=%s ch=%r tail=%s" % (i,h,o,seg.hex(" "),ch,seg[ln:].hex(" ")))

# 统计每条总长（用相邻 offset 差），看固定/变长
lens = []
for i in range(n):
    start = ts+offs[i]
    end = ts+(offs[i+1] if i+1<n else len(raw)-ts)
    lens.append(end-start)
from collections import Counter
print("条目字节长度分布:", Counter(lens).most_common(10))

# 解析 char_table
c = open(CHT,"rb").read()
m = struct.unpack_from("<I", c, 0)[0]
codes = [struct.unpack_from("<I", c, 4+i*4)[0] for i in range(m)]
print("\nchar_table 条目 =", m)

# 用 crc32(utf8) 或 crc32(u32) 匹配 hash 到码点
def crc(b): return zlib.crc32(b)&0xFFFFFFFF
# 建码点->hash 候选
cand_utf8 = {crc(chr(x).encode("utf-8")): x for x in codes}
cand_u16 = {crc(struct.pack("<H", x)): x for x in codes}
cand_u32 = {crc(struct.pack("<I", x)): x for x in codes}
hit_u8=hit_u16=hit_u32=0
whm_chars=set()
for h,o in entries:
    if h in cand_utf8: hit_u8+=1; whm_chars.add(cand_utf8[h])
    elif h in cand_u16: hit_u16+=1; whm_chars.add(cand_u16[h])
    elif h in cand_u32: hit_u32+=1; whm_chars.add(cand_u32[h])
print("hash 命中: crc_utf8=%d crc_u16=%d crc_u32=%d" % (hit_u8,hit_u16,hit_u32))
missing = [x for x in codes if x not in whm_chars]
print("char_table 中未在 whm 登记的码点数 =", len(missing), "/", m)
