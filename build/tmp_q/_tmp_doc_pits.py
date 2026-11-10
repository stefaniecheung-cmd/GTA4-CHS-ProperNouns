# -*- coding: utf-8 -*-
import io

p = r"C:\Game\gta4-chs\docs\润色流水线-已知坑.md"

sec = """
## 坑：fixes 的「新译正文」不能以颜色标签开头（P1 段实证，一次 10 条）

`fix_ctrl.py` 会按**原文**自动补开头颜色标签。若 fixes 里自己写了 `~z~~x~正文`，
`fix_ctrl` 会再补一层，得到 `~z~~x~~z~~x~正文`，`qa_gate` 报 `E [控制符]`。

**纪律**：fixes 第 4 列只写正文，开头标签一律交给 `fix_ctrl`。

**事后修法**：不要重交 fixes（会命中「已同」跳过）。写纯文本 split/join 脚本，
同时改 `zh_global.tsv` 第 1 列与日志 `p[5]`（**crc 在 `p[2]`**，`p[0]` 是 chapter），
先 `shutil.copy2` 备份，`newline="\\n"`。参考 `build\\tmp_q\\_tmp_fixdup.py`。
禁止用 csv 模块整表重写。

## 坑：`~s~` / `~1~` 标签位置与顺序不能自造（`1084AEED`）

原文 `~s~Go to SoBoHoe's by ~1~:~1~.`（标签 `['~1~','~1~','~s~']`）。
手写 `~s~~1~~s~~1~:~1~ 前到 SoBoHoe 家。` 会让译文标签数多于原文，
`fix_ctrl` 再补一个 `~s~` 后 `qa_gate` 报 `E [控制符]`。

**纪律**：译文只写 `~1~:~1~ 前到 SoBoHoe 家。`，让 `fix_ctrl` 按原文补 1 个 `~s~`。
标签严格按原文的**数量与位置**还原，不调整顺序、不合并、不拆分。

## 坑：P1 段只打包 base 一章

P1 队列（priority=1，7,950 条）在本段推进的区段全是 `base|MAIN` 条目。
TLAD / TBoGT 的 `src_*_tr.tsv` 在 `apply_zh` 后会被刷新（`apply_zh` 三行全跑），
但内容未变，**不需要重跑 `gxt_pack`**——只跑 `gxt_pack.py src_base_tr.tsv zchs_base_tr.gxt` 即可，
TLAD/TBoGT 字节保持不变（778,430 / 973,552）。
"""

with io.open(p, "ab") as f:
    f.write(("\n" + sec).encode("utf-8"))
print("appended", len(sec))
