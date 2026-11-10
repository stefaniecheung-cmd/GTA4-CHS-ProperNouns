# RESUME · 接续说明

> 本文件是**机器可校验的一页纸接续包**。上下文丢失、换会话、换模型后，先读本文件，
> 再读 `data/review/润色线-断点.json`（权威数字），即可无缝继续。
> 生成时间：2026-11-09 09:53:19

---

## 一、一句话现状

**润色线 P3 已审到 offset 11065 / 18725，剩 7660 条；下一批从 11066 起。**
渲染线（hook/UV）**已冻结**，等翻译资产全部跑完，再与新版 ASI `GTA4.CHS.fix.asi` 整合。

---

## 二、开工前三条命令

```powershell
# 1) 看当前断点（权威数字，永远以它为准，不要相信任何文档里的旧数字）
cd C:\Game\_tools
python -X utf8 pass_state.py --show

# 2) 导出下一批（60 条四语对照，E|D|F|Z）
python -X utf8 dumpline5.py 3 11066 60 > "$env:TEMP\hq.txt"

# 3) 通读 $env:TEMP\hq.txt，逐条判断，然后按下节流程落表
```

---

## 三、每批固定流程（顺序不能错）

| 步 | 命令 | 说明 |
|---|---|---|
| 1 | 写 `_tmp_log_p<offset>.py` 追加日志 | 新译**必须继承** old 的前缀控制符（`~z~`/`~s~`/`~x~`）|
| 2 | `python -X utf8 patch_polish1.py` | 日志 → 覆盖表 `zh_global.tsv` |
| 3 | `python -X utf8 fix_ctrl.py` | 补控制符（**必须在 2 之后**）|
| 4 | `python -X utf8 qa_gate.py` | 目标：`错误 0`，警告数应恒为 29 |
| 5 | `python -X utf8 pass_state.py --offset <新offset> --note "<本批摘要>"` | 刷新断点，**每批必做** |
| 6 | 每 2,000 条再做打包部署链 | `apply_zh.py` → `gxt_pack.py` → `gxt_verify_engine.py` |

**顺序坑（已踩过）**：先 `fix_ctrl` 再 `patch_polish1`，会把刚补的控制符用日志旧值冲掉，
qa 立刻报 112 个控制符错误。正确顺序是 `patch_polish1` → `fix_ctrl` → `qa_gate`。

**控制符坑（已踩过）**：新译若不带 old 的前缀 `~z~`，qa 会全量报错。写日志时用正则
`^(?:~[A-Za-z0-9_]{1,20}~)+` 从 old 提取前缀，拼到新译前面。

---

## 四、判据口径（用户原话，最高优先级）

1. **唯一判据：原文语义是否到位。** 原文有的必须译出，原文没有的**不许自加**。
2. **没有禁用词。** 侮辱词按原意译出，**不做净化**。
3. 遇歧义时**对照德语、法语同键位译文** + 上下文语境定夺。
4. **拿不准的才问用户拍板**，能判的直接改，不要每批都汇报。
5. **控制符（`~z~` `~s~` `~x~` `~c~` `~n~` `~BLIP_n~` `~INPUT_x~`）必须原样保留**，
   数量与顺序不得增删。
6. 专名（人名/地名/店名/公司名）**保留原文**，不自行音译。
7. 常用错译识别点：`one shot deal`≠转瞬即逝；`get my own place`≠一席之地；
   `sure you will` 是反讽；`a dive` 是破店；`owner`≠店长。

---

## 五、环境事实（踩过的坑，别再试）

- **`cmd` 不在 PATH**，必须 `C:\Windows\System32\cmd.exe`
- 本机**无 `numpy`**，图像统计只能纯 PIL 手写循环
- 无 `curl.exe`、无 r2/rizin/IDA/RetDec
- Python 一律加 `-X utf8`，否则中文表会乱码
- PowerShell 变量名大小写不敏感（`$Out` 与 `$out` 互相覆盖）
- 前台命令超 15 s 自动转后台，需 `TaskOutput` 取结果
- `csv.field_size_limit(10**9)` 必加，否则大文本行报错
- 读带 BOM 的日志用 `encoding="utf-8-sig"`
- **改 `.md` 不能用 Edit**，统一用 python 写 + 先 `shutil.copy2` 备份

---

## 六、关键文件索引

| 用途 | 路径 |
|---|---|
| 权威断点（机器可读） | `data/review/润色线-断点.json` |
| 断点刷新器 | `C:\Game\_tools\pass_state.py` |
| 队列（58,157 条，按 priority 分层） | `data/review/上游润色_队列.tsv` |
| 覆盖表（译文真身） | `data/zh_global.tsv` |
| 审读日志（改动记录） | `data/review/上游润色_审读日志.tsv` |
| 四语语料 | `data/corpus_base.tsv` / `corpus_TLAD.tsv` / `corpus_TBoGT.tsv` |
| 导出对照 | `C:\Game\_tools\dumpline5.py <prio> <off> <n>` |
| 写回脚本（唯一合法写回） | `C:\Game\_tools\patch_polish1.py` |
| 质检 | `C:\Game\_tools\qa_gate.py` |
| 打包 | `apply_zh.py` → `gxt_pack.py` → `gxt_verify_engine.py` |
| 进度存档（人读） | `docs/润色线-进度存档.md` |
| 双线状态板 | `docs/双线状态板.md` |
| 渲染线逆向结论 | `docs/REA-宽度层逆向-取证与结论.md` |

---

## 七、还有哪些活没干（按队列）

| 层 | 数量 | 状态 |
|---|---|---|
| P1 | 7,950 | 已部署 |
| P2 | 1,113 | 已部署 |
| **P3** | 18,725 | **11065 已审，剩 7660** |
| P4 | 30,369 | 未开始 |
| 街道/地名 | 439 | 未开始 |
| 缺字 | 7 个（虱/辖/啵/钾/墩/瘆/撬）| 未补 |

---

## 八、渲染线：已冻结，别重启

- 自研 `gta4cn.asi` 的 UV/宽度攻关**暂停**。结论：引擎 UV 消费层是 16 列硬编码
  （`slot & 0xF`）+ `40/512` 行距，与 64 列 / 66 行距 / 18 起点的图集天生不匹配；
  改 `A+0x28` 只改「一格多宽」，改不了「第几格」。
- **新方案**：翻译资产跑完后，改用第三方 ASI `GTA4.CHS.fix.asi` 负责字形渲染
  （它与旧汉化同框架，自带完整画字路径，不受引擎 UV 网格限制），我们提供文本层
  `american.gxt`（= 我们的 `zchs.gxt` 改名，524 表 / 59,661 条与原版逐条对齐）。
- 已知硬伤：该 ASI 的 `char_table.dat` 只有 3,517 字，我们译文用到 3,212 种字符里
  有 **72 种缺失**（`･` 992 次、`琪` 182 次、`冈` 162 次等）。整合前必须先解决，
  或统一把 `･`(U+FF65) 换成 `·`(U+00B7)（两边字符集都有）。
