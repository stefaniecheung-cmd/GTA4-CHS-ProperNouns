# P4 字形层·代码侧（自写 hook）交接文档

> 给新开会话窗口用。目的：让新窗口不必从零摸索，直接接手「游戏内汉字渲染」这条线。
> 撰写时间：2026-11-08。撰写方：主会话（正在跑 P3/P4 上游润色）。

---

## 一、这条线要做什么

让游戏用同一套字体渲染链路画出**自建的 3,596 个汉字码点**，从而：
1. 中文正文真机可见（当前 P3 hook 只解决「读哪份 gxt」，没解决「字怎么画」）；
2. 解锁 FusionFix 菜单中文化（161 条资产已就位，卡在字形层）；
3. 之后才允许移走旧补丁 `plugins\GTA4.CHS.asi`（用户拍板顺序如此）。

**已有成果（资源侧全部完成，只差代码侧）**：
- `C:\Game\_tools\p4_work\char_table_v2.dat` — 14,388 B / 3,596 码点（旧 3,580 ∪ 新增 16：`©¬®ÈÉàáçèéñúü™噗泞`）
- `C:\Game\_tools\p4_work\atlas_v2.png` — 4096×4096 / 2,146,939 B
- `C:\Game\_tools\p4_work\atlas_v2.dds` — 16,777,344 B（BC3/DXT5，生成时**必须** `texconv -m 1`，否则 mip 链撑到 22,369,776 B 打不进 16MB 段）
- `fonts_base_v2.wtd` 1,590,798 B / `fonts_TLAD_v2.wtd` 1,655,842 B / `fonts_TBoGT_v2.wtd` 1,747,718 B（均「解压校验 OK」）
- 这些**都还没部署**，只在 `p4_work` 里。

---

## 二、已实证的容器格式（别重复踩）

### WTD
- 12 字节 RSC5 头 `52 53 43 05 08 00 00 00 10 00 09 f0`，其余全是 zlib 流：`zlib.decompress(data[12:])`
- 解压后是 RAGE 纹理字典，3 条目（`font_chs.dds` / `font1.dds` / `font3.dds`），基址 0x230 / 0x280 / 0x2D0
- 条目字段：+0x14 去 `0x5` 基址指向路径串（0x320 / 0x340 / 0x350）；+0x1C / +0x1E 宽高 u16；+0x20 fourCC `DXT5`
- 图集数据在文件末尾连续段，偏移 base/TLAD = 0x201000、TBoGT = 0x301000，长度均 16,777,216 B
- 解压总长：base 18,878,464 / TLAD 18,878,464 / TBoGT 19,927,040
- **wtd 内没有 `DDS ` magic**，不是标准 DDS 封装，别按 DDS 解析

### 旧补丁（作为逆向参照，不是要复用）
`C:\Game\Grand Theft Auto IV\plugins\GTA4.CHS.asi` — 232,960 B，x86，ImageBase 0x10000000，EP 0x1DDB8
- 符号：`gta_font::register_patches`（lambda_1~14，**14 处补丁点**）、`gta_whm::register_patches`
- 资源引用点：`font_chs` push @`0x10006635`；`char_table.dat` push @`0x1000C879`；`whm_table.dat` push @`0x1000C8C7`
- 旧资源：`char_table.dat` 14,324 B（3,580 码点）/ `whm_table.dat` 780,676 B（5,388 项）
- 旧补丁靠 hook「内部标识 → 显示文本」，`plugins\GTA4.CHS\custom_translations.json`（3,046 B / 86 条）即替换表；菜单标签 ASCII 编译在 `.asi` 内、不读外部文本
- **已写未跑的分析脚本**：`C:\Game\_tools\dump_asi.py`、`analyze_asi_refs.py`、`check_cell_layout.py`

### 我们自己的补丁
- `plugin\z_gta4cn.asi` 194,560 B，已部署，真机验收通过（gxt 重定向）
- `chs\config.ini`：`[General] Enable=true GxtDir=chs/gxt`；`[Font] FontPath=chs/font/default.ttf FontSize=18 AtlasSize=1024`；`[Hook] GxtFileName=zchs.gxt`
- `chs\font\default.ttf` 9,755,440 B（**字形渲染尚未实现**）

---

## 三、环境约束（踩过的坑，别重复）

- 游戏根 `C:\Game\Grand Theft Auto IV`；`GTAIV.exe` 17,425,752 B / FileVersion 1.2.0.59 / SHA1 `32A3F889F9FCC572EA798213F2E9EB429EB0C9A3`
- PE：x86，ImageBase 0x00400000，EP 0x009F922B；`.text` VA 0x00401000；`.rdata` VA 0x00E73000；**带 ASLR，实测基址 0xC10000** → 任何写死绝对地址的 hook 必失败，必须按基址+偏移
- Python 3.13.16；capstone 5.0.7；pefile 2024.8.26；Pillow 13.0.0（**不支持保存 DDS**）；numpy 未装
- `texconv 2026.5.8.1` 在 `C:\Game\_tools\texconv.exe`，出 wtd 图集必须 `-m 1`
- **Ghidra 全量 auto-analysis 两次皆 `Java heap space`，`set MAXMEM=12G` 无效** → 别再用 Ghidra 全量分析，改用 capstone 定点反汇编 + pefile
- 独占全屏 `PrintWindow` 抓不到；需窗口模式 + `PrintWindow(hwnd, hdc, 2)`
- `GTA4.CHS.asi` 改名 `.asi.off` **不能禁用**且致乱码，只能移出游戏目录
- 部署目录是游戏根下 `chs\gxt\`，不是 `gta4-chs\chs\gxt\`；`update\common\text\zchs.gxt` 是 base 章实际覆盖入口

---

## 四、已定义的字符映射（改字前必看）

`apply_zh.py` 内 `CHAR_MAP`：
`·`→`･`、`（`→`(`、`）`→`)`、`…`→`...`、`–`→`-`、`“`→`「`、`”`→`」`、`’`→`'`
ASCII（<0x80）走原版字体 ASCII 区，不参与缺字判定。

---

## 五、建议的接手顺序

1. 先跑 `dump_asi.py` / `analyze_asi_refs.py` / `check_cell_layout.py`（已写未跑），把旧补丁 14 处补丁点摸清；
2. 用 capstone 在 `GTAIV.exe` 里定位字体渲染函数（取字 → 查字宽 → 贴图集 UV），不要用 Ghidra 全量；
3. 优先做「只替换资源 + 让旧 asi 读新 char_table」的最小验证（能最快看到汉字），再考虑完全自写；
4. 任何部署前先备份：`update\*\pc\textures\fonts.wtd` 与 `char_table.dat` 各存 `.bak_*`；
5. 注意：**替换 fonts.wtd 会与仍在运行的旧 asi 读的旧 char_table 错位致乱码** —— 要么同时换 char_table，要么先移走旧 asi。

---

## 六、与主会话的分工

- 主会话：继续 P3 / P4 上游润色逐条通读（队列 `data\review\上游润色_队列.tsv`，P3 18,725 条、P4 30,369 条），每次增量打包部署
- 本窗口：只管字形层代码侧，**不要动 `zh_global.tsv` 与 `build\` 下的 gxt**，避免与主会话写冲突
- 两边的共同产物只有 `p4_work` 与 `docs`

---

## 七、跑任何打包/部署脚本前必读（见 `docs\润色流水线-已知坑.md`）

即使本窗口不碰 gxt，只要你为了验证跑一次打包，就会踩同一条坑。要点内联如下：

### 坑 A：`apply_zh.py` 的输出不能接管道截断（重大，已发生一次）

```powershell
# 错误 —— PowerShell 拿到第一条输出就关管道，Python 下一次 print 抛 OSError Errno 22，
# 循环死在 base 之后，TBoGT 章静默不执行，而且 verify 与哈希都会「正常 PASS」
python -X utf8 "C:\Game\_tools\apply_zh.py" 2>&1 | Select-Object -First 1

# 正确 —— 重定向到文件再整份读
python -X utf8 "C:\Game\_tools\apply_zh.py" > "$env:TEMP\applylog.txt" 2>&1
Get-Content "$env:TEMP\applylog.txt"
```

判据：必须看到**三行**「应用 N 条译文」（正常 base 3307 / TLAD 957 / TBoGT 729 左右）。

### 坑 B：`gxt_verify_engine` PASS + 哈希 True 不能证明内容更新

它比对的是「build 里的 src 与 gxt 是否一致」，src 没更新时两边自然一致。**部署后必须从部署目录的 gxt 里按 crc 抽一条刚改的译文验内容**，判据是「改动落在哪章，那章的 gxt 字节数必须变」。

抽样工具已备好：`python -X utf8 C:\Game\_tools\_tmp_checkgxt.py`
注意 `gxt_extract.parse_gxt(path)` 返回 `(tables, entries)`，**entries 是三元组 `(name, crc, txt)`**，不是 dict。

### 坑 C：回写 `zh_global.tsv` 只能走 `patch_polish1.py`

手写 `csv.DictWriter(quoting=csv.QUOTE_NONE)` 整体重写会毁表。出问题用 `zh_global.tsv.bak_before_accept` 整表回滚，再让日志整表重放。

### 坑 D：`patch_polish1.py` 与 `fix_ctrl.py` 必须成对

`patch_polish1.py` → `fix_ctrl.py` → `qa_gate.py`，顺序不可颠倒。

### 坑 E：其他环境约束

- PowerShell 里 `python -X utf8 -c @'...'@` 含中文 + 反引号 + 双引号必崩 → 一律 `Write` 一个 `_tmp_*.py` 再跑
- `csv.DictReader` 读大 tsv 前先 `csv.field_size_limit(10**9)`，否则 `csv.Error`
- `dumpline5.py` 的 E/Z 都是截断文本，不能当完整原文用
- crc 手抄是最大出错点，落表前逐字核对 dump 行头 8 位

完整版：`C:\Game\gta4-chs\docs\润色流水线-已知坑.md`，`p4_work\给hook窗口_已知坑.md` 另存一份副本。
