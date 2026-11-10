# P4 字形层·代码侧 交接（2026-11-08 收尾版）

> 交接对象：主窗口 / 润色线。
> 本文是本窗口（hook 窗口）的最终状态。**下文每一条都标了「已证实 / 未证实」，未证实的不许当前提用。**

---

## 一、一句话结论

字形链路的**取字、算 UV、写顶点**三段都已打通并有硬证据；
卡在最后一环——**采样到的贴图与坐标系统不自洽**，导致真机仍不显示汉字。
方案已定（方案 A 的「零影响」变体），代码与资源的改动点已定位到具体地址与文件，
但**本窗口没有把它落地到能看画面的程度**，交给下一窗口继续。

---

## 二、已证实的事实（可直接依据，不要重新定位）

### 2.1 完整链路

```
0x921140  入口分流（cmp [0x10366C8],0 → 路径 B；实测恒为 0）
  └ 0x921534  路径 B
      ├ 0x921537 call 0x91C7C0   测宽
      ├ 0x92154A call 0x91BC80   查槽位+字宽
      ├ 0x92159E ← hook ① StubMap（char → 映射表槽位）
      └ 0x92176E ← hook ② StubDraw（UV 已算完、组 quad 参数前）
          └ 0x9217EA call 0x91B850   字形四边形
              └ 0x90A360            写顶点（36 B/顶点，缓冲 0x1195F70，满 170 提交）
                  └ 0x923140        绑 fontRec[font]+0x240 贴图 → 0x8D4340 提交
```

硬证据：
- `0x8D4340` 全游戏只有 2 个调用点（`0x923183`、`0x9231C2`），都在 `0x923140` 内 → **文字顶点唯一通道**。
- 三探针（测宽 `0x91C7C0` / 写顶点 `0x90A360` / 四边形 `0x91B850`）真机计数同步放大。

### 2.2 字体号（推翻「font0 是主字体」的旧假设）

改门前一次取证（`sdByFont` 按 dl 计数）：

```
stubDraw sdN=2118  sdxN=0
sdByFont: f0=2118  f1=18324  f2=0  f3=0
lookN=2118  hit=0
```

**菜单/页签文字 18,324 次绘制全部走 font1；font0 那 2,118 次画的是数字与英文（hit=0，一个汉字都没命中）。**
两处 hook 原本都有 `dl==0` 门 → font1 完全没被接管 → 页签全是 `!`（font1 的原版图集里没有汉字，引擎兜底成 `!`）。

现状：门已移除，font1/font3 也被接管。实测 `sdN=513,992 / sdxN=388,699 / uvApplied f0=324,167 f1=11,538 f3=52,994`。

### 2.3 UV 计算与写入：正确

`Pr1` 探针从 `0x90A360` 入参抓到的真实浮点：

```
vtx8: 位置 1639.62 925.82 1643.52 904.57 | UV 0.96094 0.02344 0.97266 0.01562
```

`0.96094` = 我们的 U，`0.97266 − 0.96094 = 0.00781 = 32/4096` = 我们的格宽，
与 `idx=379` 在 128 列图集里的格位完全一致。**「算 UV → 写进顶点缓冲」这一环彻底通。**

### 2.4 资源侧 wtd：正确

- `fonts_base_v2.wtd` 1,590,798 B；12 B 头 + zlib，解压 18,878,464 = `0x201000` + 16 MB；
- 图集段 16,777,216，块数 1,048,576 校验通过；图集段前 32 B 与 `atlas_v2.dds` 数据段一致；
- 内部三张纹理：`pack:/font_chs.dds`（**4096×4096 DXT5**）、`pack:/font1.dds`、`pack:/font3.dds`；
- 按 4 KB 采样 4096/4096 块组有内容（不是空图）。

### 2.5 引擎 UV 公式（反汇编 `0x9216BF` 分支，font≠2）

```
xmm2 = 1.0 / [fontRec+0x240+8]      ; = 1/512
xmm1 = [fontRec+0x246]              ; 40.0
xmm4 = [fontRec+0x250]              ; 39.5
xmm6 = [fontRec+0x24C]              ; 4.0
行 = si >> 4，列 = si & 0xF
U = 列 * [0xfe8778]                 ; 1/16
V = (行 - 基值) * (40/512) + 4/512 - 39.5/512
```

**这套公式产出的是「512² 图集坐标」，不是 4096 坐标。**

### 2.6 栈帧与宽度槽（已按反汇编逐条核实）

函数帧 `sub esp,0x30` + `push esi/edi`，记 **A = sub esp 之后的 esp**，hook 入口 esp = A − 8。

| 槽 | 语义 | 证据 |
|---|---|---|
| `[esp+28h]`（= A+0x20） | **宽度（UV 增量，U_right = U + 此值）** | `0x9217A6 addss xmm7,[esp+0x30]`，此刻 esp=A−0x10（已两次 push） |
| A+0x00 ~ A+0x0F | 传给 `0x91B850` 的第 1 个 float 块 | `0x9217B1/0x9217D8/0x9217E4` |
| A+0x14 ~ A+0x23 | 传给 `0x91B850` 的第 2 个 float 块（含 UV） | `0x9217AC lea eax,[esp+0x20]` |
| A+0x2C | **特殊字符标志**：非 0 → `0x921763 jne 0x9217F2` 直接不画 | `cmp byte [esp+0x34],0` |
| A+0x34 / A+0x38 / A+0x40 | 调用方传入的 x / y / 参数 | `0x921780/0x921790/0x92178C` |

**注意**：宽度槽引擎自己的值就是 `4.0/512 = 0.0078125`，与我们写的 `32/4096` 完全相同
→ **这个写操作等价于 no-op，它不是「文字消失」的原因**。此前我把它写成 `[esp+30h]` 和 `[esp+1Ch]` 都是错的（现在已改对）。

**`A+0x2C` 要特别小心**：`si == 0xFD` 或 `si == 0xFFFF` 时会被置 1 → 直接跳过绘制。
我们在 `StubMap` 里把 `si` 置 0，需要确认没有走 `0x9215DB` 的 `cmove` 分支（**运行期未取证**）。

---

## 三、未解决的核心矛盾（交给下一窗口的第一件事）

在「font1/font3 贴图指针改指我们的 4096 图集 + 全字体覆写 UV」的组合下，真机表现是
**所有文字（含 ASCII）彻底消失**，不是 `!`，也不是乱码。

现有静态证据**无法解释**这一点：
- UV 是对的（2.3）、贴图指针已统一（`tex=0x45D95250 0x45D95250 0 0x45D95250`）、资源是好的（2.4）；
- 即使坐标系不匹配，ASCII 的 512 坐标也应落在图集左上 1/8（那里是第 0~255 号汉字格），**至少该显示成随机汉字，而不是空白**。

因此判断：**空白不是坐标系问题，另有原因**（候选：`A+0x2C` 标志位被置 1 跳过绘制 /
批次提交时绑到的贴图并非我们以为的那张 / quad 尺寸塌陷）。
**下一窗口不要再猜，先落「顶点缓冲 dump」**（直接读 `0x1195F70` 的 36 B 顶点与 `0x923140` 绑定的指针），
把「UV 对不对 / 贴图是哪张 / quad 多大」三件事一次分开。

---

## 四、已定方案（用户已拍板：走 A，A 不行再 C）

详见 `docs\P4-字形层-实现方案.md`。核心是**方案 A 的「对润色线零影响」变体**：

1. **图集重烘焙**：4096 图集**左上 512×512** 按原版 font1/font3 布局（16 列、行高 40）1:1 画入 ASCII/标点镜像；
   汉字从 **y=512 起排**（`rowBase = 16`）。
2. **`glyphs.dat` 逐字节不变**：索引 i → 行 `16 + i/128`、列 `i%128`。只改 UV 计算里的行基址常量。
   → **润色线的字符表、gxt、tsv 全部零改动。**
3. font1/font3 的 `+0x240` 指向我们的 4096 图集，改为「字体加载完成后一次性写」，删掉周期重申。
4. 汉字覆写 UV（含 `rowBase=16`）；ASCII/标点**不覆写**，走引擎原 UV 正好命中左上镜像区。
5. 三章 wtd 重打，各留 `.bak_p4b`。
6. 后续新增字符只走「追加」（汉字区尾部续排 + `glyphs.dat` 追加条目），**永不重排**。

备选 C：在「画一个字的调用点」打 inline hook，handler 自己算 quad、自己绑贴图、自己提交（旧补丁路线）。
注意旧补丁 asi 侧的 RVA（`0x6660` / `0x6210` / `0x5F70`）**全是 asi 自己的（ImageBase 0x10000000）**，不能直接抄。

---

## 五、当前文件与状态

### 代码

- `gta4-chs\src\font.cpp` 是本窗口唯一改过的源文件，当前真值：
  - `g_orig1Len=31` / `g_orig2Len=9`；`kInstallDrawSite=true`
  - `StubMap`（`0x92159E`）：**`dl==0` 门已删**，对所有字体生效；命中则 `si=0`，真实格位走 `g_idx`
  - `StubDraw`（`0x92176E`）：**`dl==0` 门已删**；进入即 `inc [g_sdN]`；覆盖 `xmm7/xmm4/xmm6`；
    宽度写 **`[esp+28h]`**（唯一正确值，见 2.6）
  - `RetargetFontTextures()`：把 font1/font3 的 `+0x240` 改成 font0 的；**在 `DbgDumpThread` 每轮调用**
    → 这是权宜写法，正式版必须改成「加载后一次性写」
  - 探针 `Pr0/Pr1/Pr2` + `InstallProbe` + `g_prTramp/g_prResume/g_prOrig/g_prCw/g_prVx/g_prBq/g_vxBuf`
  - 计数 `g_sdN / g_sdxN / g_sdByFont[4] / g_sdxByFont[4] / g_sdLastIdx / g_sdLastU/V1/V2/W(float)`
  - `DbgDumpThread`：`Sleep(3000)` → 60 轮，每轮 `RetargetFontTextures()` + 2 次 `Sleep(600)` 采样，
    `CreateFileA`+`WriteFile` 直写 `chs\logs\fontdbg.txt`
  - **`DumpTexInfo`（D3D vtable[14] GetLevelDesc）已删除**：那个指针不是标准纹理对象，
    返回 `fmt=0 w=0 h=0`，且会让诊断线程直接不落盘。

### 部署现状

| 项 | 值 |
|---|---|
| `plugins\z_gta4cn.asi` | **207,872 B**（诊断+探针+font1 扩展版，**当前处于「文字全不显示」的坏状态**） |
| `chs\config.ini` | `EnableFontHook = false` ← **已关**，界面为纯英文，游戏可正常跑 |
| `update\pc\textures\fonts.wtd` | 1,590,798 B（base，已换我们的） |
| `update\TLAD\...\fonts.wtd` | 1,655,842 B |
| `update\TBoGT\...\fonts.wtd` | 1,747,718 B |
| `chs\font\glyphs.dat` | 14,392 B / 3,597 码点 / 3,584 mapped / max idx 3,596 |
| `update\common\text\americanFF.gxt` | 7,302 B（原版英文，已恢复） |
| 三章 `american.gxt` | 已移出游戏目录（`C:\Game\_disabled_hanhua_20261108\gxt\`） |
| `plugins\GTA4.CHS\` | 已整目录移出（`C:\Game\_disabled_hanhua_20261108\plugins_GTA4.CHS\`） |
| FusionFix 5.1.2 / Solitude 3 | **完全未动** |

### 回滚

1. 只退字形层：`chs\config.ini` 改 `EnableFontHook = true` 即恢复（当前已是 false）。
2. 退到「只接管 font0」的已知基线：`C:\Game\_disabled_font_p4\z_gta4cn.asi`（194,560 B）。
3. 图集/资源回滚：三章 `.bak_font_p4`（2,555,345 / 3,361,115 / 2,643,532）；
   整包备份 `C:\Game\Grand Theft Auto IV_backup_20261107`。

### 源与脚本

- 源码 `C:\Game\gta4-chs\src\`（`font.cpp` / `font.h` / `dllmain.cpp` / `build.bat`）
- 重编译：`cd "C:\Game\gta4-chs\src"; cmd /c build.bat` → `out\z_gta4cn.asi`
- 反汇编：`python -X utf8 C:\Game\_tools\p4_dis.py <VA-0x400000> <len>`（`0x921534`→`521534`，`0x9216BF`→`5216BF`）
- 搜绝对引用：`p4_disp_refs.py`（收绝对 VA）；搜调用者：`p4_callers2.py`（改 `TARGETS`，收绝对 VA）
- wtd 取证：`p4_wtd_scan.py` / `p4_wtd_scan2.py` / `p4_verify_wtd.py`
- 抓窗（**必须 PS 5.1**）：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Game\_tools\p4_grab_window.ps1`
  → `p4_work\game_baseline_noGlyph.png`（客户区 960×540，`PrintWindow(flag=2)`）

---

## 六、真机操作踩过的坑（别重复）

1. **GTA4 拒绝在虚拟桌面（pip）启动**：`GTA IV cannot be launched over remote desktop` → 必须 main 桌面。
2. **CU 的 `cu.hotkey("escape")` 会被运行时当成用户物理中断**，之后整个 CU 会话报
   `Desktop control was cancelled by Escape`，锁死。
3. **用 `WScript.Shell` 的 `SendKeys("{ESC}")` 有时打不开菜单**；可靠的替代是 Win32 `keybd_event`
   注入 VK 0x1B（`Add-Type` + `SetForegroundWindow` + down/up），实测稳定。
4. 按标题 `"GTA IV"` 做 `AppActivate` 返回 False，**必须传进程 pid**。
5. 载入画面阶段按 ESC 可能把窗口弄没；等场景真正出来（约 30 s，进度条消失）再按。
6. 前台命令超 15 s 会被转后台 → 编译+启动+抓图一律 `run_in_background: true` + `TaskOutput`。
7. 后台线程里 `LOG_I` 写不进日志，必须 `CreateFileA`/`WriteFile` 直写。
8. 单次 `Sleep(9000)` 采样会撞上「还没画字」，必须多轮轮询。
9. Ras 之外：`sigscan` 返回的 rva = `VA - 0x401000`（不是 `VA - 0x400000`），传错会整体偏 0x1000，全 0 假阴性。

---

## 七、必须清理的诊断残留（发布干净版前）

`Pr0/Pr1/Pr2`、`InstallProbe`、`g_prCw/g_prVx/g_prBq/g_prTramp/g_prResume/g_prOrig/g_vxBuf`、
`g_sdN/g_sdxN/g_sdByFont/g_sdxByFont/g_sdLastIdx/g_sdLastU/V1/V2/W`、
`g_b66c0/g_b66b8/g_b66bc/g_b45d8`、`g_dbgS/g_dbgN/g_dbgHit/g_stubN`、`DbgDumpThread`。
`RetargetFontTextures` 若改成一次性写入则不必留在循环里。

---

## 八、交给润色窗口的对接事项

1. **图集变更通告已写进 `docs\双线状态板.md` §二**（小节「与润色线的图集变更通告」）：
   重烘焙对润色线是**零影响**（`glyphs.dat` 不变、`build\zchs_*.gxt` 与 `data\zh_global.tsv` 不碰），
   但需要润色线回答**「当前译文字符集是否还会变、什么时候定稿」**，以便安排最后一次图集追加。
2. **时间窗**：重烘焙 + 重打三章 wtd 期间（预计半小时到一小时，纯离线）请润色线暂停 gxt 重打包与部署；
   字形线真机验证那几分钟同样暂停（归因问题，不是文件冲突）。
3. 字形线**现在就能验 base**（库里已有 3,408 行中文文本），不必等 gxt 定稿；只有最终整体打包才等。
4. 字形线独占文件：三章 `fonts.wtd`、`plugins\z_gta4cn.asi`、`chs\config.ini`、`chs\font\glyphs.dat`；
   润色线独占：`build\zchs_*.gxt`、`data\zh_global.tsv`。互不交叉。
5. 本窗口**没有动过任何** gxt、tsv、译文数据。

---

## 九、一句话给下一窗口的起点

先做 `0x923140` 处的「绑定贴图指针 + 顶点缓冲前 36 B」dump（一次真机就能出），
回答「那张图到底是谁、quad 有多大」，再决定是继续 A 还是直接转 C。
**不要再去改 `[esp+XX]` 的偏移，已经核实完并写进 2.6 表。**
