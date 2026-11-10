# -*- coding: utf-8 -*-
import io

p = r"C:\Game\gta4-chs\docs\润色线-进度存档.md"
raw = io.open(p, "rb").read()
enc = "utf-8-sig" if raw[:3] == b"\xef\xbb\xbf" else "utf-8"

sec = """
## P1 队列收尾（2026-11-09 20:52）

P1（priority=1，7,950 条：专名/短词/车名/绰号 + base|MAIN 大段对白、电台台词、UI 提示、短信）已全部走完。
本轮自 6,366 断点起连续推进 34 批（6,366→7,950），每批 100 条（末批 85 条）。

**构建读数（P1 收尾）**

| 项 | 值 |
|---|---|
| `apply_zh` 生效条数 | base **9,661** / TLAD 2,486 / TBoGT 2,816 |
| `zchs_base_tr.gxt` | **2,670,200 字节** |
| `zchs_TLAD_tr.gxt` | 778,430 字节（本段无改动，未重打包） |
| `zchs_TBoGT_tr.gxt` | 973,552 字节（同上） |
| `qa_gate` | 「检查 **14,040** 条，错误 **0**，警告 **17**」（17 为既有「多换行」常驻豁免，拍板 B3 不改） |
| 审读日志 | **12,102 行** |
| 覆盖表 `zh_global.tsv` | **13,235 行**（含表头） |

三章打包均「文本逐条比对: 不一致 0 条」。

**部署状态**：**未部署**。游戏侧仍是 `p49725`（2,669,910 / 778,430 / 973,552，各带 `.bak_p49725`），
build 与游戏侧 base 已差 40,290 字节。P1 之后无部署阈值约定，下次部署需用户点头。

**断点**：`p1{total 7950, offset_done 7950, remaining 0, next_from 7951}`；`p2{1113, 0, 1113, next_from 7951}`；
`passed_offset 57044`、`remaining 1113`（正好剩 P2）。已写回 `润色线-断点.json`。

### 本段（P1）集中修正的语义类型

1. **人名口径统一**：`Niko`/`Nicky`/`Niko boy` → 一律「尼克」（本段改了 30+ 条）；`cousin` → 「堂弟」（`F2DBC226`/`B8EDBAAE` 等，原译「你哥」的关系错误已修）。
2. **车型/品牌专名保留英文**：`Karin Dilettante`（`27A0F303` 原译「半吊子」）、`Dilettante`（`ECF728A5`）、`Sabre GT`（`507DEE3D` 原译「军刀涡轮」）、`Emperor`（`588DF684` 原译「皇霸天」）；`Holland Hustlers`（`B27635AB`/`2431991C`/`FADBC671`/`E97B23B0`/`14E9FA8D`，原译「荷兰皮条客帮」把 Hustlers 误读成皮条客）；`Insurgiscan`（`7ACF5842`/`7F28E215`，原译「叛乱扫描仪」）；`Playboy X`（`8B577DFE`/`7151`）；`Von Crastenburg` → 「冯·克拉斯滕堡」（`72A372E4`/`0EA62C47`，原译「克拉斯顿堡」漏 Von）。
3. **原文漏译整句**：`346DAEC5`（漏 `I'm surprised the ER wasn't full of your victims`）、`FD1F893A`（漏 `since her 11th birthday`）、`062CC17B`（漏 `with extreme satin finish`）、`A61E10B5`（漏 `for this tour`）。
4. **译文多出控制符/换行**：`25A228B1`/`38A92C69`/`4707AF14`/`8900A803`/`B194C1E0`/`DAE51C17`/`24780912`/`F0AEE4CD` 原文无 `~n~` 而原译多插，已删；`8B38A457` 标签与拉丁名挤在一起，补分隔空格。
5. **方向/主语反解**：`EE1CD506`（below the radar「下方」原译「上方」）、`0DE34CA5`（fly under「从桥下飞过」原译「穿桥引线」）、`CEE772C9`（`got confused` 主语是「我自己搞糊涂」）、`D115DDAB`（`would kill to date her` 强度被削）、`F511E6D2`（`put me in a chair` 被动被译成赠予）、`A25EC1F9`（前后逻辑接反）、`25B1914D`（`A lot of good you are` 反讽被译成褒扬）。
6. **UI/系统提示语病**：`FF5BDDCE`（相机说明整句不成句）、`08645444`（客服腔「这边建议您…哦」）、`4A4D` 类「您需要在哪里的帮助」病句（`7397`/`7868`）、`BAEDA7D9`（`more matches` 误读成「更多房间」）、`7A5B91A4`/`CF2A3AE8`（`exit dance` 译成「退出观看」）、`9C056DC3`（`skip the tour` 译成「跳过旅途」）。

### 本段新增的两条坑（已写入实操纪律，建议并入 `润色流水线-已知坑.md`）

1. **fixes 的「新译正文」不能以颜色标签开头**。`fix_ctrl` 会按原文自动补开头标签，自写 `~z~~x~` 会被再套一层变成 `~z~~x~~z~~x~`，qa 报 `E [控制符]`（本段一次 10 条）。修法：写 `_tmp_fixdup.py` 纯文本 split/join 改 `zh_global` 第 1 列 + 日志 `p[5]`（**crc 列 `p[2]`**），压回单层。
2. **`~s~`/`~1~` 标签顺序也不能自造**。`1084AEED` 手写 `~s~~1~~s~~1~:~1~` 被 `fix_ctrl` 再补一层 `~s~` → `E [控制符]`。修法：只写 `~1~:~1~ 前到 SoBoHoe 家。`，让 `fix_ctrl` 按原文补 1 个 `~s~`。
3. **P1 段只需跑 base 一章的 `gxt_pack`**（本段 34 批队列全是 `base|MAIN`，TLAD/TBoGT 无改动，字节不变）。

**备份**：本段新增 `zh_global.tsv.bak_before_p1dup` / `.bak_before_p1dup2` / `.bak_before_sbo`，
`上游润色_审读日志.tsv.bak_before_p1dup` / `.bak_before_p1dup2` / `.bak_before_sbo`；本文件 `.bak_before_p1end`（本段追加前）。
"""

with io.open(p, "ab") as f:
    f.write(("\n" + sec).encode("utf-8"))
print("appended", len(sec), "chars; enc=", enc)
