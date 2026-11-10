# 其他游戏汉化/HOOK 实现逻辑调研 与 本方案风险取舍

> **修订提示（2026-11-08 补）**：本文第 12 行表格与第 18 行把「本机上游简中补丁」归为纯资源替换，**该定性已被实测推翻**。实测结论见《GTA4.CHS-技术路线解构.md》§2.1、§5.1、§10.3：`GTA4.CHS.asi` 是 60 处 inline patch（57 处 `E8` ＋ 3 处 `E9`）的绘制 / 取串层补丁，与《补丁之补丁 v1.0》的资源替换互补，合起来是两段式方案。第 18 行「官方/商业汉化多为纯资源替换」对第二节 A/B/C 三例仍成立，但**不适用于这个 asi**。

调研目的：GTA IV 引擎老旧、且是主机版暴力移植到 PC，担心 hook 导致反复调试。
本文件回答三个问题：别人怎么做的、哪些坑是必踩的、我们这条路线为什么把自己限制到最低风险档。

---

## 一、结论先行

| 方案类型 | 代表案例 | 改了哪些东西 | 需要代码 hook | 调试成本 |
|---|---|---|---|---|
| 纯资源替换（换文本容器 + 换字形图集） | 官方日文版、1C 俄文版、韩语补丁、**本机上游简中补丁** | `.gxt` / `fonts.dat` / `fonts.wtd` / 字符表 | 不需要 | 低，改错只表现为文字不对 |
| 文件名重定向（让引擎去读另一个名字的文本） | 日文版、部分韩语补丁 | 把 `japanese.gxt` 改名成 `american.gxt` | 不需要 | 低 |
| 文本查询层 hook（拦"取某条文本"的调用） | Galgame 半动态汉化 | 函数入口 + 文本缓冲区 | 需要 | 中高，易出现文本同步问题 |
| 绘制层 hook（自己画字形） | FusionFix 等大型 mod | 渲染链路 | 需要 | 高，涉及 D3D/字体矩阵 |
| 数据补丁（只改一条指令里的立即数） | **本方案 P3** | 一个 4 字节 imm32 | 严格说改的是数据不是控制流 | 最低 |

**关键事实：GTA IV 所有"官方级"汉化都是纯资源替换，没有一个在文本取用链路上挂 hook。**

---

## 二、案例取证

### A. 官方日文版（Rockstar 自家）
- 新增 `japanese.gxt`、`fonts_j.dat`、`fonts_j.wtd`。
- 通过把日文文本/字体的命名对接到引擎预期的 `american.gxt` / `fonts.dat` / `fonts.wtd` 生效。
- 即：**换资源 + 换名字**，引擎代码零改动。

### B. 1C 俄文版（商业发行）
- 替换 `russian.gxt`，配套 `fonts_r.dat`。
- 引擎自带的语言分支（`langId` 1..6）本来就有俄语槽位，所以连重定向都不需要。

### C. 韩语社区补丁
- 直接替换 `update\common\text\japaneseFF.gxt`（FusionFix 层的中文/日文槽），并在游戏内语言选 `LANG J`。
- 依赖上游 mod 已有的槽位命名，仍然不写代码。

### D. 本机上游「简中补丁之补丁 v1.0」（最重要的参照）
本机取证（2026-11-08）：

```
GTA4 简中补丁之补丁（含AI翻译）v1.0\
  _ORIGINAL_fonts_pc.wtd      2,434,859
  _ORIGINAL_fonts_tlad.wtd    3,233,826
  _ORIGINAL_fonts_tbogt.wtd   2,518,694
  _ORIGINAL_char_table.dat       14,072
  _ORIGINAL_american.gxt      2,977,612
  _ORIGINAL_american_tlad.gxt   820,498
  _ORIGINAL_american_tbogt.gxt  995,302
  update\pc\textures\fonts.wtd        2,555,345
  update\TLAD\pc\textures\fonts.wtd   3,361,115
  update\TBoGT\pc\textures\fonts.wtd  2,643,532
```

对应游戏内实际文件：`fonts.wtd` 由原版 101,044 B 变成 2.55 MB（字形图集被换成含中文的图集），并额外提供 `fonts_chs.wtd`；`common\data\` 下出现 `char_table.dat`（字符表，字形索引映射）。

⇒ **上游汉化的技术本质 = 字形图集 + 字符表 + `american.gxt` 三件套的资源替换，绘制链路代码一行没动。**
这与它"翻译率接近 100%"的宣称是自洽的：文本在 gxt 里，字形在图集里，引擎按字符表查表绘制，天然支持中文。

### E. 需要 hook 的场景（我们不采用，但要知道代价）
- **Galgame 半动态汉化**（文件级替换文本缓冲区）：比纯动态替换更稳，但仍要处理——回看记录（backlog）仍是原文、返回主菜单后不生效、多线程下缓冲区被复用。
- **编码判定魔改**：老日文引擎用 SJIS 双字节判定（类似 `c ^ 0x20 + 0x5f > 0x3B` 这种非常规写法），汉化时直接 patch 判定。GTA4 用 UTF-16LE，天然绕开这类坑。
- **字体 IAT hook**（改 `CreateFontIndirectA` 的 charset/字面）：GTA4 不用 GDI 画字，此路不通。
- **inline hook 通例陷阱**：`thiscall` 等价 stdcall + `ecx`，调用约定搞错必栈不平衡（典型报错 `Run-Time Check Failure #0: ESP not properly saved`）；5 字节 `E9` 跳转要搬移被覆盖的完整指令并处理跨边界；多线程下打补丁要挂起线程。
- **FusionFix 这类大型 mod**：确实是绘制链路 hook，但它有专职维护者、按版本逐个适配，属于"高成本可持续投入"路线，不是单人一次性汉化该选的档位。

---

## 三、我们这条路线为什么风险最低

P2 定位到的 `0x008C5DF0(entity, langId)` 目标指令（完整反汇编已在 `P0-P1-落地记录.md` 留档）：

```
008C5E29  B8 48 F9 E7 00   mov eax, 0x00E7F948   ; "AMERICAN.GXT"
008C5E2E  5E               pop esi
008C5E2F  C2 04 00         ret 4
```

P3 只改写 `B8` 后面那 4 字节立即数，指向我们自己的字符串。这样做避开了 inline hook 的全部典型故障：

- **指令流不变**：仍是 `mov eax, imm32` 这一条，长度、位置、后续 `pop esi`/`ret 4` 全部原样，栈平衡不可能被破坏。
- **不需要 trampoline**：没有被覆盖的指令要搬移，不存在指令跨边界。
- **不改 ABI**：不插入 `call`，不涉及 `ecx`/`this`、不涉及返回值约定。
- **不碰 `.rdata` 原字符串**：原版 `AMERICAN.GXT` 字面量保留，随时可回退。
- **线程安全面小**：4 字节对齐写入本身原子，且发生在模块初始化早期（游戏尚未开始读文本）。

同时 P3 加了四道闸门，任一不过就拒绝挂载、游戏跑原版：

1. 特征码命中数必须恰好为 1；
2. 命中 RVA 换算后的 VA 必须等于 `0x004C5DF0`；
3. `fn+0x39` 处操作码必须是 `0xB8`，`fn+0x3A` 处 imm32 必须仍是 `0x00E7F948`；
4. `VirtualProtect` 写入 → `FlushInstructionCache` → 恢复保护 → **回读校验**。

隔离宿主实测（2026-11-08，`host.exe`）：特征码 count=0 时日志

```
[ERROR] [hook] gxt redirect FAILED, running vanilla: sig gxt_filename_by_lang count=0 (must be exactly 1), hook refused
```

即"失败就放弃"这条设计在真实代码里生效，不是口头承诺。

---

## 四、老引擎 PC 移植的坑，以及各自的规避方式

| 坑 | 后果 | 规避 |
|---|---|---|
| 调用约定错（thiscall / `ret 4`） | 崩溃、ESP 报错 | 本方案不改调用，只改数据 |
| 编码判定写死双字节 | 中文被截断/乱码 | GTA4 本身 UTF-16LE，无需改判定 |
| 渲染线程与主线程竞争 | 偶发崩溃 | 打补丁在 init 早期，且只改一次 |
| 字形图集不含汉字 | 方块/问号墙 | 资源层换 `fonts.wtd` + 字符表（官方日文版已验证可行） |
| 缓存/回看层保留原文 | "改完没反应" | 首版验收只看菜单/字幕/手机页新开局；回看类文本单列观察项 |
| 版本偏移 | 换版本后 patch 打到错位置 | 特征码 + VA + 原立即数三重校验，不过则放弃 |
| 构建环境漂移 | 编不过 | 见下节"环境固化" |

### 环境固化（本次踩到的两个真实坑）

1. `vswhere -latest` 会命中本机新装的 VS18 Community，其 `vcvars32` 不提供 x86 头文件路径 → `windows.h` 找不到。已改为**优先硬编码 `BuildTools 2022`**，仅在不存在时回退 vswhere（且去掉 `-latest`）。
2. 该 BuildTools 的 `vcvars32.bat` 只设置了 MSVC 的 `INCLUDE`，**没有拼上 Windows SDK** → `windows.h` 依旧找不到。已在 `build.bat` 里显式绑定 `Windows Kits\10\Include\10.0.26100.0\{ucrt,shared,um,winrt}` 与 `Lib\...\{um,ucrt}\x86`。
3. `build.bat` 必须是**纯 ASCII**：中文 `rem` 注释会让 `cmd.exe` 按 OEM/GBK 解析，报 `'44' is not recognized`、`'��装的'`、`The filename, directory name, or volume label syntax is incorrect.`，随后 `cd /d` 失效、`c1xx` 找不到源文件。

---

## 五、当前状态与下一步

已完成
- P2：4 条特征码全部命中数=1，`verify_sigs.py` 复验 PASS。
- P3 代码：`hook.cpp/.h` 已编入 `z_gta4cn.asi`（本次编译通过），默认 `EnableGxtRedirect=false`。
- 隔离宿主验证：拒绝路径正确。

未完成
- 三章外置 gxt 已产出：`zchs_base.gxt` 2,709,976 B / `zchs_TLAD.gxt` 796,424 B / `zchs_TBoGT.gxt` 978,944 B（均回环 PASS、逐条文本 0 不一致），**尚未部署到游戏，也未验证引擎自己的解析器能否读**。
- P4 字形层未启动。方向已定：**走资源层（复用/自建含汉字的 `fonts.wtd` + `char_table.dat`），不做绘制层 hook**。
- 真缺口 2,756 条待译。
- `GTA4.CHS.asi` 技术路线解构（后台任务）报告未产出。

## 六、上线前的验证清单（避免反复调试）

1. 只挂 gxt 重定向、**不换字体**，进游戏看中文是否变成方块——若变方块，说明字形层必须同步做（预期如此）。
2. gxt 读取失败必须在日志留 `[ERROR] gxt load failed` 并回落原版，不允许静默空白。
3. 未命中键记 `[WARN] gxt miss key=0x????`（同 key 只记一次），作为 P5 补译输入。
4. 三章（base / TLAD / TBoGT）分别验证：章节切换后是否取到各自 `zchs_*.gxt`。
5. 退出游戏不崩溃、不改动存档；删除 `plugins\z_gta4cn.asi` 与 `chs\` 即完全回退。

## 七、来源

- 日文版做法：`https://wikiwiki.jp/gta4pc/日本语化`
- 俄文版（1C）：`https://gta.com.ua/file_gta4_details.phtml?id=5`、`https://libertycity.net/files/gta-4/130883-rusifikator-dlja-gta-iv-steam.html?amp=1`
- FusionFix（大型 hook 型 mod 参考）：`https://fusionfix.io/iv`、`https://gillian-guide.github.io/essential-modding/fusionfix/`
- GXT 格式权威：`https://www.grandtheftwiki.com/GXT`
- inline hook 与 trampoline 风险：`https://blog.schnee.moe/posts/GalgameReverse6/`、`https://blog.schnee.moe/posts/GalgameReverse7/`、`https://www.unknowncheats.me/forum/c-and-c-/135538-help-hooking-functions.html`
- 汉化安装现状（需 `dinput8.dll`、需开字幕）：`https://b9348.pages.dev/安装汉化/0：安装说明/`
