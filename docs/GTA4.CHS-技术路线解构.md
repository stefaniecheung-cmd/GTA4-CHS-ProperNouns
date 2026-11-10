# GTA4 第三方汉化补丁 GTA4.CHS.asi 技术路线解构

> 本报告服务于本项目从零实现 `z_gta4cn.asi` 的决策：当前 P1 骨架已完成、尚未挂任何 hook；P3 采取只改 `0x008C5E2A` 处 4 字节立即数的最低风险路线。报告的唯一用途是判断新方案**在哪一层接管、用哪种定位手段、避开哪些坑**，不是对第三方补丁的测评或使用教程。
>
> 分析对象为只读副本 `C:\Game\_tools\chs_re\GTA4.CHS.asi`（与 `plugins\GTA4.CHS.asi` 逐字节一致），全程未运行、未部署、未挂钩；游戏目录内除本 `docs\` 报告外未写入或修改任何文件。证据标注：`【实测】`＝本机字节 / 反汇编 / 文件清单直接得到；`【推断】`＝由实测证据推导、尚未逐字节证实；`【未确定】`＝证据不足，卡在哪、缺什么证据见附录 B。

---

## 0. 结论摘要

1. **它是一个内存签名补丁（sigscan batch patch）型 ASI，未加壳、标准 MSVC x86 DLL**：Machine `0x014C`，ImageBase `0x10000000`，入口 RVA `0x1DDB8`，导入面仅 KERNEL32（42）＋msvcrt（59）；无 `VirtualAlloc`、`WriteProcessMemory`、`CreateThread`、`LoadLibrary`、任何 GDI/D3D 函数。`【实测】`
2. **目标定位完全靠运行时特征码扫描，零硬编码 exe RVA**：`.text` 内无任何指向 `0x00400000–0x01400000` 的有效绝对寻址；61 条 ASCII hex 特征（无通配位）在本机 exe 上复扫出 33 条唯一命中。补丁地址在扫描命中后于运行时回填。`【实测】`
3. **不存在运行时版本 / 大小 / 哈希比较**：版本串 `1.2.0.59`（asi 偏移 `0x269E0` / VA `0x10027DE0`）只存在于补丁记录表，`.text` 对它零代码引用；导入表无版本资源、文件大小、证书 / 哈希类 API。扫描或校验失配时静默返回（出口 `0x100087B2`），不写日志、不弹窗、不降级。`【实测】`
4. **hook 类型是 inline hook，共 60 个 asi 侧安装调用点**：`E8` call rel32 安装器 `0x7110` 对应 57 处，`E9` jmp rel32 安装器 `0x7680` 对应 3 处；每次改写 5 字节（1 操作码 ＋ 4 rel32），`VirtualProtect(0x40)` → 备份原字节 → 写 → 恢复保护；**无 trampoline、不搬移被覆盖指令**，原函数经保存的绝对指针（`0x37B20` / `0x37B24`）回跳。`【实测】`
5. **它是"两段式"汉化，不是纯资源替换**：第一段 UI / 短串在 `0xB6A0` / `0xB3C0` 用 FNV-1a 32（basis `0x811C9DC5`、prime `0x01000193`）查外置 `whm_table.dat` 串池（5,388 条），命中拷中文、未命中透传；第二段剧情长文本完全靠外部已替换成中文的 gxt，由游戏自带链路解析——asi 对 exe GXT 解析函数 `0x8C6780` 等零引用、零改写。`【实测】`
6. **它与我方选定的四个文本函数入口零重合**：61 条特征无一落在 `0x4C5CC0` / `0x4C5D70` / `0x4C5DF0` / `0x4C5E80` / `0x4C6780` ±0x40 范围内；asi 内也无 `CHINESE.GXT`、`common:/text`、`%s/%s`、`TABL/TKEY/TDAT` 或任一语言名。`【实测】`
7. **字形图集不在 asi 内，asi 自身不碰字体文件、不写盘**：中文字形来自外部三章 `fonts_chs.wtd`；`char_table.dat` 是 3,580 字升序 Unicode 名单，`whm_table.dat` 实测是中文译文串池而非字宽表；缺字兜底回退全角问号 `U+FF1F`。`【实测】`
8. **GXTStudio 只配当人工复核对照 UI**：抽取、对齐、未译识别、批量翻译、回写 gxt 走我方已有 Python 链；可白拿的是 `IVTKEY.lst` 键名映射（91,248 条，TBoGT 键名反解覆盖率 86.6%）与解析思路；二次开发前须先核实授权（仓库根目录无 LICENSE）。`【源码】【实测】`

---

## 1. 分析对象与方法

### 1.1 文件指纹

| 项 | 参照物 `GTA4.CHS.asi` | 对应游戏 `GTAIV.exe` |
|---|---|---|
| 路径 | `plugins\GTA4.CHS.asi`（只读副本在 `C:\Game\_tools\chs_re\`） | 游戏根目录 `GTAIV.exe` |
| 大小 | 232,960 字节（`0x38E00`） | 17,425,752 字节 |
| 校验 | SHA256 `9437FE10247E3A87C75CFF651A2216689E771F9E7C93CBD6A5D2726238E61588` | SHA1 `32A3F889F9FCC572EA798213F2E9EB429EB0C9A3` |
| 版本 | 面向 1.2.0.59 提取的机器码签名 | FileVersion `1.2.0.59`，ImageBase `0x00400000` |
| PE 机器 | `0x014C`（x86 / i386，32 位） | 32 位 |
| ImageBase | `0x10000000` | `0x00400000` |
| 入口点 | RVA `0x1DDB8`（VA `0x1001DDB8`） | — |
| 时间戳 | `0x6ABE34F4`（2026-10-01 10:24:52 UTC） | — |

### 1.2 PE 结构实测

| 字段 / 节 | 值 | 判定 |
|---|---|---|
| Characteristics | `0x2102`（EXECUTABLE_IMAGE / 32BIT_MACHINE / DLL） | — |
| SizeOfImage `0x3D000`；SizeOfHeaders `0x400`；Subsystem 2（WINDOWS_GUI） | — | — |
| DllCharacteristics | `0x140`（NX 兼容；`DYNAMIC_BASE` 未置位，无 ASLR 标志） | — |
| `.text` | VA `0x10001000`，VSize `0x257D8`，RawOff `0x400`，RawSize `0x25800`，熵 6.557 | 正常代码段，无压缩 |
| `.rdata` | VA `0x10027000`，VSize `0xBC7C`，RawOff `0x25C00`，RawSize `0xBE00`，熵 5.273 | 只读数据 / 特征码表 / 字符串 |
| `.data` | VA `0x10033000`，VSize `0x5148`，RawOff `0x31A00`，RawSize `0x4A00`，熵 4.882 | 可写数据 / RTTI 类型名 |
| `.rsrc` | VA `0x10039000`，VSize `0x1E0`，RawOff `0x36400`，RawSize `0x200`，熵 4.725 | 仅一份 manifest |
| `.reloc` | VA `0x1003A000`，VSize `0x2800`，RawOff `0x36600`，RawSize `0x2800`，熵 6.501 | 标准重定位表 |

**加壳 / 压缩判定：未加壳、未压缩。** 依据：标准 MSVC 五节布局；`.text` 熵 6.557 属正常 x86 代码区间（壳 / 压缩段通常 ≥7.5）；存在完整可读的 `.rdata` 字符串、RTTI 类型名（`.?AV...@std@@`、`.?AV...@nlohmann@@`）与导入表；`.reloc` 非空且结构正常；无加密节、无入口跳转到节外解包桩。`【实测】`

### 1.3 导入面与导出面

- **导入 DLL 仅两个，共 101 个函数**：KERNEL32 42 个 ＋ msvcrt 59 个。`【实测】`
- **未导入**：`VirtualAlloc`、`VirtualAllocEx`、`WriteProcessMemory`、`CreateThread`、`CreateRemoteThread`、`LoadLibraryA/W`、`MapViewOfFile`、`CreateFileA/W`、任何 GDI / Direct3D 函数。`【实测】`
- KERNEL32 42 个按类别：模块 / 进程句柄与查询（`GetModuleFileNameW`、`GetModuleHandle*`、`GetProcAddress`、`GetCurrentProcess/Id/ThreadId`、`IsDebuggerPresent`、`ExitProcess`、`TerminateProcess`）；内存保护 / 查询（`VirtualProtect`、`VirtualQuery`）；同步临界区与 SRW 件；时间本地化（`Sleep`、`QueryPerformanceCounter`、`LCIDToLocaleName`、`LCMapStringEx`、`GetLocaleInfoEx`）；指针编码 / 异常（`EncodePointer`、`DecodePointer`、`SetUnhandledExceptionFilter`、`UnhandledExceptionFilter`）；字符串消息（`MultiByteToWideChar`、`WideCharToMultiByte`、`FormatMessageA`、`LocalFree`）。`【实测】`
- msvcrt 59 个为 CRT 常规件：堆 / 内存拷贝、只读 stdio（`fopen/_wfsopen/fread/fclose/fseek/_fseeki64`）、字符串 / 宽字符、C++ 异常与 locale 支撑件。文件 IO 走 msvcrt stdio，**不直接调用 Win32 `CreateFile`**。`【实测】`
- **无导出表**：`DIRECTORY_ENTRY_EXPORT` 目录大小为 0，符号表为空。作为 ASI 插件不对外导出函数，完全由 ASI 加载器按 DllMain 约定加载。`【实测】`
- **资源段仅一份 UAC manifest**：类型 `#24`（RT_MANIFEST）、语言 `#1033`，文件偏移 `0x39060`，大小 `0x17D`；`<requestedExecutionLevel level='asInvoker' uiAccess='false' />`，不含 GXT、字体、文本块或数据表。`【实测】`

### 1.4 关键业务字符串（长度 ≥8 扫描，ASCII 733 条 / UTF-16LE 22 条中与汉化业务相关者）

| 文件偏移 | 节 / RVA | 字符串 | 代码引用（asi VA） | 语义 |
|---|---|---|---|---|
| `0x27190` | `.rdata` / `0x28590` | `GTA4.CHS` | `0x1000C682` `push 0x10028590` | 插件名 / 资源组标识 |
| `0x2719C` | `.rdata` / `0x2859C` | `char_table.dat` | `0x1000C879` `push 0x1002859C` | 外置字符表（码位名单） |
| `0x271AC` | `.rdata` / `0x285AC` | `whm_table.dat` | `0x1000C8C7` `push 0x100285AC` | 外置译文串池（名义 WHM 表） |
| `0x271BC` | `.rdata` / `0x285BC` | `custom_translations.json` | `0x1000C915` `push 0x100285BC` | 外置自定义翻译（nlohmann JSON） |
| `0x261C8` | `.rdata` / `0x275C8` | `font_chs` | `0x10006635` `push 0x100275C8` | 中文字体 / 字体资源键名 |
| `0x269E0` | `.rdata` / `0x27DE0` | `1.2.0.59 sub_91EE50` | **无直接代码引用**（仅补丁记录项被数据结构引用） | 目标版本指纹标注 |
| `0x281C0` | `.rdata` / `0x295C0` | `961c151d2e87f2686a955a9be24d316f1362bf21 3.12.0` | `0x10013AB5` | nlohmann-json ABI 哈希与版本（库自带，非游戏校验） |

负向锚点计数（整文件 0 命中）：`TABL`、`TKEY`、`TDAT`、`AMERICAN`、`CHINESE`、`.gxt/.GXT`、`common:/text`、`FONTS/FONTS_R`、`.fnt/.ttf`；asi 内不嵌入任何游戏文本或字体资源。UTF-16LE 串仅 `kernel32.dll`、`mscoree.dll`、`msvcrt.dll` 三个宽字符 DLL 名（`0x2B584 / 0x2C224 / 0x2C27C`），属 CRT/CLR 启动残留。`【实测】`

RTTI 命名空间（`.data` mangled 类型名还原）：`gta_benchmark`、`gta_font`（λ1–λ14）、`gta_game`（λ1–λ18）、`gta_html`（λ1–λ7）、`gta_mail_reply`（λ1–λ11）、`gta_menu`（λ1–λ4）、`gta_phone`（λ1–λ2）、`gta_save`（λ1–λ4）、`gta_whm`（λ1）。插件按"分类批量注册补丁"组织：每个命名空间一组 lambda，把候选 `memory_pointer` 列表交给 `batch_matching` 做批量特征匹配与落补丁。`【实测】`

### 1.5 实际走通的工具链与失败点

| 环节 | 手段 | 结果 |
|---|---|---|
| PE 解析 | pefile 2024.8.26：头字段、节表、导入 / 导出、资源、RTTI | 成 |
| 特征复扫 | capstone 5.0.7 定点扫描；`.text` 内逐字节匹配，`??` 通配规则与我方 `sigs.h` 一致（参照物特征未用通配） | 成 |
| asi 反编译 | Ghidra 12.2 headless（JDK25）全量 auto-analysis，导出 1,194 个函数伪代码 ＋ 反汇编；中间脚本 `asi_dump.txt / asi_dump2.txt / asi_dump3.txt / exe_targets.txt` | 成 |
| exe 定点反编译 | 按 `-noanalysis` 导入定点反编译；历史全量 auto-analysis 在 Decompiler 阶段 OOM（`-Xmx2G` / `-Xmx12G` 均崩），本轮不复现全量 | `0x8C5DF0`、`0x8C6780` 成功；`0x8C5CC0`、`0x8C5D70` 的 `createFunction` 抛 `OverlappingFunctionException`，改 capstone 定点反汇编 ＋ pefile 读字符串补齐 |
| REA（`npx rea-agents`） | 本轮未安装、未运行 | 未尝试；Ghidra ＋ capstone 兜底已覆盖全部目标 |
| 动态验证 | 未运行 asi、未挂钩、未读取运行时内存 | 所有"写入字节"结论来自静态反汇编的指令形态，实际落盘字节需动态验证（见附录 B） |

**对我们的含义**：静态路线（pefile 头解析 ＋ capstone 定点扫描 ＋ Ghidra 定点反编译）在不跑游戏的前提下足以定位函数、核对特征、核对导入面；凡涉及"运行时落到哪个 exe RVA""handler 栈约定是否逐字匹配""落盘字节是否正确"的结论，静态侧必须标未确定，留待动态快照补证。我方 `sigs.h` 的四条特征已经在本机 exe 上复扫命中数＝1，与这条静态路线一致。

---

## 2. 它究竟改了什么

### 2.1 改写形态总览

【实测】所有安装路径最终都改写游戏 `.text` 目标处的指令字节（`E8` call rel32 或 `E9` jmp rel32），由 `VirtualProtect` 包裹改写。未见 IAT hook、未见对游戏 vtable 指针表的批量写；RTTI 命名空间下的 `register_patches(batch_matching&)` lambda 只是签名记录注册器，不是函数指针替换。

安装点统计（capstone 全 `.text` 扫描 call 目标）：

| 安装器 | patch 前（目标处原指令） | patch 后（写入 5 字节） | asi 侧安装调用点数 | 证据 |
|---|---|---|---|---|
| `0x7110` | 原 `E8`/`E9`/`FF 15`/`FF 25` 等指令，由 `0x7450`/`0x6FD0` 解析出原始绝对目标并备份 | `E8 <rel32>`（1 操作码 ＋ 4 字节位移，位移由 `0x72D0` 按 handler 重算） | 57 处（其中批量安装器 `0x6CB0` 一次挂 20 个 call-site，handler 统一 `0xBAD0`） | `call_scan.py` 输出 |
| `0x7680` | 同上，先由 `0x6FD0` 读原指令并解析原目标 | `E9 <rel32>`（1 操作码 ＋ 4 字节位移，`0x72D0` 重定位） | 3 处（`0x79A0`、`0x79CD`、`0x7B9D`） | 同上 |

**口径裁定**：57 / 3 是 **asi 二进制内调用安装器的调用点数量**，不是静态可列的 exe 目标 RVA 表。一处安装调用对应运行时被改写的一个目标；exe 侧最终 VA 要等运行时签名扫描回填到记录 `+0x50` 槽，静态 asi 镜像里只有特征 hex 与结果槽，没有 exe 绝对地址。`【实测】`

批量安装器 `0x6CB0`（`__stdcall`，1 参）内目标 ＝ 签名记录解析出的基址对象 ＋ 小偏移，偏移清单：`0x4D3 / 0x920 / 0x95C / 0x998 / 0x9D4 / 0xA10 / 0xA4C / 0xA88 / 0xAC4 / 0xB00 / 0x13BC / 0x14BC / 0x19D7 / 0x1A21 / 0x1A74 / 0x1AB0 / 0x1AEC / 0x1B28 / 0x1B5D / 0x203B`；相对的是基址对象，静态未逐一换算成 exe RVA。`【实测】`

### 2.2 asi 侧安装点 → handler 分类映射

【实测】`hook_map.py` 全 `.text` 扫描 `call 0x7110` / `call 0x7680`，回扫前 30 条指令取 handler 立即数。按职责归类：

| 职责分类 | handler RVA | 数量 | 备注 |
|---|---|---|---|
| UTF-16→UTF-8 编码 | `0xBAD0` | 21 | `0x6CB0` 批量 20 处 ＋ `0x8850` |
| 字形绘制 / 度量辅助 | `0x6660`、`0x6620` | 4 | 绘制 2、辅助 2 |
| 宽度 / 单字宽 / 可打印判定 | `0x6210`、`0x61A0`、`0x6120`、`0x60A0`、`0x6900`、`0x6A90` | 8 | 其中 `0x6210`、`0x61A0`、`0x6A90` 为 E9 jmp |
| 回跳桩 / 标志规整 | `0x77D0`、`0x77B0`、`0x77C0` | 3 | 见 4.3 回跳通路 |
| 串比较 / 守卫 / 拷贝 / 缓冲 | `0xB7F0`、`0xBE10`、`0xBAA0`、`0xB950`、`0xB510`、`0xBBF0` | 9 | — |
| pushal 包装族（→内层取串 / 编码） | `0x8CE0`、`0x8D60`、`0x8D80/8D20/8D40/8D00/8DC0/8DE0/8DA0`、`0xC020` | 11 | 内层转发到 `0x94D0/95C0/95F0/9540/9580/9500/9660/9690/9620/C0F0` |
| 哈希查表取串 | `0xB6A0`、`0xB3C0` | 4 | 各 2 个安装点，见 5.2 |

合计 `E8` 调用点 57、`E9` 调用点 3（`0x79A0`、`0x79CD`、`0x7B9D`）。

### 2.3 改写前后字节与安装器流程

安装器 A `0x7110`（`__cdecl`，4 栈参 `(out_orig*, target, new_handler, length)`）：

1. `VirtualProtect(target, len, 0x40/*RWX*/, &old)` 改可写；
2. 读目标处现有指令并分类：`0xE8` call rel32 / `0xE9` jmp rel32 → 交 `0x7450` 解析出原始绝对目标写入 `*out_orig`；`0xFF` 且次字节 `0x15`(call [mem]) / `0x25`(jmp [mem]) → 解引用内存指针；否则 `*out_orig = 0`；
3. 改写：`*target = 0xE8`，由 `0x72D0` 写 rel32 位移 `disp = handler - (field+4)`，操作数宽 4；
4. 再次 `VirtualProtect` 恢复原页属性。

安装器 B `0x7680`（`__cdecl`，4 栈参）：先由 `0x6FD0` 读原指令并解析原目标，再写 `0xE9`，位移仍交 `0x72D0` 重定位；`VirtualProtect` 同样 RWX → 写 → 恢复。

| 环节 | asi VA | 实测要点 |
|---|---|---|
| 跳板写入 | `0x100076D9` | `mov byte ptr [esi],0xE9`（JMP rel32 首字节）；`0x10007776` `push 0x90`（NOP 填充长度 0x90） |
| 写前保护 ＋ 备份 | `0x10006C40` / `0x10006C6C` | `VirtualProtect(addr, len, 0x40, &old)`；读原始字节 `mov bl,[esi]` 备份；`test al,al` 判断保护是否成功 |
| 相对地址解析 | `0x7450` | rel8 / rel16 / rel32 → 绝对地址：`target = field_addr + disp + instr_len` |
| 重定位写入 | `0x72D0` | `VirtualProtect` 包裹，支持 rel8 / 16 / 32 |
| 原目标解析（handler 侧） | `0x8090` | `__stdcall`，1 参；解析被 hook 目标的原始绝对目标，存全局 `DAT_10037B20` |

**覆盖长度**：两种安装器写出的都是 5 字节（1 字节操作码 `E8`/`E9` ＋ 4 字节 rel32）。`length` 入参只用于 `VirtualProtect` 的页保护区域大小与指令分类，不决定拷贝长度。`【实测】`

**另一处 exe 内改写 `0x8620`**（`__stdcall`，0 参，410B）：在 exe 内存中扫描 `.text` 特征段，定位唯一匹配后把 9 字节 `0xCC` 改写为 `DAT_10027DB4` 起的字节，再把 1 字节写成 `'6'`（`0x36`）。比较对象是 `.text` 内 7 字节机器码签名（要求唯一命中）＋ 后续 `0x14` 标记与 9×`0xCC` 占位校验，**不是** PE VERSIONINFO 资源、不是模块内版本字符串、也不是文件大小 / 哈希。`【实测】` 该改写的确切语义（版本校验绕过 / 崩溃检查绕过 / 反调试绕过）未完全确认，见附录 B。

### 2.4 与我方 `sigs.h` 四条特征的对照

我方四条特征在本机 exe 复扫，命中数均 ＝ 1：

| 我方目标 | 特征（`??` 通配） | exe 命中 VA | RVA |
|---|---|---|---|
| `gxt_filename_by_lang` | `80 7C 24 04 00 56 8B F1 74 07 E8 ?? ?? ?? ?? EB 05 A1 ?? ?? ?? ?? 80 BE` | `0x008C5DF0` | `0x4C5DF0` |
| `text_dir_root` | `53 8B 1D ?? ?? ?? ?? 55 0F B7 53 04 56 33 C9 57 85 D2 7E 1B 8B 33 8D 86` | `0x008C5CC0` | `0x4C5CC0` |
| `path_join` | `53 56 57 FF 74 24 10 8B F1 E8 ?? ?? ?? ?? 8B 5C 24 14 8B D3 2B D0 8A 08` | `0x008C5D70` | `0x4C5D70` |
| `gxt_parser` | `81 EC 2C 02 00 00 A1 ?? ?? ?? ?? 33 C4 89 84 24 28 02 00 00 8B 94 24 3C` | `0x008C6780` | `0x4C6780` |

五个候选目标的 exe 原始字节（patch 前，只读回读；换算口径：`.text` RawOff `0x400`、VA `0x00401000`，故 `raw = VA - 0x00401000 + 0x400`）：

| 候选 | VA | RVA | exe 文件偏移 | patch 前原始字节（前 16 字节 hex） | patch 后（我方 P3 路线） |
|---|---|---|---|---|---|
| 语言 ID→GXT 文件名 | `0x008C5DF0` | `0x4C5DF0` | `0x4C51F0` | `80 7C 24 04 00 56 8B F1 74 07 E8 81 1F FF FF EB` | 函数头不动；仅函数内 `fn+0x3A`（`0x008C5E2A`）imm32 `0x00E7F948` 改为指向中文 gxt 名指针，4 字节 |
| 语言跳表 | `0x008C5E80` | `0x4C5E80` | `0x4C5280` | `29 5E 8C 00 32 5E 8C 00 3B 5E 8C 00 4D 5E 8C 00` | 不改 |
| GXT 解析器 | `0x008C6780` | `0x4C6780` | `0x4C5B80` | `81 EC 2C 02 00 00 A1 B4 7F 05 01 33 C4 89 84 24` | 不改 |
| 返回 `common:/text` | `0x008C5CC0` | `0x4C5CC0` | `0x4C50C0` | `53 8B 1D 28 56 BB 01 55 0F B7 53 04 56 33 C9 57` | 不改 |
| 拼路径 | `0x008C5D70` | `0x4C5D70` | `0x4C5170` | `53 56 57 FF 74 24 10 8B F1 E8 42 FF FF FF 8B 5C` | 不改 |

跳表 `0x008C5E80` 处为 7 个 32 位指针（`0x8C5E29 / 0x8C5E32 / 0x8C5E3B / 0x8C5E4D / 0x8C5E44 / 0x8C5E56 / 0x8C5E66`），其后 `CC CC CC CC` 填充，再接 `0x008C5EA0` 的字符串比较函数。语言名 / 文本目录串位于 `.rdata`：`common:/text` 首现 `0xA7ED38`，`AMERICAN` `0xA7ED48`、`FRENCH` `0xA7ED58`、`GERMAN` `0xA7ED64`、`SPANISH` `0xA7ED70`、`ITALIAN` `0xA7ED7C`、`RUSSIAN` `0xA7ED88`、`JAPANESE` `0xA7ED94`。`【实测】`

**重合判定**：把 61 条 asi 特征（含 33 条唯一命中）逐条与五个候选 RVA 做 ±0x40 邻近比对，**重合 0 处**；五个候选目标的前 16 字节与任一 asi 特征序列做前缀包含比对，**无一条完全前缀匹配**。结合 asi 内无 GXT 文件名、无 `common:/text`、无 TABL/TKEY/TDAT、无硬编码 RVA 四点，参照物不改写 GXT 文件名、文本目录、路径拼接或 GXT 解析器这一条文本加载链；其内存补丁集中在渲染 / UI / 菜单 / 手机 / 存档 / HTML / 邮件回复 / 字体 / WHM 等代码路径。`【实测】`

**对我们的含义**：我方 P3 挂载点 `gxt_filename_by_lang`（RVA `0x4C5DF0`）在参照物的补丁覆盖面之外；我们改的是"选哪个文件名"这一处数据，参照物改的是下游取串 / 宽度 / 绘制层，两者不在同一指令上。进入真机回归前仍须把参照物移出 `plugins\` 隔离验证（见第 7 节），避免两套补丁在同一批下游函数上二次改写。

---

## 3. 定位手段与版本校验

### 3.1 定位手段：签名扫描，不用硬编码 RVA

【实测】全量反汇编 `.text`（36,147 条指令）枚举立即数与绝对内存寻址：指向 exe 映像范围 `0x00400000–0x01400000` 的有效绝对地址 **0 条**。初筛 31 条落在 `0x01000193` 附近的"命中"逐条核对均为 `imul reg, reg, 0x1000193` 乘法立即数（FNV prime 常数 `0x1000193`），不是地址引用，已排除；4 字节对齐扫描出的 6,319 个误报（含 PE 头、代码字节、`.reloc` 项）无一被代码以 `mov/lea/push` 绝对寻址引用。

特征码存储形态：`.rdata` 内 61 条去重后的 ASCII hex 指令序列（空格分隔两位十六进制，最小 4 字节、最大 19 字节，中位 6 字节），每条由对应注册 lambda 用 `push <串VA>` 推入匹配器。**这 61 条中没有 `?`/`??` 通配位**（解析后 wild=0）；运行时对候选字节逐字节精确比较，立即数 / 相对跳转偏移在编译特征时已固化为具体字节。`【实测】`

扫描引擎（静态还原）：

| asi VA | 角色 | 证据（反汇编要点） |
|---|---|---|
| `0x10008620` | 目标镜像 / 节定位 | `mov ecx,0x10037A48; call 0x1000C630` 取模块基址；读 PE 头 `[edi+0x3C]`（e_lfanew）→ 节表；按步长 `0x28` 遍历节，比对节名魔数 `.tex`（`cmp dword ptr [esi],0x7865742e`、`cmp byte [esi+4],0x74`）定位目标 `.text` 节 |
| `0x10008650`–`0x100086CB` | 节内候选遍历 | 以 `0x28` 为记录步长枚举；候选前缀 7 字节与参考字节比对（`cmp [ecx],[ebx]`、`movzx eax,word [ecx+4]; cmp ax,[ebx+4]`、`movzx eax,byte [ecx+6]; cmp al,[ebx+6]`），计数命中 `edx`，记录首个匹配 `esi` |
| `0x100086DE`–`0x10008701` | 二次校验 | `cmp byte [eax],0x14` 标志位；连续 9 字节 `0xCC` 填充校验（`cmp byte [esi+eax],0xCC; inc eax; cmp eax,9; jb …`） |
| `0x10006C40` / `0x10006C6C` | 写前保护 ＋ 备份 | `VirtualProtect(addr, len, 0x40, &old)`；读原始字节备份；`test al,al` 判断保护是否成功 |
| `0x100076D9` | 跳板写入 | `mov byte ptr [esi],0xE9`，随后回填偏移并恢复原保护属性 |
| `0x10006AD0 / 0x10006C10 / 0x10006B40 …` | 匹配器 / 闭包调度 | vtable 槽位调用：`[ecx+0x0C]`、`[ecx+0x10]`、`[ecx+0x30]`、`[ecx+0x38]`、`[ecx+0x3C]`、`[ecx+0x44]`、`[ecx+0x48]`、`[ecx+0x54]` |

未发现 `rep movs` / `memcmp` 内建循环作为主扫描回路；比对以上述显式字节比较指令实现。`memcmp/memmove/memcpy` 仅来自 msvcrt 导入，服务于数据搬运。`【实测】`

特征在 GTAIV.exe `.text`（VA `0x00401000`，VSize `0xA71EFA`）上的命中统计：33 条唯一命中、8 条命中 2、3 条命中 3、2 条命中 6、各 1 条命中 7 / 8 / 9 / 20 / 34 / 145 / 175 / 201 / 247 / 285 / 558 / 1283 / 1489 / 2433 / 4445。高命中短特征（4 字节，本身不具唯一性，需配合上下文 / 多特征联合定位）：

| 命中数 | 特征（hex） |
|---|---|
| 4445 | `F3 0F 59 05` |
| 2433 | `66 0F 6E C0` |
| 1489 | `F3 0F 11 05` |
| 1283 | `F3 0F 11 44 24 20` |
| 558 | `F3 0F 11 0C 24 E8` |
| 285 | `8B CE 50 E8` |
| 247 | `6A 01 57 E8` |
| 201 | `80 7C 24 08 00` |

### 3.2 33 条唯一命中特征

【实测】33 条唯一命中的 exe VA 清单（asi 串偏移、特征 hex、asi 引用 VA 归档于本机只读副本 `C:\Game\_tools\chs_re\`；此处列命中 VA 供邻近比对）：`0x0040BA60`、`0x00412A7A`、`0x00413311`、`0x00413523`、`0x00439964`、`0x00451C20`、`0x0059F946`、`0x005AAF62`、`0x005D608D`、`0x005D6CF4`、`0x005D9B51`、`0x005E49DE`、`0x005E4CCE`、`0x005E5205`、`0x005E7B4B`、`0x006A351B`、`0x008B42B8`、`0x0091B850`、`0x0091BDE0`、`0x0091BFD0`、`0x0091C1E6`、`0x0091C650`、`0x0091C6C0`、`0x00920B6E`、`0x009222A0`、`0x0092250E`、`0x009225A0`、`0x009225C7`、`0x00922B83`、`0x00923819`、`0x00B8EDCD`、`0x00B8FE4F`、`0x00B8FE7C`。

注：`0x00B8EDCD`（RVA `0x78EDCD`）邻近 exe 语言名 / `common:/text` 字符串区（语言串位于文件偏移 `0xA7ED38` 起，VA 约 `0x00B8ED38`），但该特征落在代码段 `.text`，与文本数据区仅位置相邻；是否命中文本路径函数，静态侧不能定论。`【未确定】`

### 3.3 凭什么认 1.2.0.59：不存在运行时版本比较

【实测】**版本 / 大小 / 哈希三类校验在代码内均不存在**：

- **文件大小**：asi 内未编码 exe 期望大小 `17,425,752`（双字扫描 `0x109E558` 计数 0）；导入表无 `GetFileSize`。
- **PE 版本资源**：无 `GetFileVersionInfo` / `VerQueryValue` 导入；asi 自身 `.rsrc` 仅 manifest，未读取 exe 版本资源。
- **SHA1 / 哈希**：无 `WinVerifyTrust`、无证书校验 API；除 json ABI 哈希串外无游戏侧指纹哈希。
- **版本串**：`1.2.0.59 sub_91EE50`（`0x269E0` / VA `0x10027DE0`）是人工标注性质的记录项。`ref_scan.py` 双字扫描：该串址仅在记录区 raw `0x269C0`（记录表内指针）出现，`.text` 内无任何 `push / mov / lea` 立即数指向它；未看到与运行时获取的版本字符串做 `strcmp` 的回路。

导入表同样未导入 `GetFileVersionInfoW/A`、`VerQueryValueW/A`、`GetFileSize`、`WinVerifyTrust`、`CryptHashData` / `CertGetCertificateChain`。不存在读取 PE VERSIONINFO 资源、模块大小或计算文件哈希的调用点。`【实测】`

**修正口径**：本补丁面向 1.2.0.59 这一 exe 版本（签名按该版本机器码提取），但代码内**没有**"先校验版本、不符则拒绝运行"的分支。早期反编译材料中"版本锁 1.2.0.59"的措辞过度，已作废；以本节实测为准。

补丁记录区（`0x269C0`，可复算双字）：

| asi 偏移 | 双字值 | 初步含义（静态推断，未在运行时验证） |
|---|---|---|
| `0x269C0` | `0x10027DE0` | 指向版本标注串 `1.2.0.59 sub_91EE50` |
| `0x269C4` | `0x10027DAC` | 指向 7 字节参考前缀 |
| `0x269C8` | `0x00000007` | 计数 / 长度参数（7） |
| `0x269CC` | `0x00000006` | 计数 / 长度参数（6） |
| `0x269D0` | `0x00003614`（13,844） | 记录长度 / 偏移量（非 exe 文件大小、非段大小；**具体语义未确定**） |
| `0x269D4` | `0x0000003D`（61） | 长度 / 偏移参数（61，对应某补丁块跨度；**语义未确定**） |
| `0x269D8` | `0x00000009` | 校验长度（连续 `0xCC` 计数 ＝ 9，与扫描二次校验一致） |
| `0x269DC` | `0x10027DB4` | 指向另一参考前缀 |

参考前缀两条：`0x269AC` `66 3B CF 72 19 EB 14` 在 exe `.text` 复扫命中 1 处，VA `0x0091EE96`（RVA `0x51EE96`）；`0x269B4` `66 81 F9 FF 00 77 DA EB` 命中 0 处。`【实测】`

### 3.4 认不出来时怎么办：静默返回

【实测】扫描 / 校验任一环节失败，控制流跳转到 `0x100087B2`：

```
0x100087B2  5F                pop edi
0x100087B3  5E                pop esi
0x100087B4  5D                pop ebp
0x100087B5  5B                pop ebx
0x100087B6  83 C4 1C          add esp, 0x1C
0x100087B9  C3                ret
```

兜底行为：直接返回（静默跳过该补丁）。未发现日志写入、弹窗、异常抛出或降级改写；特征找不到 / 保护失败 / 校验不通过都沿上述出口退出对应注册函数。补丁写入后若 `VirtualProtect` 返回 0（`test eax,eax; setne al; je 0x10008763`），同样跳过回填，不报错。`【实测】`

### 3.5 对我们的含义

- **定位手段可借鉴**：签名扫描 ＋ 出现序号 ＋ 结果槽的登记 / 扫描 / 校验三段式（我方 `sigscan.cpp` / `sigs.h` 已是同一路线）；特征必须在本机 exe 上复扫命中数＝1，多命中短特征不能单独作为挂载依据。
- **兜底行为不可照搬**：参照物失败即静默跳过，无日志；我方路线在 P3 四道闸门之外，要求未命中键与加载失败写日志（见既有风险分析文档的上线验证清单），这一点保持我方设计，不向静默对齐。
- **版本指纹走我方路线**：我方 P1 已采集大小 ＋ FileVersion ＋ SHA1 指纹并写日志；参照物不靠运行时版本比较，不能作为"不需要指纹校验"的依据。

---

## 4. 注入时机与 hook 机制

### 4.1 入口与初始化链

【实测】PE 入口点 VA `0x1001DDB8`，标准 `DllMain(HINSTANCE, DWORD reason, LPVOID)`：`cmp [ebp+0xC],1; jne …; call 0x1001E692`（仅 reason=1 ＝ `DLL_PROCESS_ATTACH` 时调用 `0x1001E692`），随后 `call 0x1001DC7F`（CRT wrapper）。

| 环节 | 地址 / 证据 |
|---|---|
| CRT 调度 | 入口 RVA `0x1DDB8` → CRT 调度 `0x1DA6B`；attach 路径经 CRT DLL 包装 `0x1DABE`（SEH_prolog4），detach 路径 `0x1DBC8`；`0x1DABE` 内依次 `___scrt_initialize_crt` → `initterm_e(0x271D0, 0x271D8)` → `initterm(0x271A4, 0x271C4)` |
| 静态构造槽 | `.rdata` 指针表 `0x100271FC` 起：`0x1001EBD0 / 0x1001F030 / 0x1001F180 / 0x100208C0`…；CRT 静态初始化槽 `0x271AC→0x10001100`、`0x271B4→0x100010DC`、`0x271BC→0x10001000` |
| 用户侧包装 | `0x5F40`（`__stdcall`，`ret 0xC`）：先判 reason==1，再把 HMODULE 压栈、`ECX = 0x10037A48`（全局补丁管理器对象），调用主初始化 `0xC700` |
| 主初始化 | `0xC700`（`__thiscall`，`ECX=this`）：`GetModuleHandleW(NULL)` 取游戏 exe 模块，模块路径经 `0x2990` 解析（`GetModuleFileNameW(hModule, buf, 0x200)`，按 `\` / `/` 切分目录）；登记各子系统签名组 `0x7650 / 0x7D50 / 0x83F0 / 0x8B70 / 0x96C0 / 0x9F40 / 0xA0E0 / 0xA2A0 / 0xC110`；`0x3FD0` 扫描（遍历签名记录链表，匹配地址存 `record+0x50`）；`0x3F20` 校验 ＋ 安装 hook；`0x4230`；`0x8620` exe 内特征段改写；随后加载 `char_table.dat → this+0x38`、`whm_table.dat → this+0x44`、`custom_translations.json → 0x14D00` |
| TLS 回调 | TLS 目录 `0x2D8C0`，回调表仅一项 `0x1001D401`（CRT TLS 初始化，非业务补丁线程） |

**时机判定：补丁初始化发生在 DLL 加载的 loader lock 内（DllMain / CRT 静态构造路径），未另起工作线程。** 依据：导入表无 `CreateThread` / `CreateRemoteThread`；无 `LoadLibraryA/W`、无延迟线程初始化；业务注册由 ATTACH 回调同步调用链完成；TLS 回调仅 CRT 件。`【实测】`

`【未确定】` `0x5F40` 作为用户 DllMain 回调被 CRT 调度槽引用的确切数据槽位置：静态未追溯到固定 RVA（`.text` 内无指向 `0x5F40` 的 rel32 call，也无绝对指针落盘；全量绝对双字扫描 `0x10005F40` 零命中）。不影响"attach 内联初始化、无独立线程"的结论。

### 4.2 Hook 类型：inline hook，无 IAT hook、无 vtable 替换

【实测】所有安装路径最终改写游戏 `.text` 目标处指令字节（`E8` call rel32 或 `E9` jmp rel32），由 `VirtualProtect` 包裹改写。安装器核心 `0x7110` / `0x7680` 直接对目标指针写操作码字节；全文件未发现对游戏模块 IAT 的操作，未发现对游戏 vtable 指针表的批量写。

定位登记接口 `0x40E0`（`__thiscall`，4 参：this、hex 模式串、出现序号、结果槽 `.data`）；扫描 `0x3FD0`（`__fastcall`）遍历记录链表；校验 / 安装 `0x3F20`（`__fastcall`）。`【实测】`

### 4.3 E8 与 E9 两种改写的用途差异、回跳与栈平衡

**E8 call rel32（安装器 `0x7110`，57 处）**：目标处改写为 `E8 handler`。游戏流程到达目标时执行 `call`，**压入返回地址 `target+5`** 进栈，再跳入 handler；handler `ret` 后回到原调用点后续指令。原目标函数体默认不被进入；handler 需要调原函数时，经安装期解析保存的原始目标指针回跳。返回值按原函数约定经寄存器 / 浮点栈回填到调用方。`【实测】`

**E9 jmp rel32（安装器 `0x7680`，3 处）**：目标处改写为 `E9 handler`，**无条件跳转、不压返回地址**。handler 不能靠 `ret` 自动回到 `target+5`；要么完全接管原函数职责，要么经保存的原目标指针自行重新调用原函数后再返回。`【实测】`

**回跳通路**：全局 `DAT_10037B20` / `DAT_10037B24` 在安装期由 `0x8090` 解析写入原始目标；回跳桩 `0x77D0` 反汇编：

```
; RVA 0x77D0（capstone）
0x100077D0  pop  edi                     ; 取回跳转地址
0x100077D1  call dword[0x10037B24]      ; 调保存的原函数
0x100077D7  or   eax,0x80000000         ; 返回值置标志位
0x100077DC  jmp  edi                    ; 跳回调用点
```

`0x77B0` / `0x77C0` 是标志 / 指针规整桩（`and edi,0x7FFFFFFF` 后取字 / 写字节），不是原函数调用。`【实测】`

**无标准 detour 跳板**：导入表无 `VirtualAlloc` / `VirtualAllocEx`，也未发现被覆盖指令字节的拷贝。原始目标以绝对指针形式保存在 out_orig 结构 / 全局 `DAT_10037B20`；相对 call / jmp 的地址重定位已由 `0x7450`（rel → 绝对地址）与 `0x72D0`（按新 handler 位置重算 rel32）处理，但**未做按指令长度的反汇编指令拷贝**——被覆盖的若干字节不会被搬到跳板执行，这是该实现与标准 detour 跳板的关键差别。`【实测】`

**写保护流程**：`0x7110` / `0x7680` / `0x72D0` / `0x8090` 均为"改页保护 → 写 → 恢复原属性"；每次写出 5 字节（1 操作码 ＋ 4 rel32）。`【实测】`

### 4.4 调用约定与栈平衡归属

【实测】各核心例程约定（Ghidra 推断 ＋ 反汇编 `ret n` 核验）：

| RVA | 约定 | 参数来源 | 栈平衡归属 |
|---|---|---|---|
| `0x7110` 安装器 A | `__cdecl` | 栈 | 调用方清栈（调用后 `ADD ESP,0x10`） |
| `0x7680` 安装器 B | `__cdecl` | 栈 | 调用方清栈（`ADD ESP,0x10`） |
| `0x72D0` / `0x7450` / `0x6FD0` / `0x6C40` | `__cdecl` | 栈 | 调用方清栈 |
| `0x8090` 原目标解析 | `__stdcall`，1 参 | 栈 | 被调方 `ret 0x4` |
| `0x40E0` 签名登记 | `__thiscall` | `ECX=this` ＋ 栈 | 调用方清栈 |
| `0x3FD0` 扫描 / `0x3F20` 校验安装 | `__fastcall` | `ECX`/`EDX` ＋ 栈 | 按 `__fastcall` |
| `0xC700` 主初始化 | `__thiscall` | `ECX=this` ＋ 栈 | 调用方清栈 |
| `0x2990` 模块路径 | `__thiscall` | `ECX=this` ＋ 栈 | 调用方清栈 |
| `0xBAD0` UTF-16→UTF-8 | `__cdecl`，2 参 `(ushort* src, byte* dst)` | 栈 | 调用方清栈（`ADD ESP,8`） |
| `0x6210` 宽度计算 | `__cdecl`，3 参，返回 `float10` | 栈 | 调用方清栈 |
| `0x6660` 字形绘制 | `__cdecl`，4 参 `(float x, float y, uint char, param4)` | 栈（XMM / 浮点栈返回） | 调用方清栈 |
| `0x1FCE0` 格式解析 | `__fastcall`，1 参 | `ECX` / 栈 | 按 `__fastcall` |

handler 约定与裸函数判定：注册为补丁 lambda / 包装器的例程多为 `__stdcall` params=1（`ret 4`）；`0x77E0–0x78B0` 区间是 13 字节 `__stdcall` 桩。**未发现 naked / 裸函数或手写内联汇编 thunk**：所有被列函数都有标准 prologue（`push ebp / mov ebp,esp` 或 `sub esp,…`）与 epilogue，handler 参数按被 hook 游戏函数的原约定从栈 / `ECX` / `EDX` 取。`【实测】`

`【未确定】` 逐个 hook handler 与游戏原函数约定是否逐字匹配（尤其是 `__thiscall` 的 `ECX=this` 回填与浮点返回值）：静态只核验了 asi 侧函数自身的约定；运行时栈不平衡会以崩溃表现，需逐个反汇编被 hook 的 exe 原函数原型对照。

返回值回填：`__cdecl` 宽度函数 `0x6210` 经浮点栈 / `XMM0` 返回宽度；绘制函数 `0x6660` 计算四边形坐标后交 `0x6BD0` 画 quad，自身无显式整数返回；`0xBAD0` 返回指向输出 UTF-8 缓冲末尾的指针（`param_2` 递增后写 `0`）。`【实测】`

### 4.5 异常与崩溃保护

【实测】导入表**无** `AddVectoredExceptionHandler`（VEH）、**无** `IsBadReadPtr` / `IsBadWritePtr`；`IsDebuggerPresent` 仅用于状态判断，不是崩溃守护。

实际存在的保护机制：复杂函数内有编译器生成的 C++ SEH 帧——prolog 内 `push fs:[0]` 链（`ExceptionList`）、`__security_check_cookie` 栈 Cookie（`DAT_10033100 ^ EBP/ESP`），处理件走 `__CxxFrameHandler3` / `_except_handler4_common`；C++ 异常经 `_CxxThrowException` 抛出（如 `0xBAD0` 遇非法代理对 / 越界码点时抛异常，ThrowInfo `DAT_10030FA0` / `DAT_10030F48`）。`SetUnhandledExceptionFilter` / `UnhandledExceptionFilter` 只出现在 CRT 崩溃上报路径：`0x1E4D7`（RTC 失败 `0x40000015`）、`0x1EA50`（栈缓冲溢出 `0xC0000417`）、`0x1E2C7`。这是 CRT 自身的未处理异常上报，**不是补丁层安装的自定义顶层崩溃守护**。hook handler 周围未识别到自定义 `__try/__except` 帧；asi 侧主动做的内存访问边界判断仅在查表 / 编码函数内部（如 `0xBAD0` 的代理对与码点范围检查），没有对游戏只读指针做批量 `IsBadReadPtr` 探测。`【实测】`

### 4.6 对我们的含义

- **我方 P3 不进入这套机制**：P3 只改写 `0x008C5E2A` 处 4 字节立即数（`mov eax, imm32` 的 imm32），指令流不变、长度不变、后续 `pop esi` / `ret 4` 原样，不插 `call`、不涉及 `ECX=this`、不搬移指令、不需要 trampoline；参照物的 57/3 个 inline hook 及其约定风险与我方 P3 无关。
- **若后续 P4/P5 需要挂取串或绘制层 hook**，参照物暴露的坑必须正视：`__thiscall` 的 `ECX=this` 回填、浮点返回值、栈清理要逐项对照原函数原型；E9 jmp 型 hook 不压返回地址，不能靠 `ret` 自动回跳；无跳板意味着被覆盖指令必须落在"整条可丢弃"的位置，否则要自己搬指令。
- **异常保护按我方设计补强**：参照物仅有编译器 SEH 帧、无 VEH、无指针探测；我方 handler 若进入游戏只读指针密集的链路，应在设计上预留边界判断与日志，而不是默认照搬参照物的薄保护。

---

## 5. 文本链路接管层次

### 5.1 链路分层与参照物落点

链路按「key→string 查询 → 排版 / 换行 / 宽度 → 字形绘制」三层归类。参照物接管集中在**宽度计算**与**字形绘制**两层，外加格式 / 编码转换；译文来自外置 `char_table.dat` / `whm_table.dat` / `custom_translations.json`。`【实测】`

| 层 | RVA | 约定 | 职责 | 证据 |
|---|---|---|---|---|
| 查询 / 编码 / 格式 | `0x5CE0` | `__cdecl`，2 参 | 按 key 查表（表 / JSON）取译文；未命中返回默认串（`.rdata 0x100275B4` 起） | 先调 `0x1CB1E` 查表，空结果走默认串回填 |
| 查询 / 编码 / 格式 | `0xBAD0` | `__cdecl`，2 参 | UTF-16 → UTF-8 编码器；解码代理对，非法字符 `_CxxThrowException`；逐字交 `0x8C50` | 伪代码见反编译记录；`0x8C50` 为逐字 UTF-8 编码 |
| 查询 / 编码 / 格式 | `0x1FCE0` | `__fastcall`，1 参，1264B | printf 风格格式符解析（`%A/%E/%F/%G/%C/%S/%X/%Z…`），用 `wctomb_s` / `wcsnlen` / `strnlen` | `switch` 按格式符分派 |
| 宽度 / 排版 | `0x6210` | `__cdecl`，3 参，返回 `float10` | 遍历 UTF-16 串，逐字宽度查 `0x6120`；缩放因子取 `DAT_10037AF4`；处理 `0x7E` / `0x807E` 序列；`\n`(`0x6E`) 重置最大宽度；返回宽度 | 反汇编伪代码 |
| 宽度 / 排版 | `0x5F70` | — | 单字宽：先 `0x1D50` 判可打印，查 `whm` 宽度表（`DAT_10037AF4` 起），乘缩放 | 反汇编：`0x5FC5 mov edx,[0x10037AF4]`、`0x5FD6 imul ecx,eax,0x96`、`0x5FE8 movss xmm0,[eax+ecx*4+0x204]`、`0x5FFE divss xmm0,[0x10037B00]`、`0x6008 mulss xmm0,[edx+4]` |
| 宽度 / 排版 | `0x6AE0` / `0x6BD0` | — | 度量 / 排版辅助 | 被宽度与绘制函数调用 |
| 字形绘制 | `0x6660` | `__cdecl`，4 参 `(float x, float y, uint ch, param4)`，661B | 用自定义字体度量 `DAT_10037AF8` 算四边形坐标；字符查 `0x5850`（`char_table.dat` 表）；`0x6BD0` 画 quad；不可打印 / 越界走 `0x6B70` 兜底 | 反编译伪代码 |
| 字形绘制 | `0x6B70` / `0x6BA0` / `0x6BD0` / `0x6BF0` / `0x6C10` | — | 兜底绘制 / quad 装配 / 上屏辅助 | 被 `0x6660` 调用 |

### 5.2 第一段：asi 侧哈希查表换中文（UI / 短串）

【实测】串进入下游排版 / 绘制前，在 asi 侧按 FNV 哈希查 `whm_table.dat` 串池换中文；未命中则透传原文。相关环节：

| 环节 | RVA | 职责（证据） |
|---|---|---|
| whm 串池装载 | `0x1BBE0` | `__thiscall`，从 `0xC8F0` 调用；把 `whm_table.dat` 头表 ＋ NUL 分隔 UTF-8 串池载入全局对象 |
| char_table 装载 | `0x58D0` | 从 `0xC8A2` 调用；载入 3,580 个允许 Unicode 码位 |
| 码位二分成员判定 | `0x5850` | 被 `0x58C2`（装载期）与 `0x6717`（绘制路径）调用 |
| JSON 覆盖查表 | `0x5CE0` → `0x1CB1E` | `custom_translations.json` 取值；未命中回填默认串（`.rdata 0x100275B4`）；`0x1CB1E` 由 `0x5D14` 调用 |
| 运行期哈希查表 handler | `0xB6A0`、`0xB3C0` | 各挂 2 个安装点（见 2.2 映射表） |
| 哈希表桶链查询 | `0xA560` | 桶数组 ＋ 链表节点比对 `node+8` 键；返回命中节点或哨兵 `0x10037A2C` |
| 未命中透传拷贝 | `0xA330` | ANSI→UTF-16 逐字展宽拷贝原文（`punpcklbw`） |
| 排除表成员判定 | `0x1CCA2` → `0x1CCD5` | 查全局排除表 `0x10033058`，`strcmp` 式比对 |
| 引用计数释放 | `0x1CCB3` | 查表后 `[ecx+0x2C]--`，归零释放 |

**查表键与哈希算法（已还原）：FNV-1a 32 位。** 常量证据（`0xB6A0` / `0xB3C0` 内联）：

```
; RVA 0xB6A0（capstone，哈希主体）
0x1000B6F9  add  edi,esi                ; 串尾 = 首址 + 长度
0x1000B6FB  mov  edx,0x811C9DC5         ; FNV offset basis
0x1000B704  movzx eax,byte[esi]
0x1000B707  inc  esi
0x1000B708  xor  eax,edx
0x1000B70A  imul edx,eax,0x01000193    ; FNV prime
0x1000B710  cmp  esi,edi
0x1000B712  jne  0x1000B704
; 随后对哈希值自身 4 字节再做一轮混合（shr 8/0x10/0x18），
; 并与全局 salt 0x10037A28 组合，交 0xA560 查桶链
0x1000B749  mov  ecx,0x10037A28        ; 哈希表对象 / salt
0x1000B756  push eax                   ; 最终哈希键
0x1000B761  call 0x1000A560            ; 桶链查询
```

- **键**：英文源串的 ANSI / ASCII 字节序列（长度由 NUL 扫描得到，逐字节参与哈希）；basis `0x811C9DC5`、prime `0x01000193` 均为标准 FNV-1a 32 常量。
- **二次混合**：首轮 FNV 之后，代码再把 `edx` 四个字节经 `shr 8 / 0x10 / 0x18` 逐字节喂回同一 prime 做 finalization，并叠加全局 `0x10037A28`；这是在标准 FNV-1a 之上的附加混淆，确切 finalization 语义以反汇编为准。
- 同类 FNV 查表助手还存在于 `0xA63A`、`0xFACA`、`0x14CD0` 所在函数；`0xA7AA`、`0xFC02` 所在函数是哈希表**装载期插入**路径。

命中 / 未命中走向（`0xB6A0`，`0xB3C0` 同构）：

```c
// RVA 0xB6A0 / 0xB3C0  伪代码
void LookupTranslate(src /*[esp+0x18/0x1C]*/, dst /*[esp+0x20/0x1C]*/)
{
    if (!src || !dst) return;
    len = strlen(src);
    if (InExcludeList(0x10033058, src, len))   // 0x1CCA2
        Abort(5);                                // 0x1CE51(5)，不参与翻译
    if (DAT_10033084 == 0x7FFFFFFF) { Abort(6); DAT_10033084=0x7FFFFFFE; }

    h = FNV1a_32(src, len) + finalize + salt;   // 0x811C9DC5 / 0x01000193
    node = HashMapLookup(0x10037A28, h);       // 0xA560
    if (node != sentinel 0x10037A2C) {
        memcpy(dst, node+0xC, node+0x10 - node+0xC);  // 命中：拷译文区间
        ReleaseRef(0x10033058);                  // 0x1CCB3
    } else {
        PassthroughWiden(dst, src);              // 0xA330：未命中透传原文
        dst[0] = 0;                              // 写终止符
        ReleaseRef(0x10033058);
    }
}
```

命中：节点 `+0xC` / `+0x10` 给出译文串起止区间，经 `0x1E876`（memcpy）拷入输出缓冲；译文来自 `whm_table.dat` 串池。未命中：`0xA330` 把原文逐字节展宽拷贝进输出缓冲（保持英文原样），写 NUL 终止符。前置过滤：命中排除表 `0x10033058` 或守卫 `0x10033084` 异常时走 `0x1CE51` 编号中止路径（消息表 `0x1002C9B0` / 类别表 `0x1002C9CC`），不是静默透传。`【实测】`

### 5.3 第二段：剧情长文本走游戏自带 GXT 链路

【实测】asi 自身不读 `.gxt`、不解析 `TABL/TKEY/TDAT`、无 `common:/text` / `update\` 路径串；剧情长文本依赖附属补丁替换的三章 `american.gxt`，由游戏自带 GXT 链路加载，asi 不接管这一层。

exe 侧 GXT 链路四定点函数反编译对照（exe 布局：ImageBase `0x400000`，SizeOfImage `0x1BE6400`，`.text` VA `0x4010000` VSize `0xA71EFA`）：

| exe VA | exe RVA | 角色 | 反编译 / 反汇编结果 | 与 asi 关系 |
|---|---|---|---|---|
| `0x008C5DF0` | `0x4C5DF0` | 语言 ID → GXT 文件名 | `__thiscall sub_8c5df0(this, langFlag)`；读全局 `0x01160CC8` 或调 `0x8B7D80`，`switch` 语言 id 0..6 返回 `.rdata` 串；默认 `0xE7F9A4` | asi 0 直接引用，未调用 |
| `0x008C6780` | `0x4C6780` | GXT 解析 / 加载器 | `__thiscall sub_8c6780(...)`；调 `0x8C5D70` 拼路径、`0x40B410` 分配、`0x40E870` 读 2/4/8 字节、`0xDFD1E0` `memcmp` 比对 magic；分块交 `0x8C6190` / `0x8C6120` / `0x8C60D0`；清理 `0x40EA40` / `0x40EA80` / `0xDF8AAE` | asi 0 直接引用，未调用；asi 也未复刻这套分块解析 |
| `0x008C5CC0` | `0x4C5CC0` | 返回默认基路径 | Ghidra `createFunction` 抛 `OverlappingFunctionException`；capstone 兜底：查全局表 `0x1BB5628`，默认返回 `0xE7F938` ＝ `"common:/text"` | asi 0 直接引用 |
| `0x008C5D70` | `0x4C5D70` | 路径拼接器 | Ghidra 同样 `OverlappingFunctionException`；capstone 兜底：先调 `0x8C5CC0` 取基路径并拷贝，追加 `0xE7F9B4` 分隔符 `\`，再调 `0x8C5DF0` 取 GXT 文件名，`rep movsd/movsb` 追加；`RET 0xC`（3 栈参） | asi 0 直接引用 |

magic / 字符串核验（pefile 读 exe 原文件）：

| exe 地址 | 内容 |
|---|---|
| `0xE7FB48` | `TABL`（`54 41 42 4C`） |
| `0xE7FB50` | `TKEY`（`54 4B 45 59`） |
| `0xE7FB58` | `TDAT`（`54 44 41 54`） |
| `0xE7F938` | `common:/text`（ANSI） |
| `0xE7F9B4` | `\`（`5C 00`） |
| `0xE7F948` / `0xE7F958` / `0xE7F964` / `0xE7F97C` / `0xE7F970` / `0xE7F988` / `0xE7F994` / `0xE7F9A4` | `AMERICAN.GXT` / `FRENCH.GXT` / `GERMAN.GXT` / `ITALIAN.GXT` / `SPANISH.GXT` / `RUSSIAN.GXT` / `JAPANESE.GXT` / `AMERICAN.GXT`（默认） |

对照结论：游戏侧 GXT 链路是「`0x8C5CC0` 取基路径 `common:/text` → `0x8C5D70` 拼 `基路径\语言.GXT` → `0x8C6780` 按 `TABL/TKEY/TDAT` 解析加载 → `0x8C5DF0` 决定语言文件名」。asi 对这四个函数零直接引用，内部也没有 GXT 路径串与 magic 解析。`【实测】`

### 5.4 查询层三态结论

| 子结论 | 状态 | 依据 |
|---|---|---|
| asi 侧「取串 / 串包装」入口被 hook，在宽度 / 绘制前按哈希换中文 | **已证实** | 4 个安装点 handler `0xB6A0`（`0xA190`、`0xA220`）、`0xB3C0`（`0xA1C1`、`0xA1E8`），内部 FNV-1a 查表 ＋ 命中拷译文 / 未命中透传；`hook_map.py` 直接映射到上述 handler |
| exe 原生 GXT key 解析 / 查询函数被 hook | **已排除** | 对 `0x8C5DF0` / `0x8C6780` / `0x8C5CC0` / `0x8C5D70` 的 VA 与 RVA 打包双字扫描零命中；asi 内无 GXT magic / 路径串 |
| 被 hook 的 4 个入口对应 exe 侧哪个原生函数（原型签名、exe RVA） | **证据不足** | 目标由签名扫描运行时解析，静态 asi 不存 exe RVA；handler 与游戏原型的 `ECX=this` / 浮点返回 / 栈清理逐项未对照 |
| 命中后译文缓冲的输出编码（UTF-8 直拷 vs 二次转 UTF-16） | **证据不足** | 命中路径 `0x1E876` 为 memcpy；输出缓冲最终编码需结合下游 `0xBAD0` / `0xBBF0` 与动态快照确认 |

**中文替换发生在哪一步**：替换点在**排版 / 宽度计算 / 字形绘制之前的取串（串包装）层**——`0xB6A0` / `0xB3C0` 在源串进入宽度函数 `0x6210`、单字宽 `0x5F70`、绘制 `0x6660` 之前完成哈希查表与译文回填；下游的 `0xBAD0`（UTF-16→UTF-8）、`0xBBF0`（UTF-16→ANSI 逐字）、`0x1FCE0`（格式符解析）是编码 / 格式转换层，宽度与绘制层（`0x6210` / `0x6120` / `0x5F70` / `0x6660` / `0x6620`）负责度量与上屏。未命中的串以原文透传到这些下游层。`【实测】`

### 5.5 对我们的含义

- **我方 P3 站在第二段（GXT 链路）**：改 `0x8C5DF0` 选的文件名 imm32，让游戏自带解析器读我们的外置 gxt；这与参照物"绕开 GXT、在取串层换短串"是两条不同的接管层。我方复用游戏自带解析器，不自己实现 `TABL/TKEY/TDAT` 解析的运行时链路（解析器读写在我方 Python 侧完成，见第 8 节）。
- **第一段的 FNV 查表路线我方不需要照搬**：我方译文已在 gxt 内，由游戏 key→string 查询返回；参照物的哈希串池是它绕开 gxt 后自建的旁路。
- **证据缺口要在动态阶段补**：被 hook 的取串入口对应哪个 exe 原生函数、译文缓冲输出编码，静态侧写未确定；若我方未来要挂取串层 hook，必须先做运行时快照把这两点坐实。

---

## 6. 字体与字形

### 6.1 它读哪些文件、写不写盘

【实测】导入的文件 IO API 全为读侧：打开 `fopen` / `_wfsopen`；读 `fread` / `fgetc` / `fseek` / `_fseeki64` / `fgetpos` / `fsetpos` / `ungetc`；关闭 / 缓冲 `fclose` / `fflush` / `setvbuf`。解析后的导入表中**无** `fwrite`、`fputc`、`WriteFile`、`CreateFileW`、`CreateFileMappingW`（`fwrite` 字样仅作为导入目录 hint 残留串存在，Raw `0x2B7E0`，无对应 IAT 调用点）。

运行期打开的文件（字符串 ＋ 引用点 ＋ 数据槽）：

| 文件名字符串 | Raw 偏移 | VA | 代码引用 | 对象槽位（init `0x1000C700`） | 加载器 RVA |
|---|---|---|---|---|---|
| 目录名 `GTA4.CHS` | `0x27190` | `0x10027190` | `0x1000C682` | 基路径构造器 `0x1000C640` | — |
| `char_table.dat` | `0x2719C` | `0x1002719C` | `0x1000C879` | 结构 `+0x38` | `0x100058D0` |
| `whm_table.dat` | `0x271AC` | `0x100271AC` | `0x1000C8C7` | 结构 `+0x44` | `0x1001BBE0` |
| `custom_translations.json` | `0x271BC` | `0x100271BC` | `0x1000C915` | 结构 `+0x70` | `0x10014D00` |
| 字库字典名 `font_chs` | `0x261C8` | `0x100261C8` | `0x10006635` | — | — |

打开模式串 `"rb"`（只读二进制）位于 VA `0x100275C4`（Raw `0x261C4`）；打开辅助函数 `0x100059D0`；stdio thunk：`fclose` `0x1001EF2D`、`fopen` `0x1001EF33`、`fread` `0x1001EF39`。负向锚点整文件 0 命中：`.ttf`、`.otf`、`.gfx`、`.wtd`、`.gxt`、`FONTS`、`CreateFileMapping`、`WriteFile`。`【实测】`

**结论**：asi 本身**不读取、也不生成** `FONTS.DAT` / `FONTS_R.DAT` / `fonts_j.dat` / 任何 `.ttf` / `.otf` / `.gfx` / `.wtd` / `.gxt`；它只读 `plugins\GTA4.CHS\` 下那三份数据文件。导入表与模式串均为只读侧；运行期不向磁盘写任何文件（无写 API、无写路径字符串、无映射视图调用）。字体图集与文本字典的落地全部由外部安装包在文件层完成，asi 只在内存里接管游戏代码。`【实测】`

### 6.2 是否自带字形图集

| 排查项 | 结果（实测） |
|---|---|
| 位图 / 容器魔数 | `BM`(BMP)、`\x89PNG`、`DDS `、`RIFF`、`GFX`、`RSC` 均 0 个有效命中；`\x00\x00\x01\x00` 的 105 处命中为零填充 / 跳转立即数巧合，非 ICO 资源 |
| 近常量数据块 | 全段 4 KB 窗口扫描，0 个"零 / 255 占比 >90%"的 1bpp / 8bpp 字模阵列 |
| 段熵 | `.text` ≈ 7.49、`.rdata` ≈ 5.75、`.data` ≈ 3.43；无大段等宽重复的字形栅格区 |
| `.rsrc` | 仅一条 asInvoker 的 UAC manifest XML，无版本信息、无图片资源 |

asi 内部未内嵌位图字模 / 图集；字形来自外部部署的字库 wtd。asi 体积 232,960 字节里的大段二进制是 `.rdata` 中的代码特征模式串与 RTTI / 字符串，不是纹理。`【实测】`

### 6.3 外部字库与字体文件实况

游戏树内中文图集为三章 `fonts_chs.wtd`（本体 / TLAD / TBoGT，2023-07-02 时间戳）；原版 `fonts.wtd`（101,044 B，2012-04-06）及 `fonts_r/j.wtd`、`common\data\fonts*.dat` 均未被改动；逐文件大小 / 时间戳见附录 A.6。asi 内的 `font_chs` 字典名（`0x100261C8`）与 `fonts_chs.wtd` 命名对应；`【推断】` asi 把游戏字体引用切换到 `font_chs` 字典，字形度量走该 wtd 内原生字模数据。

### 6.4 `char_table.dat`：允许字符名单

【实测】14,324 B ＝ 4 字节头 ＋ 3,580 × u32；3,580 个 Unicode 码位升序排列（`U+2014`…`U+FF65`，CJK 统一表意 3,561 / CJK 标点 9 / 全角 9 / 通用标点 1）；原版名单 3,517，现网多出 63 个码位；明细见附录 A.5。成员判定函数 `0x10005850` 对升序数组二分，命中返回位组 `(index>>6, index&0x3F)`（位图下标 ＋ 位）。

### 6.5 `whm_table.dat`：实测为译文串池，不是字宽表（纠偏）

【实测】780,676 B；头 u32 计数 5,388；头部 43,108 字节 `{散列 u32, 索引 u32}` 头表（止于 `0xA864`）＋ 其后 737,568 B NUL 分隔串池（5,382 段，5,349 段含汉字，平均 48.7 字符，最长 666）；串样例为短信 / 网页 / 博客类中文译文。结构明细见附录 A.5。

`【推断】` 条目为 `{散列 u32, 串池索引 u32}`，散列键是英文原文的某种编码；散列算法 / 密钥本次未还原（卡在头部高熵值无法反推明文映射，见 B11）。**纠偏**：文件名字面像 "width/height metrics"，但实测串池是中文译文而非逐字宽高，对应 RTTI 命名空间 `gta_whm`；字宽数据不在此文件。旁挂 `custom_translations.json+滤镜中文翻译`（3,123 B / 89 键）与已加载的 `custom_translations.json`（3,046 B / 86 键）并存；`【实测】` asi 只引用无加号那份，加号文件是否被读取未找到引用点（B16）。

### 6.6 字宽模型：全角等宽还是实测宽度

| 证据 | 结论 |
|---|---|
| `【实测】` asi 内无独立字宽表文件，无 `.ttf/.otf`，`.rdata/.data` 中未发现逐字宽度数组（u8/u16 宽度表解剖无对应结构） | 宽度不由 asi 自带数据表提供 |
| `【实测】` 排版 / 测量路径函数 `0x10006663` 引用一组浮点与整型单元常量（见 6.8），字符先经 `0x10005850` 判定是否在 `char_table` 名单内 | 中文走补丁后的测量路径，按名单成员身份分流 |
| `【推断】` CJK 按全角固定单元排版，拉丁 / 标点沿用游戏原版字宽；逐字字形度量来自外部 `fonts_chs.wtd` 字模与游戏原排版代码，asi 在测量 hook 里做单元换算与缩放 | 依据：名单成员制 ＋ 单元常量 32/64/66，未见逐字实测宽度读取 |

`【未确定】` wtd 内每个字形的步进（advance）字段结构本次未解剖，无法逐字核对全角 / 半角；需要在能解包 wtd 的工具里复核。

### 6.7 缺字兜底

【实测】成员判定 `0x10005850` 二分未命中时，落到 `0x100058B6` 分支，**改查回退码位 `U+FF1F`（全角问号 `？`）**，而不是直接跳过或回退英文。

【实测】标点白名单函数 `0x10006940` 逐条比较以下全角 / 中文标点，命中则按双字节（UTF-16 单元）放行：

| 码位 | 字符 | 码位 | 字符 |
|---|---|---|---|
| `0x3001` | 、 | `0xFF1A` | ： |
| `0x3002` | 。 | `0xFF1B` | ； |
| `0x300F` | 』 | `0xFF1F` | ？ |
| `0xFF01` | ！ | `0xFF5E` | ～ |
| `0xFF0C` | ， | `0x2026` | … |

`【推断】` 若连回退码 `U+FF1F` 都不在名单内，二分返回未命中索引；最终是画占位符还是保留原字符，取决于游戏绘制层分支，asi 内未发现画空方框的位图路径。未在本机真机观察过缺字现象，此分支行为待运行期复核。

### 6.8 字号与行距：来源与常量

【实测】排版 / 测量函数 `0x10006663` 引用的常量区（`.rdata` VA `0x100275D0` 起）：

| VA | 原值（hex） | 浮点 / 整型值 | 用途推断 |
|---|---|---|---|
| `0x100275D4` | `0x39800000` | 0.0002441（1/4096） | 像素 ↔ 归一化坐标换算 |
| `0x100275DC` | `0x3D864ECF` | 0.06558 | 字号缩放系数 |
| `0x100275E0` | `0x3D897745` | 0.06712 | 字号缩放系数（另一档） |
| `0x100275E4` | `0x3F740081` | 0.9531 | 宽度 / 间距修正系数 |
| `0x100275E8` | `0x3F800000` | 1.0 | 中性系数 |
| `0x100275EC` | `0x41F80000` | 31.0 | 字号阈值档 |
| `0x100275F0` | `0x42000000` | 32.0 | 字号阈值档 |
| `0x100275F4` | `0x42800000` | 64.0 | 字形单元宽 |
| `0x100275F8` | `0x42840000` | 66.0 | 字形单元宽（另一档） |
| `0x100275FC` | `0xBD864ECF` | -0.06558 | 反向偏移系数 |

asi 没有 INI / 配置项控制字号或行距；运行期唯一配置输入是 `custom_translations.json`（键值译名）。字号档位与单元尺寸是硬编码常量，取自游戏原有字号体系的档位（30/31/32、64/66 与原版 UI 字号档对应）。反汇编中未见独立的行距乘数或行高重调常量；`【推断】` 行距沿用游戏原版排版，补丁只改字符测量与定位，未针对中文另设行距。`【实测】`

### 6.9 对我们的含义

- **我方 P4 方向与资源层路线一致**：字形 / 字宽问题走字体图集（`fonts.wtd` / `fonts_chs.wtd`）＋ 字符表（`char_table.dat`）资源层，不做绘制层 hook；参照物的内部测量 / 绘制 hook 是它绕开 gxt 后自建的旁路，不是我方必走的路。
- **名单制可借鉴**：`char_table.dat` 的升序码位名单 ＋ 二分成员判定，是资源层补字时需要维护的一份白名单；我方 P4 补字时同步更新这份名单，缺字回退策略（全角问号）可作为观察项而非照搬。
- **未决项留到 P4**：wtd 内 advance 字段结构、全角 / 半角逐字核对、缺字最终表现、行距是否被重调，均需 wtd 解包工具与真机观察补证（附录 B）。

---

## 7. 与 mod 生态的关系

### 7.1 加载链与加载顺序

【实测】根目录 `dinput8.dll`，5,418,336 字节，FileVersion **9.7.4.0-6b44066**（ThirteenAG Ultimate ASI Loader，非 FusionFix 自带）。UAL 按文件名字母序加载 `plugins\*.asi`；本项目 `z_gta4cn.asi` 的 `z_` 前缀保证排在最后。渲染底层：`d3d9.dll` 1,328,784 字节（5.1.2，配合 `dxvk.conf`，实测为 **DXVK**，转 Vulkan）；`vulkan.dll` 7,856,142 字节为 Vulkan 运行时。

### 7.2 `plugins\` 清单（实测，按层归类）

| 文件 | 类别 / 锚点实测 |
|---|---|
| `GTA4.CHS.asi`（232,960 B）＋ `GTA4.CHS\` 数据表目录 | 第三方汉化主补丁；锚点 `font`/`char_table`/`whm_table`，无 D3D 导入 |
| `GTAIV.EFLC.FusionFix.asi`（14,526,680 B）＋ `.cfg`（801 B，`GraphicsAPI=1`/`Windowed=1`/`Language=0`）＋ `.ini`（8,945 B） | 综合修复 / 画质框架；锚点 `Font`/`D3D`/`gxt`；ini 未见字体覆盖项 |
| `mapfix.asi`（89,600 B） | 暂停地图区名乱码修复（补丁之补丁附带）；无字体 / 文本锚点 |
| `GTAIV.XboxRainDroplets.asi`、`IVLodLights.asi`(+.dat/.ini)、`LongShadows.asi`、`VolumetricLights.asi`、`SISCO.asi`(+.ini/.log) | 特效 / 灯光 / 预算修复；除 SISCO 锚点 `d3d9`/`D3D` 外均无字体锚点 |
| `Liberty's Legacy.asi`(+资源目录)、`LibertyCityPlates.asi`(+.txt) | 内容扩展 / 车牌替换；无字体锚点 |
| `z_gta4cn.asi`（179,200 B） | **本项目成品（P1 骨架）**，见 7.5 |

根目录注入件（`.asi`/`.dll`）：`1911.dll`、`aCompleteEditionHook.asi`、`AdvancedHook.dll`、`AdvancedHookInit.asi`、`binkw32.dll`、`d3d9.dll`(DXVK)、`dinput8.dll`(UAL 9.7.4)、`DLSS-IV.asi`（锚点 `Font`/`d3d9`/`D3D`，`【推断】` 含叠加 UI 字体绘制）、`GTAIV.EFLC.ProceduralFixes.asi`、`launc.dll`、`MTLX.dll`、`orig_socialclub.dll`、`ScriptHook.dll`、`ScriptHookDotNet.asi`（锚点 `Font`/`D3D`；`scripts\` 下 13 个 `.net.dll/.cs` 由它加载）、`socialclub.dll`、`steam_api.dll`、`vulkan.dll`。

### 7.3 冲突面分类

| 层 | 插件 | 与汉化补丁的关系 |
|---|---|---|
| 游戏代码内存补丁（文本 / 字体 / 排版） | `GTA4.CHS.asi`、`mapfix.asi` | 同一层：都改写游戏 `.text` 或字符串指针。`mapfix.asi` 仅替换地图区名字符串指针，与 CHS 主补丁分工不同 |
| 综合框架（含 D3D 与少量文本 / 字体路径） | `GTAIV.EFLC.FusionFix.asi` | `【推断】` 宽框架，理论上可能触及字体 / 文本函数；实测 ini/cfg 无字体覆盖项，当前配置 `Language=0`。叠加时需重点回归菜单 / HUD 文本 |
| D3D/Vulkan 渲染层 | `d3d9.dll`(DXVK)、`vulkan.dll`、`SISCO.asi`、`GTAIV.XboxRainDroplets.asi`、`GTAIV.EFLC.ProceduralFixes.asi`、`DLSS-IV.asi`、`ScriptHook.dll` | 与 CHS 的代码补丁层**正交**：CHS 不挂设备、不接管 Present/Reset；`【推断】` 冲突点只在分辨率 / 拉伸导致的中文排版溢出，不在 hook 叠加 |
| 脚本宿主 / 叠加 UI | `ScriptHookDotNet.asi`、`AdvancedHook*`、`aCompleteEditionHook.asi` | `【推断】` .NET 脚本与叠加层若自绘 UI 文字，使用自带字体，不读 CHS 字库；互不覆盖 |
| 内容 / 特效 / 车牌 / 光影 | `Liberty's Legacy.asi`、`LibertyCityPlates.asi`、`LongShadows.asi`、`IVLodLights.asi`、`VolumetricLights.asi`、`MTLX.dll` | 无字体 / 文本锚点，实测无直接冲突面 |

已知外部风险（来自补丁包 `使用说明（必读）.txt` FAQ）：装过其它字库类 mod 会导致中文变问号；`mapfix.asi` 可能被杀软隔离。

### 7.4 「补丁之补丁 v1.0」本机实况

文件夹 `GTA4 简中补丁之补丁（含AI翻译）v1.0\` 存在于游戏目录内（未解压进根目录合并），内容实测：

| 部件 | 内容 |
|---|---|
| `安装.bat` / `卸载.bat` | 三级探测游戏目录（相对路径 → Rockstar 注册表 → Steam 库列表）；先检测 `plugins\GTA4.CHS.asi`，缺则中止；覆盖前备份到 `_ORIGINAL_*` |
| 覆盖清单（bat 实测） | `plugins\GTA4.CHS\char_table.dat`；三章 `fonts.wtd`（本体 / TLAD / TBoGT）；三章 `american.gxt`；新增 `plugins\mapfix.asi` |
| `_ORIGINAL_*` | 7 个回退基底（`_ORIGINAL_fonts_pc.wtd` 2,434,859、`_ORIGINAL_fonts_tlad.wtd` 3,233,826、`_ORIGINAL_fonts_tbogt.wtd` 2,518,694、`_ORIGINAL_char_table.dat` 14,072、`_ORIGINAL_american.gxt` 2,977,612、`_ORIGINAL_american_tlad.gxt` 820,498、`_ORIGINAL_american_tbogt.gxt` 995,302） |
| 译文资料 | `翻译对照表.md`、`未翻译内容清单.tsv`、`地图区名对照表.md`、`更新日志.txt`、`声明.txt` |
| 字符数口径 | 更新日志记 3,517→3,559；README 与现网实测 `char_table.dat` 为 **3,580**（口径差异：日志写于 v1.0 定稿前，以实测 3,580 为准） |

`【未确定】` 字库 wtd 覆盖链条与实测文件名对不上：bat 目标是 `fonts.wtd`，但真机 `pc\textures\fonts.wtd` 仍是 2012 原版 101,044 字节，中文图集名是 `fonts_chs.wtd`（2023-07-02 时间戳）；补丁包 `update\pc\textures\fonts.wtd` 为 2,555,345 字节（2026-09-20），与现网 `fonts_chs.wtd` 2,434,864 字节不一致。需要复核：安装时是否改名落到 `fonts_chs.wtd`，或该 wtd 覆盖步骤在当前部署中未执行。

### 7.5 与本项目 `z_gta4cn.asi` 共存判断

| 项 | 实测 |
|---|---|
| 部署文件 | `plugins\z_gta4cn.asi`，179,200 字节，x86（`0x014C`），EP RVA `0x8208` |
| 导入 | 仅 `VERSION.dll`、`KERNEL32.dll`；无 msvcrt、无 d3d、无字体 / 文本相关库 |
| 字符串锚点 | 无 `font`/`gxt`/`wtd`/`d3d` 命中；自有日志串 `no hook installed (stage=P1, sig hits=0)`、`config not found: %ls (using defaults)`、`version=%ls size=%llu sha1=%ls exe=%ls` |
| 当前行为 | P1 骨架：指纹采集 ＋ 日志，**未安装任何 hook**；字母序最后加载 |

**共存结论**：当前阶段双方无 hook 叠加、无同一函数改写，共存只是多占一份内存与一条日志，不存在行为冲突。`【推断】` 进入 P2/P3 后，若 `z_gta4cn.asi` 挂文本查询 / 排版 / 绘制 hook，且与 `GTA4.CHS.asi` 同时启用：两者定位的是同一批游戏函数，后加载者（`z_` 最后）写入的代码字节会盖掉 CHS 先前的内存补丁，导致 CHS 特征基线失配或补丁被部分覆盖；两套译文与字库（`fonts_chs.wtd`、`whm_table.dat`、gxt）也只会有一套生效。目标路线是**取代而非叠加**：真机回归前应先把 `GTA4.CHS.asi` 及其数据表移出 `plugins\`，隔离验证新补丁。

### 7.6 对我们的含义

- **加载顺序有利**：`z_` 前缀最后加载，若未来真要与其它 asi 同层改代码，后写者覆盖先写者；但这不是叠加兼容的保证，回归时仍按隔离路线做。
- **同层插件清单要记牢**：`mapfix.asi` 与 CHS 同属文本 / 字符串指针层；FusionFix 宽框架需重点回归菜单 / HUD；渲染层（DXVK、SISCO、雨滴、DLSS 等）与我方代码补丁正交，预期不在同一指令上冲突。
- **FusionFix 硬依赖未证实**：二进制内未出现 `FusionFix` / `fusionfix` 字符串，导入表也无其相关导出；是否经 `GetProcAddress` 运行时探测其它 ASI/Fix 插件，静态证据不足（`GetProcAddress` 已导入，但未见指向外部插件名的字符串），标未确定。

---

## 8. GXTStudio 能不能用

> 评估对象：本地源码 `C:\Game\_tools\gxtstudio_src\GXTStudio-main`（C++ / Qt6，作者 Lzh10_慕黑，自称 III.VC.SAGXTExtracter 替代品）。评估方式：只读源码 ＋ 只读二进制探针，未编译、未安装、未联网下载新版；未改动 `gxt_out\` 与游戏目录任何文件。证据标注：`【源码】`＝直接读源码得到的确定事实（附文件 / 类 / 函数）；`【实测】`＝本机二进制或数据文件实测；`【推断】`＝基于代码结构 / 经验的判断，尚未上机验证。
>
> 我们的盘子（实测基线）：base 59,634 键（英文 59,661，缺 27）、TLAD 18,557、TBoGT 23,910；中文侧 **26,713 条与英文逐字节相同**（约 45% 实际未译）；`summary.json` 的 `ascii_only` 为 base 26,983 / TLAD 8,649 / TBoGT 11,119。

### 8.1 三个原话问题的拍板结论

#### 问题一：用它打开并保存我们那三份 `chinese.gxt`，结构会不会被改坏？

**结论：有条件下能。** 读路径与我方实测结构吻合；写路径两遍重算偏移、保留原 CRC，但尚未上机做保存后逐块比对，存在若干低概率边界项。

读路径核对（我方事实基线：魔数 `0x00100004`，LE version=4 / bits=16 → `TABL`+u32 size，12 字节 / 项：8 字节表名 ＋ u32 偏移，524 张表 → 每张表 [可选 8 字节内联表名] ＋ `TKEY`+u32 size，u32 offset ＋ u32 crc，8 字节 / 项 → `TDAT`+u32 size，UTF-16LE，offset 为字节偏移，文本以 `0x0000` 结尾；键是 CRC 哈希而非名字）：

| 结构点 | 源码实现 | 与基线是否吻合 |
|---|---|---|
| 文件头识别 | `GXTParser::parse()`，`GXTParser.cpp:596-617`：读前 4 字节解 `version`/`bits`，`version==4 && bits==16` 判为 `GTA_IV`，随后 `fseek(4)` 跳过头部 | `【源码】` 吻合；对应魔数 `0x00100004` |
| TABL 条目 | `GXTParser.cpp:925-935`：`struct TblEntry { char name[8]; uint32_t offset; }`，12 字节 / 项 | `【源码】` 吻合 |
| 可选内联表名 | `GXTParser.cpp:949-959`：先 peek 8 字节，若不是 `TKEY` 就跳过 8 字节（`hasTableName=true`） | `【源码】` 吻合"可选 8 字节内联表名" |
| TKEY 条目（SA/IV） | `GXTParser.cpp:1044-1052`：逐项读 `offset`(u32) ＋ `crc`(u32)，8 字节 / 项 | `【源码】` 吻合 |
| TDAT 编码 | `GXTParser.cpp:1068-1106`：`bitsPerChar==16` 走 UTF-16LE，`offset/2` 转 u16 索引，二分找下一个 `0x0000` 终止；IV 分支**强制** `WideCharToMultiByte(CP_UTF8)`，不再回退猜测编码（`:1096` 注释） | `【源码】` 吻合；中文 UTF-16LE 解码路径明确 |
| 键的存储 | `GXTParser.cpp:1105`：`tabl.entries.push_back({u32_to_hex(crcs[i]), val})`，键存为十六进制 CRC 串 | `【源码】` 吻合"键是哈希不是名字" |
| 表 / 条目规模 | 解析全程 `std::vector` 动态 `reserve`，未见表数或条目数硬上限；唯一计数上限在辅助 DAT 解析 `parseDAT`（`GXTParser.cpp:1929`，count>2,000,000 拒识），与 GXT 无关 | `【源码】` 524 表 / 59,634 键不存在截断上限 |

写路径核对（`GXTEditor::saveAsGTA_IV()`，`GXTEditor.cpp:1640-1797`）：

| 结构点 | 源码实现 | 评估 |
|---|---|---|
| 两遍计算偏移 | 第一遍 `:1679-1706` 算每张表偏移 / TKEY 大小 / TDAT 大小；第二遍 `:1726-1773` 写数据，最后 `:1776-1784` 回填 TABL 表名与偏移 | `【源码】` 偏移是重算的，不是照搬旧文件；结构可重建 |
| 文件头 | `:1709-1712` 写 `version=4`、`bits=16` | `【源码】` 吻合 IV 头 |
| 内联表名 | `:1687-1690`、`:1731-1736`：**非 MAIN 表**写 8 字节补零表名；MAIN 不写 | `【源码】` 与实测一致；但这是"MAIN 无内联、其余都有"的固定假设，若原文件某张非 MAIN 表本就无内联名，保存时会被补上——`【推断】` 属低概率边界，需回归确认 |
| TKEY 哈希回填 | `:1746-1754`：键能按十六进制解析（`std::stoul(...,16)`）就**保留原哈希**；解析不成才查 `IVTKEY` 映射，再不行用 `calculateGTA4Hash` 兜底 | `【源码】` 现有条目往返保留原 CRC；新增 / 改名条目才依赖哈希映射 |
| TDAT 编码与终止符 | `:1768-1771`：`utf8_to_utf16le` 转码后写数据，再补 `\0\0`（UTF-16 null） | `【源码】` 吻合 UTF-16LE ＋ 双字节终止 |
| 偏移口径 | `:1756`、`:1760`：`currentDataOffset` 按字节累加（UTF-16 字节数 ＋ 2），相对 TDAT 数据区起始 | `【源码】` 与"offset 是字节偏移"一致 |

本机二进制实测（探针 `gxt_probe.py`，只读）：

| 文件 | 大小 | 表数 | 条目数 | 带内联名的表 | 头 version/bits |
|---|---|---|---|---|---|
| `common\text\chinese.gxt`（base） | 2,977,612 B | 524 | 59,634 | 523（仅 MAIN 无） | 4 / 16 |
| `TLAD\common\text\chinese.gxt` | 820,498 B | 142 | 18,557 | 141 | 4 / 16 |
| `TBoGT\common\text\chinese.gxt` | 995,302 B | 163 | 23,910 | 162 | 4 / 16 |
| `update\common\text\chineseFF.gxt`（覆盖层） | 4,324 B | 1（MAIN） | 84 | 0 | 4 / 16 |

三张主文件的头、TABL、内联名分布、TKEY 8 字节项、UTF-16 终止与源码读路径假设一一对应；探针解出的条目数与 `summary.json` 一致。`【实测】`

**未决项（不能写"已证实安全"）**：
1. 保存后是否与原文件逐块一致，未上机回归；需在副本上跑通"GXT → 保存 → 重新解析 → 逐块比对"闭环。
2. 非 MAIN 表内联名的固定假设可能给原本无内联名的表补写 8 字节；需核对我方三份 gxt 每张表的内联名分布。
3. `calculateGTA4Hash`（`GXTEditor.cpp:927-951`，自定义乘性哈希：A-Z 转小写、`\`→`/`、乘子 1025）不是标准 CRC32；对现有条目往返无影响（保留原 CRC），但对新增具名键，兜底哈希是否与游戏实际校验一致，本地未验证。`【推断】` IV 新增键应优先走 `keylist\IVTKEY.lst` 映射，不要依赖兜底哈希。
4. `0x` 前缀十六进制键在 IV 导入时是否被 8 字符长度校验拦截（`validateImportKeyName()`，`GXTStudio.cpp:2157-2174`；IV `maxKeyLength=8`，`:3246`）：导出时十六进制键加 `0x` 前缀（`GXTEditor.cpp:841-852`），`0x`＋8 位 ＝ 10 字符且 `x` 虽合法但超长；是否在别处先剥前缀，本地未逐行确认，需一次真实导入回归。

#### 问题二：26,713 条未译条目能不能靠它的 AI 翻译 ＋ 导出分表跑批量，跑完再导回去？

**结论：不能。** 它不具备我方批量流水线所需的任何一项条件。

| 维度 | 源码事实 |
|---|---|
| 翻译作用范围 | `【源码】` 翻译入口 `translateSelectedRows` 作用于**当前勾选 / 选定行**（`GXTStudio.cpp:7085-7146, 9311-9371`）；未见"自动跳过空值 / 跳过已译 / 跳过与英文相同"的开关。要只翻未译，需先用搜索 / 过滤手动圈出范围 |
| 术语表 / 一致性 | `【源码】` 无独立术语表 / 词典文件；术语一致性只能写进系统提示词文本（`TranslateConfigDialog.cpp:27,86`） |
| 服务商 / 端点 | `【源码】` `SmartTranslator.cpp:104-109`：写死 `deepseek`（`https://api.deepseek.com/chat/completions`）与 `xiaomi`（`https://api.xiaomimimo.com/v1/chat/completions`）；免费通道走 Google 非官方端点 / MyMemory（`GoogleFreeTranslator.cpp:201,240,387`）；对话框未暴露自定义端点 URL |
| 可配置项 | `【源码】` API Key、模型、系统提示词、批次提示词（`{contents}` 占位）、批次大小 / 并发 / 重试（`SmartTranslator.h:84-96`、`TranslateConfigDialog.cpp:371-405`）；模型清单基本固定 |
| 格式保护 | `【源码】` `NLLBTextProtector`（`NLLBTextProtector.h:19-29`）翻译前把 `~r~`/`~k~`/`%d` 等替换成 `[Tn]` 占位、译后还原，保护颜色 / 按键 / 占位符 |
| 在线依赖 | `【源码】` 云端 API 与免费端点都需联网；更新检查也走在线接口（`AboutDialog.cpp:690,802`）。无离线翻译模型 |
| 交换格式 | `【源码】` 原生导出只有文本：GXT-compiler 格式（`GXTEditor::saveAsGXTCompilerFormat()`，`GXTEditor.cpp:803-861`，`[KEY]` / `[KEY:TABLE]` ＋ 文本）、普通文本（`saveAsText()`，`[TABLE]` ＋ `KEY=VALUE`）、自定义模板导出（`GXTStudio.cpp:5163-5213`，占位符仅 `%key%` `%value%` `%table%` `%tabl%`，产物仍是按行渲染的 **TXT**）；导入只认 TXT（`importTxtFile()` `:2312`、合并 `importAndMergeTxtFiles()` `:3431`、自定义规则 `importCustomFormatFile()` `:3152`）。全仓检索：`CSV` / `TSV` / `JSONL` 无任何解析或导出实现；`JSON` 仅出现在 `DebugConfigDialog.h:87,112` 的调试配置文件过滤器里 |
| 命令行 | `【源码】` `main.cpp:134` `runCliMode()` 提供无 UI 命令：`--gxt2txt`（`:172`）、`--txt2gxt`（`:246`）、`--gendat` / `--gendattxt` / `--dattxt2dat` / `--dat2dattxt`（`:411,500,573,683`）、`--info`（`:758`）；CLI 每条命令处理**单个文件**；批量导出 / 批量并行解析只在 GUI（`GXTStudio.cpp:1595` `batchExport`、`:2127`） |

我方 `gxt_out\` 资产：`text_american.jsonl` / `text_chinese.jsonl`（当前落盘为 TBoGT 单份，23,911 / 23,910 行，163 张表，schema `{"t": 表名, "crc": 8位大写十六进制, "s": 文本}`）；`gap_base.tsv` / `gap_TBoGT.tsv` / `gap_TLAD.tsv`（表头 `table / crc / english`）。这些 **不能被 GXTStudio 直接吃**；要走它，必须先写一层转换器把 JSONL/TSV 排成它的 compiler TXT，润色后再从 TXT 导回 GXT，中间格式转换、键值对齐、未译标记仍得自己写。`【源码】【实测】`

#### 问题三：中文字形不够时，它的 DAT 字库编辑能不能顶上？

**结论：不能。** 它的 DAT 编辑只维护码点 ↔ 图集行列映射，不碰字模与字宽；字形仍须走 `fonts.wtd` ＋ `char_table.dat` 资源层，正好与我方 P4 方向一致。

工具里有两类"DAT"，别混淆：

| 类别 | 源码 | 内容 |
|---|---|---|
| 辅助文本 DAT（hash/offset/text） | `GXTParser::parseDAT()`，`GXTParser.cpp:1908`；`DATEntry{hash,offset,text}`（`GXTParser.h:191-195`） | 结构类似 GXT 的键值文本表，**不是字库** |
| 字符映射表 DAT（码点 ↔ 图集行列） | `CharTableParser`，`CharTableParser.h:15-25` / `CharTableParser.cpp` | 编辑器真正能改的"字库" |

字符映射表到底能改什么：

- `【源码】` VC 版：`loadGtaVc()`（`CharTableParser.cpp:13-52`）读 `0x10000×2` 字节映射，每项 `(row,col)`；`saveGtaVc()`（`:120-166`）反向写回 65536 项表，未用位置填 `(63,63)`。
- `【源码】` IV 版：`loadGtaIv()`（`:54-118`）按 UTF-32LE 码点序列读字符列表，64 列网格排布；`saveGtaIv()`（`:168-206`）收集有效码点重新写出。
- `【源码】` `CharTableData.cells`（`CharTableParser.h:11`）是 `QVector<uint16_t>` 码点网格；**结构里没有字模位图、没有字宽 / 间距 / kerning 字段**。
- `【源码】` 图集纹理走 `TXDExporter`（`TXDExporter.h:109-122`），接口只有 `exportTxd` / `exportTxdWithImages` / 异步导出，**没有导入或改像素的接口**。

即：DAT 编辑只能增删"某个 Unicode 码点是否出现在字体图集的第几行第几列"，维护码点清单与映射；**不能编辑字模像素、不能新增图集里不存在的字形、不能改字宽**。README 所称"编辑 DAT 字库"（`README.md:55`，屏蔽 ASCII 与重复字符）指的也是这层码点录入，不是改字模。`【源码】`

### 8.2 覆盖层与多文件往返

【源码】每个 `FileTab` 持有单一 `filePath` 与一份 `tables` / `noTablEntries`（`SaveWorker.h:33-49`）；代码中没有 `update\` 目录扫描、没有 base/overlay 双层结构、没有同键优先级合并模型。唯一的"合并"是 GUI 内把多个 TXT 文本合并进当前标签页：`GXTStudio::importAndMergeTxtFiles()`（`GXTStudio.cpp:3431`），冲突时弹 `ConflictDialog` 逐条选择"替换 / 跳过"（`:4149-4179`）。这是文本级人工合并，不是 GXT 覆盖层语义。

【实测】覆盖层 `update\common\text\chineseFF.gxt` 仅 1 张 MAIN 表、84 条；同目录还有 `americanFF/CV/RR/1.gxt` 等小文件。游戏运行时由加载顺序决定同键取值，这套关系 GXTStudio 不记录。把 `chineseFF.gxt` 单独打开、单独保存，它仍是一个独立小 GXT；**不会**自动与 base 对齐，也不会标注某键来自覆盖层。若我方要维护"base ＋ 覆盖层"双层文本，必须在自己的脚本里建模。

### 8.3 大文件与性能

- `【源码】` `GXTEditor::loadFromFile()`（`GXTEditor.cpp:37-62`）调用 `parser.parse(path)` 后，把所有表 / 条目**整份复制**进内存 `tables` 向量；`parseWithMemoryMap()`（`GXTParser.cpp:1204`）虽存在，但加载入口未走内存映射。
- `【源码】` UI 模型 `GXTTableModel`（`GXTTableModel.h:103` 起）继承 `QAbstractTableModel`，显示层有 `RowCache` 与 `buildPartialDisplayCache(firstRow,lastRow)`（`:193`）只构建可见区域缓存；但底层数据仍是全量驻留，**不是磁盘分页 / 懒加载**。
- `【源码】` 解析与保存各有后台线程：`ParseWorker`、`SaveWorker`（`SaveWorker.h:52`），带进度回调。
- `【实测】` base 2.98 MB / 59,634 键；按 Qt `QString` 估算全量驻留约几十 MB 量级。`【推断】` 这个量级在现代 PC 上不会卡死，60k 行的表格模型也在其设计范围内（`SmartTranslator.h:79` 任务上限 50,000、`QList` 上限 100,000 也侧面说明按万级条目设计）；但**没有**针对 59k 键的实测数据，首开 / 全量替换时的卡顿程度需上机确认。未发现按条目数截断的逻辑；风险不在"截断"，而在全量驻留下大表编辑时的 UI 响应。

### 8.4 键名反解覆盖率与可白拿的资产

【实测】`keylist\IVTKEY.lst` 共 **91,248 条**"名字 ↔ 哈希"映射；对落盘的 TBoGT 中文 23,910 键，可反解为可读名的 20,712 条，**覆盖率 86.6%**；其余约 13.4% 在界面上只能显示 `0xCRC`。`【推断】` base / TLAD 的覆盖率需用对应 JSONL 另算；未命中的键不影响保存（保留原 CRC），只影响人工校对时的可读性。

可借鉴的源码资产：IV 解析 / 保存结构清晰（`GXTParser.cpp` 读、`GXTEditor.cpp::saveAsGTA_IV` 写、`utf8_to_utf16le_vector` `GXTEditor.cpp:76-95`、CRC32 / 哈希表实现）；`IVTKEY.lst` 可直接被我方脚本读取，用于把 CRC 反解成可读键名。

### 8.5 授权与二次开发前提

- `【实测】` 源码根目录**没有** `LICENSE` / `COPYING` 文件；仅随附的第三方子模块带许可：`qwindowkit-main\LICENSE`、`syscmdline\LICENSE`。`README.md:99` 仅写"本软件免费开源"，**未标注 SPDX 协议**（MIT / GPL / Apache 等）。
- `【推断】` 在未取得明确授权前，默认"保留所有权利"：把它的二进制或源码打包进我方发布包、二次改造后再分发，都存在授权风险。若要复用其解析代码，需先到其 GitHub 仓库（`AboutDialog.cpp:340` 指向 `Lzh102938/GXTStudio`）核实 LICENSE 条款，或直接联系作者确认。第三方子模块 `qwindowkit` 另有自己的许可，复用核心时需一并遵守。
- `【源码】` 构建依赖：CMake Qt6 Core / Gui / Widgets / Concurrent / Network；C++17；MSVC 2022 x64；`qwindowkit` 以子目录编入；WebP 为 `REQUIRED`，zlib 可选。构建路径写死本机：Qt 在 `D:/Qt/6.11.1/msvc2022_64`、vcpkg 在 `D:/vcpkg/installed/x64-windows`，可用 `CMAKE_PREFIX_PATH` / `VCPKG_INSTALL_DIR` 覆盖。`app.manifest` 声明 `amd64`，supportedOS 含 Win7 / 8 / 8.1 / 10 / 11；`【推断】` manifest 声明 Win7，但 Qt6 运行时实际官方支持区间偏 Win10+。

### 8.6 拍板建议

**GXTStudio 只当人工复核对照 UI。** 抽取、对齐、未译识别、批量翻译、回写 gxt 走我方已有的 Python 链；可白拿的是 `IVTKEY.lst` 键名映射（91,248 条，TBoGT 覆盖率 86.6%）与解析思路；二次开发前先核实授权（其仓库根目录无 LICENSE）。

| 我方环节 | 能否接 GXTStudio | 说明 |
|---|---|---|
| 已抽取的 JSONL / gap TSV 对齐结果 | **不能直接接** | 无 JSONL/TSV 通道；需自写转换器排成 compiler TXT 才能进它的界面 |
| 45% 未译条目的批量补译 | **不建议用它跑主干** | 无"只翻未译"开关、无术语表、端点写死且依赖联网；批量一致性与可复现性不如我方脚本 ＋ 可控翻译接口 |
| 人工逐条润色、看上下文、改个别长文本 | **可作为辅助 UI** | 表格 / 正则搜索 / 撤销重做 / 颜色标记预览（`TextRenderWidget`）可用；前提是先编译出可执行文件并跑通 TXT 往返闭环 |
| 三份主文件 ＋ 覆盖层的整体回写 | **不能由它独立承担** | 无覆盖层建模、无批量 CLI、格式往返需转换层；回写 GXT 仍以我方脚本为准 |
| 字形 / 缺字补齐 | **不能** | 只维护码点映射，不碰字模与字宽 |

若试用，先在副本上跑通"GXT → TXT → 改 → 导回 GXT"闭环，重点核对 `0x` 前缀键是否被导入校验拦截、保存后表偏移与内联名是否一致；不把它作为发布包内的依赖组件，授权与可编译性未核实前，不向最终汉化包捆绑其产物。

---

## 9. 照搬会踩的坑

逐条：现象 → 原因 → 我方对策。

| # | 现象 | 原因 | 我方对策 |
|---|---|---|---|
| 9.1 | 特征找不到 / 保护失败 / 校验不通过时，补丁沿出口 `0x100087B2` `ret` 静默跳过，不写日志、不弹窗、不降级；分不清是未译还是 hook 没挂上 | 参照物失败路径设计为静默返回；导入表无日志 / 弹窗串，`SetUnhandledExceptionFilter` 只服务 CRT 崩溃上报 | P3 四道闸门（命中数恰为 1 → 命中 RVA 等于 `0x004C5DF0` → `fn+0x39` 为 `0xB8` 且 `fn+0x3A` imm32 仍为 `0x00E7F948` → `VirtualProtect` ＋ `FlushInstructionCache` ＋ 恢复保护 ＋ 回读校验）任一不过即拒绝挂载并写 `[ERROR]`；未命中键记 `[WARN] gxt miss key=0x????`（同 key 只记一次） |
| 9.2 | `ECX=this` 回填错、浮点返回值未回填、清栈归属搞错，崩溃或 `ESP not properly saved` 一类栈报错 | 参照物混用 `__cdecl/__stdcall/__thiscall/__fastcall`；静态只核验 asi 侧自身约定，handler 与原函数原型逐字匹配属未确定项 | P3 不插 `call`、不改 ABI、不碰 `ECX=this`、不搬指令；未来挂取串 / 绘制层 hook 前，逐个反汇编原函数原型，约定（`ECX`/`EDX`/栈参、返回值位置、清栈归属）逐项对照 |
| 9.3 | 改成 `E9 handler` 后 handler 末尾 `ret` 跳到错误地址崩溃 | `E9` jmp rel32 不压返回地址，不能靠 `ret` 回 `target+5`；参照物 3 处 E9 要么完全接管，要么经保存指针（`0x37B20`/`0x37B24`）＋ 桩 `0x77D0` 自行调用原函数 | P3 不挂 jmp hook；未来 E9 跳板必须显式保存原函数指针，桩内自行调用 ＋ 显式回跳 |
| 9.4 | 5 字节改写覆盖跨边界多字节指令，原指令后半段被破坏 | 参照物无 `VirtualAlloc`、不拷贝被覆盖指令，只做相对地址重定位（`0x7450`/`0x72D0`），不做指令反汇编搬迁 | P3 只改 `mov eax, imm32` 的 4 字节立即数，指令长度 / 位置 / 后续 `pop esi`/`ret 4` 原样；未来 inline hook 选点须确认被覆盖字节落在整条可丢弃指令上，否则自实现搬迁跳板 |
| 9.5 | 4 字节短特征在 `.text` 命中数百上千处，单独使用挂错地址 | 61 条特征中 33 条唯一命中，其余为多命中短特征（最高 4,445 处），需上下文 / 多特征联合定位 | 我方 `sigs.h` 四条特征本机复扫命中均＝1；扫描器强制 `hit==1`，0 或 >1 即 `[ERROR]` 不挂 hook；挂前把命中处前后 16 字节反汇编写日志人工确认 |
| 9.6 | 换 exe 版本后特征失配 / 偏移变化，补丁打到错位置 | 签名按 1.2.0.59 机器码提取，但代码内无运行时版本 / 大小 / 哈希比较，失配即静默跳过 | P1 指纹（大小 17,425,752 ＋ FileVersion 1.2.0.59 ＋ SHA1 `32A3F889F9FCC572EA798213F2E9EB429EB0C9A3`）写日志；指纹不符先查环境；特征 ＋ RVA ＋ 原立即数三重校验，不过则放弃 |
| 9.7 | 两套 asi 同时启用，后加载者覆盖先写者补丁，CHS 基线失配或被部分覆盖；两套译文 / 字库只一套生效 | 两者定位同一批游戏函数；UAL 字母序加载，`z_` 最后 | 路线定取代而非叠加；真机回归前先移出 `GTA4.CHS.asi` 及其数据表；删除我方 asi 与 `chs\` 即完全回退 |
| 9.8 | gxt 有中文却渲染成方块 / 全角问号 | 字形在 wtd 图集，引擎按字符表查表；图集缺码位时参照物回退 `U+FF1F`；我方 P4 尚未做 | P4 走资源层（复用 / 自建含汉字 `fonts.wtd` ＋ `char_table.dat`），不做绘制层 hook；首验只挂 gxt 重定向、不换字体，看是否变方块 |
| 9.9 | 菜单 / 字幕 / 手机页新开局正常，回看记录、返回主菜单后仍是原文 | 老引擎文本可能被缓存；参照物未覆盖所有取串入口（查询层是否间接接管存未确定项） | 首版验收只看新开局；回看类文本单列观察项；章节切换后分别验证 base / TLAD / TBoGT 取到各自 `zchs_*.gxt` |
| 9.10 | `~r~`/`~k~`/`%d`/按键占位符被翻译翻坏，颜色 / 按键 / 变量替换失效 | 批量翻译不做占位符保护时，格式符被当普通文字处理 | Python 链送译前做占位符保护（参照 `NLLBTextProtector` 的 `[Tn]` 思路，自有脚本实现），译后还原；术语表独立文件维护 |

---

## 10. 结论：可借鉴 / 必须避开

### 10.1 可借鉴（主语：我们）

1. **特征码 ＋ 出现序号 ＋ 结果槽的三段定位**：登记模式串 / 序号 / 结果槽 → 扫描存 `record+0x50` → 校验安装；与我方 `sigscan.cpp` / `sigs.h` 同路线，继续保持命中数＝1 的硬门槛。
2. **写保护包裹流程**：`VirtualProtect(RWX)` → 读原始字节备份 → 写 → 恢复原属性；我方 P3 已在此基础上加 `FlushInstructionCache` 与回读校验，比参照物多一道确认。
3. **外置数据表与代码分离**：译文 / 名单 / 配置不塞进二进制，运行期按目录只读加载；我方 `chs\gxt\` / `chs\font\` 目录骨架沿用这一思路。
4. **码位名单制 ＋ 二分判定**：`char_table.dat` 的升序 Unicode 名单 ＋ 二分成员判定，可作为 P4 补字时维护白名单的参照结构。
5. **FNV-1a 查表思路（仅作理解旁路之用）**：basis `0x811C9DC5`、prime `0x01000193`；我方译文已在 gxt 内，不需要自建哈希串池，但理解参照物短串旁路有助于排查"某条文本为何仍显示英文"。
6. **占位符保护思路**：翻译前把颜色 / 按键 / 变量占位符替换成安全占位、译后还原，可在我方 Python 链里复现。
7. **解析思路与键名映射白拿**：GXTStudio 的 IV 解析 / 保存结构、`IVTKEY.lst` 91,248 条名字 ↔ 哈希映射，可用于我方脚本把 CRC 反解成可读键名。
8. **分类注册的组织方式**：按子系统分组注册补丁（`gta_game/font/menu/phone/save/html/mail_reply/whm`），我方 asi 后续扩展 hook 时可按链路层分组，避免注册函数混成一团。

### 10.2 必须避开（主语：我们）

1. **不照搬静默失败**：参照物失配即静默返回；我方所有闸门失败必须写 `[ERROR]` / `[WARN]` 日志，不允许静默空白。
2. **不进无 trampoline 的 inline hook 写死区**：我方 P3 停在 4 字节 imm32 改写；未来若挂 inline hook，先解决指令搬迁与约定对照，不复用参照物"覆盖即丢弃"的写法。
3. **不依赖静态不可列的 exe RVA 表**：参照物 57/3 是 asi 侧安装调用点，exe 目标 RVA 运行时才解析；我方每条挂载点必须有本机复扫命中＝1 的特征 ＋ 明确 RVA 校验，不靠运行时猜测回填。
4. **不绕开游戏自带 GXT 链路去自建解析旁路**：我方复用 `0x8C5CC0` → `0x8C5D70` → `0x8C6780` → `0x8C5DF0` 这条自带链路；运行时不实现 `TABL/TKEY/TDAT` 解析，解析 / 回写只在 Python 侧完成并做往返校验。
5. **不把 GXTStudio 当批量流水线主干**：无 JSONL/TSV/CSV 通道、无"只翻未译"开关、无术语表、CLI 单文件、不建模覆盖层；抽取 / 对齐 / 翻译 / 回写走自有脚本。
6. **不指望 DAT 编辑器补字形**：它只改码点 ↔ 行列映射，不碰字模与字宽；字形 / 字宽问题在 wtd 资源层解决，不纳入该工具链。
7. **不与参照物叠加启用**：真机回归前先移出 `GTA4.CHS.asi` 及其数据表；目标是取代，不是共存挂 hook。
8. **不在授权未核实前复用 / 分发其源码或二进制**：GXTStudio 仓库根目录无 LICENSE；二次开发前先核实 GitHub 仓库许可条款。

### 10.3 对既有路线判断的一处修正

既有文档《hook-方案调研与风险分析.md》写有"GTA IV 所有官方级汉化都是纯资源替换，没有一个在文本取用链路上挂 hook"，并把本机上游简中补丁归入纯资源替换类。本次实测**推翻这一表述对 `.asi` 部分的适用性**：

- `GTA4.CHS.asi` 是 **60 处 inline patch**（57 处 `E8` call ＋ 3 处 `E9` jmp）的绘制 / 取串层补丁，挂在游戏 `.text` 上做签名扫描改写，不是纯资源替换。
- "纯资源替换"这一判断**只对配套的《补丁之补丁 v1.0》成立**：它换 `fonts.wtd`（三章）/ `char_table.dat` / 三章 `american.gxt`，文件层落地，不动游戏代码。
- 两者是**互补的两半**：补丁之补丁提供资源（图集 / 字符表 / gxt 译文），`.asi` 在内存里接管取串 / 宽度 / 绘制旁路；剧情长文本走替换后的 gxt 游戏链路，UI / 短串走 asi 哈希查表。
- 对我方路线的影响：P3 改 gxt 文件名 imm32 ＋ P4 资源层补字形，属于"资源替换 ＋ 单点数据改写"的低风险档；参照物的取串 / 宽度 / 绘制层 inline hook 是高风险档，我方不进入。既有文档未被修改，本报告在此记录该修正口径。

---

## 附录 A 证据索引

### A.1 参照物 `GTA4.CHS.asi` PE 与导入

| 标记 | 值 / VA | 文件 Raw / RVA | 说明 |
|---|---|---|---|
| Machine | `0x014C` | — | x86 / i386 |
| TimeDateStamp | `0x6ABE34F4` | — | 2026-10-01 10:24:52 UTC |
| Characteristics | `0x2102` | — | EXECUTABLE_IMAGE / 32BIT_MACHINE / DLL |
| ImageBase | `0x10000000` | — | — |
| AddressOfEntryPoint | VA `0x1001DDB8` | RVA `0x1DDB8` | DllMain 入口 |
| SizeOfImage | `0x3D000`；SizeOfHeaders `0x400` | — | — |
| DllCharacteristics | `0x140` | — | NX 兼容；无 `DYNAMIC_BASE` |
| `.text` | VA `0x10001000` | RawOff `0x400`，RawSize `0x25800`，熵 6.557 | 代码段 |
| `.rdata` | VA `0x10027000` | RawOff `0x25C00`，RawSize `0xBE00` | 特征码表 / 字符串 |
| `.data` | VA `0x10033000` | RawOff `0x31A00`，RawSize `0x4A00` | 可写数据 / RTTI |
| `.rsrc` | VA `0x10039000` | RawOff `0x36400`，RawSize `0x200` | 仅 manifest `#24` |
| `.reloc` | VA `0x1003A000` | RawOff `0x36600`，RawSize `0x2800` | 标准重定位表 |
| 导入 | KERNEL32 42 ＋ msvcrt 59 | — | 无 VirtualAlloc / WriteProcessMemory / CreateThread / LoadLibrary / GDI / D3D |
| 导出 | 无 | — | DIRECTORY_ENTRY_EXPORT 大小 0 |

### A.2 参照物关键字符串偏移

| 字符串 | Raw | VA | 代码引用 VA |
|---|---|---|---|
| `GTA4.CHS` | `0x27190` | `0x10027190` / `0x10028590` | `0x1000C682` |
| `char_table.dat` | `0x2719C` | `0x1002719C` / `0x1002859C` | `0x1000C879` |
| `whm_table.dat` | `0x271AC` | `0x100271AC` / `0x100285AC` | `0x1000C8C7` |
| `custom_translations.json` | `0x271BC` | `0x100271BC` / `0x100285BC` | `0x1000C915` |
| `font_chs` | `0x261C8` | `0x100261C8` / `0x100275C8` | `0x10006635` |
| `1.2.0.59 sub_91EE50` | `0x269E0` | `0x10027DE0` | 无直接引用（记录项） |
| `"rb"` 模式 | `0x261C4` | `0x100275C4` | 打开辅助 `0x100059D0` |
| json ABI 哈希 3.12.0 | `0x281C0` | `0x100295C0` | `0x10013AB5` |

### A.3 参照物代码 RVA / VA 索引

| 分组 | asi VA / RVA | 说明 |
|---|---|---|
| 入口 / 初始化 | 用户包装 `0x5F40`（`__stdcall`，`ret 0xC`）；主初始化 `0xC700`（`__thiscall`）；路径解析 `0x2990`；签名登记 `0x40E0`；扫描 `0x3FD0`；校验安装 `0x3F20` | 取模块、登记模式串 / 序号 / 结果槽、扫描回填 `record+0x50`、安装、加载三份数据表 |
| 安装器 / 重定位 | A `0x7110`（`E8`，57 处）；B `0x7680`（`E9`，3 处 `0x79A0/0x79CD/0x7B9D`）；批量 `0x6CB0`；相对地址解析 `0x7450`；重定位写入 `0x72D0`；原指令读取 `0x6FD0`；次字节判定 `0x6C40`；原目标解析 `0x8090` | 均 `__cdecl`（`0x8090` 为 `__stdcall` 1 参）；原目标存全局 `DAT_10037B20` |
| 特征段改写 / 兜底 | `0x8620`（`__stdcall`，0 参，410B）；静默出口 `0x87B2`；回跳桩 `0x77D0`；规整桩 `0x77B0/0x77C0` | 唯一命中后 9 字节 `0xCC` 改写 ＋ 1 字节 `0x36`；出口 `pop edi/esi/ebp/ebx; add esp,0x1C; ret`；桩 `pop edi; call [0x10037B24]; or eax,0x80000000; jmp edi` |
| 编码 / 格式 | UTF-16→UTF-8 `0xBAD0`（`__cdecl` 2 参）；逐字 UTF-8 `0x8C50`；格式符解析 `0x1FCE0`（`__fastcall` 1 参，1264B） | `0xBAD0` 遇非法代理对 / 越界码点抛 C++ 异常 |
| 宽度 / 绘制 | 宽度 `0x6210`（`__cdecl` 3 参，返回 `float10`）；单字宽 `0x5F70`；绘制 `0x6660`（`__cdecl` 4 参，661B）；兜底 / quad `0x6B70/0x6BA0/0x6BD0/0x6BF0/0x6C10` | 绘制先查 `0x5850`，`0x6BD0` 画 quad |
| 查表 / 装载 | JSON 查表 `0x5CE0→0x1CB1E`；whm 装载 `0x1BBE0`；char_table 装载 `0x58D0`；二分判定 `0x5850`；哈希 handler `0xB6A0/0xB3C0`；桶链 `0xA560`；透传 `0xA330`；排除表 `0x1CCA2→0x1CCD5`；释放 `0x1CCB3`；标点白名单 `0x6940` | 未命中回填默认串 `.rdata 0x100275B4`；二分未命中走 `0x58B6` 查 `U+FF1F`；桶链哨兵 `0x10037A2C`；排除表 `0x10033058` |
| 常量 / 全局 | 排版常量区 `.rdata 0x100275D0` 起；全局原函数指针 `DAT_10037B20/0x37B24`；哈希对象 / salt `0x10037A28` | 单元 31/32/64/66、缩放 0.06558/0.06712/0.9531；指针由 `0x8090` 写入 |

### A.4 exe 侧 GXT 链路定点（GTAIV.exe 1.2.0.59，ImageBase `0x00400000`）

| exe VA | RVA | 文件偏移 | 角色 | patch 前前 16 字节 |
|---|---|---|---|---|
| `0x008C5DF0` | `0x4C5DF0` | `0x4C51F0` | 语言 ID→GXT 文件名 | `80 7C 24 04 00 56 8B F1 74 07 E8 81 1F FF FF EB` |
| `0x008C5E80` | `0x4C5E80` | `0x4C5280` | 语言跳表（7 个 32 位指针） | `29 5E 8C 00 32 5E 8C 00 3B 5E 8C 00 4D 5E 8C 00` |
| `0x008C6780` | `0x4C6780` | `0x4C5B80` | GXT 解析 / 加载器 | `81 EC 2C 02 00 00 A1 B4 7F 05 01 33 C4 89 84 24` |
| `0x008C5CC0` | `0x4C5CC0` | `0x4C50C0` | 返回 `common:/text` | `53 8B 1D 28 56 BB 01 55 0F B7 53 04 56 33 C9 57` |
| `0x008C5D70` | `0x4C5D70` | `0x4C5170` | 路径拼接器 | `53 56 57 FF 74 24 10 8B F1 E8 42 FF FF FF 8B 5C` |

exe 字符串 / magic 锚点：`0xE7F938` `common:/text`；`0xE7F9B4` `\`；`0xE7F948/0xE7F958/0xE7F964/0xE7F97C/0xE7F970/0xE7F988/0xE7F994/0xE7F9A4` 七个语言 `.GXT` 串 ＋ 默认 `AMERICAN.GXT`；`0xE7FB48` `TABL`、`0xE7FB50` `TKEY`、`0xE7FB58` `TDAT`。

我方 P3 挂载点：`0x008C5DF0` 函数内 `fn+0x39` 操作码 `0xB8`，`fn+0x3A`（即 `0x008C5E2A`）imm32 原值 `0x00E7F948`（`AMERICAN.GXT`，重定位后按实际加载基址重算期望值）；P3 只改这 4 字节。

### A.5 外置数据表解剖

| 文件 | 大小 | 头字段 | 条目 / 结构 |
|---|---|---|---|
| `char_table.dat` | 14,324 B | u32 ＝ 3,580 | 3,580 × u32 Unicode 码位，升序；`U+2014` … `U+FF65`；CJK 统一表意 3,561 / CJK 标点 9 / 全角 9 / 通用标点 1；原版名单 3,517 |
| `whm_table.dat` | 780,676 B | u32 ＝ 5,388 | 43,108 字节 `{散列 u32, 索引 u32}` 头表（结束于 `0xA864`）＋ `0xA864` 起 737,568 字节 NUL 分隔 UTF-8 串池；5,382 段，5,349 段含汉字，平均 48.7 字符，最长 666 |
| `custom_translations.json` | 3,046 B | JSON 对象 | 86 键 UI 选项中译；旁挂 `+滤镜中文翻译` 3,123 B / 89 键，代码未引用 |

### A.6 外部字库文件实测

| 路径 | 大小 | 修改时间 |
|---|---|---|
| `pc\textures\fonts_chs.wtd` | 2,434,864 | 2023-07-02 17:58:52 |
| `TLAD\pc\textures\fonts_chs.wtd` | 3,018,109 | 2023-07-02 17:59:28 |
| `TBoGT\pc\textures\fonts_chs.wtd` | 2,498,515 | 2023-07-02 17:59:12 |
| `pc\textures\fonts.wtd` | 101,044 | 2012-04-06 20:11:22（原版未覆盖） |
| `pc\textures\fonts_r.wtd` / `fonts_j.wtd` / `fonts_r_streamed_1.wtd` | 125,940 / 598,680 / 48,457 | 2012-04-06 |
| `common\data\fonts.dat` / `fonts_r.dat` / `fonts_j.dat` | 10,850 / 12,285 / 18,667 | 2012-04-06 |

### A.7 GXT 实测基线（探针 `gxt_probe.py`）

| 文件 | 大小 | 表数 | 条目数 | 带内联名表 | 头 version/bits |
|---|---|---|---|---|---|
| `common\text\chinese.gxt`（base） | 2,977,612 B | 524 | 59,634 | 523（仅 MAIN 无） | 4 / 16 |
| `TLAD\common\text\chinese.gxt` | 820,498 B | 142 | 18,557 | 141 | 4 / 16 |
| `TBoGT\common\text\chinese.gxt` | 995,302 B | 163 | 23,910 | 162 | 4 / 16 |
| `update\common\text\chineseFF.gxt`（覆盖层） | 4,324 B | 1（MAIN） | 84 | 0 | 4 / 16 |

---

## 附录 B 未确定项与补证方式

> 下表合并四份材料的未确定项并去重；每条写"缺什么证据 ＋ 用什么手段补（动态快照 / 上传测试 / 真机日志）"。手段口径：**动态快照**＝运行时 dump 内存 / 断点观察调用链与缓冲区；**上传测试**＝隔离宿主或真机小范围部署观察；**真机日志**＝按我方日志规范留 `[ERROR]` / `[WARN]`。

| # | 未确定项 | 现状 / 卡在哪 | 缺什么证据 | 补证手段 |
|---|---|---|---|---|
| B1 | 33 个唯一命中函数的运行时语义 | 静态侧未逐条反编译 33 个命中函数；不能排除个别补丁间接影响文本显示 | 每个命中函数的原型、入参、返回值、是否触及取串 / 排版 | 动态快照：在扫描回填地址处下断点，记录调用者与返回串；或真机挂起后 dump `.text` 补丁点对照表 |
| B2 | 各 hook 运行时 exe RVA 表 | 目标由签名扫描运行时解析，静态只 asi 侧登记了特征与结果槽；批量安装器偏移相对基址对象，未逐一换算 | `0x3FD0` 解析出的全部 exe VA → RVA 映射表 | 动态快照：运行时读取记录 `+0x50` 槽，落成 exe RVA 表；与我方 `sigs.h` 四条目标做邻近比对 |
| B3 | handler 与原函数调用约定逐字匹配 | 只核验了 asi 侧自身约定；`ECX=this`、浮点返回、栈清理逐项未对游戏原型 | 被 hook exe 原函数的原型签名（this/thiscall/ret n / 浮点返回位置） | 动态快照 ＋ 静态对照：逐个反汇编被 hook 的 exe 原函数；真机日志观察是否出现 ESP 报错 / 崩溃 |
| B4 | `0x8620` 改写的确切语义 | 确认是"特征定位 ＋ 9 字节 `0xCC` 改写 ＋ 1 字节改 `0x36`"，目的未确认（版本校验绕过 / 崩溃检查绕过 / 反调试绕过） | 改写前后该处机器码行为、改写后被哪个函数引用、不改写时游戏行为差异 | 动态快照：断点观察 `0x8620` 命中前后指令流；真机对照该补丁开关前后的运行表现 |
| B5 | key→string 查询层被接管的 exe 原生入口 | asi 取串包装入口 `0xB6A0` / `0xB3C0` 已证实被 hook；但对应 exe 侧哪个原生函数（原型签名、exe RVA）证据不足 | 4 个安装点上游的 exe call-site、原函数原型 | 动态快照：上溯 `0x5CE0` / `0xB6A0` / `0xB3C0` 调用链到具体 exe call-site |
| B6 | 命中后译文缓冲的输出编码 | 命中路径 `0x1E876` 为 memcpy；输出缓冲最终编码（UTF-8 直拷 vs 二次转 UTF-16）证据不足 | 下游 `0xBAD0` / `0xBBF0` 收到的缓冲编码与长度 | 动态快照：断点读输出缓冲字节序列与终止符，对照 UTF-8 / UTF-16LE |
| B7 | `0x5F40` 的 CRT 注册槽位 | 无 rel32 call、无落盘绝对指针；静态未追溯到固定 RVA | 用户 DllMain 回调被 CRT 调度槽引用的写入点 | 动态快照：观察 CRT dispatch 数据段中回调指针写入；静态侧继续追踪 `.CRT$XCU` 槽表 |
| B8 | 是否经 `GetProcAddress` 运行时探测 FusionFix / 其他 ASI 插件 | 二进制内无 `FusionFix` / `fusionfix` 字符串；`GetProcAddress` 已导入，但未见指向外部插件名的字符串 | 运行时是否枚举 / 查询其他 asi 导出符号 | 动态快照：钩 `GetProcAddress` 调用参数；真机列出共存插件清单回归 |
| B9 | 补丁记录区参数语义 | `0x3614`(13,844)、`0x3D`(61)、`0x07`、`0x06` 四个双字字段的确切含义未确定 | 字段在扫描 / 安装流程中的读写关系 | 动态快照：跟踪记录区结构在 `0x3FD0` / `0x3F20` 中的使用；静态侧补反汇编 |
| B10 | 静态"写入字节"结论的落盘验证 | 所有"写入字节"来自静态反汇编指令形态（`0xE9` 跳板 / `0x90` NOP），未运行 asi | 安装后 exe 内存中各补丁点的实际字节 | 上传测试：隔离宿主加载后 dump 补丁点前后 16 字节，与静态预期对照 |
| B11 | `whm_table.dat` 散列算法 / 密钥与原文映射 | 头部 4 字节高熵，未做逆散列；串池索引与英文原文的对应关系未逐一对上 | 散列键的明文编码、salt 与 finalization 完整公式 | 动态快照：断点看查询入参（英文串）/ 出串；或获取上游工程源码对照 |
| B12 | wtd 字形 advance / 步进字段结构 | 未解包 `fonts_chs.wtd`，逐字全角 / 半角未核对 | 图集内每个字形的步进 / 宽高字段布局 | wtd 解包工具（OpenIV / GIMS 导出）读字形表；静态解剖图集纹理与描述头 |
| B13 | 缺字分支最终表现 | 静态反汇编只到回退 `U+FF1F`；未命中后是画占位符 / 保留原字 / 问号，未跟踪绘制分支 | 回退码也不在名单内时的绘制路径 | 真机日志 ＋ 上传测试：构造生僻字串观察渲染表现（方块 / 问号 / 原字） |
| B14 | 补丁包 wtd 覆盖是否真正落到现网 | bat 目标 `fonts.wtd`，但真机 `fonts.wtd` 仍是 2012 原版 101,044 B；中文图集名 `fonts_chs.wtd` 与包内 `update\...\fonts.wtd` 大小 / 时间戳不一致 | 安装时是否改名落到 `fonts_chs.wtd`，或该 wtd 覆盖步骤在当前部署中未执行 | 对照 `_ORIGINAL_fonts_pc.wtd` 哈希与现网两个 wtd；复核 `安装.bat` 目标路径与改名逻辑 |
| B15 | 行距是否被补丁重调 | 未发现独立行距常量，但未逐函数跟踪行高计算 | 文本换行 / 行高计算函数中的行步进系数是否被改 | 静态反汇编换行 / 行高函数；真机对比中英文本行距 |
| B16 | `custom_translations.json+滤镜中文翻译` 是否被读取 | 代码中只找到无加号文件名引用 | json 加载器的路径拼接是否枚举旁挂文件 | 静态反汇编 json 加载器路径逻辑；动态快照观察打开文件列表 |
| B17 | `0x` 前缀十六进制键在 IV 导入时是否被长度校验拦截 | 导出加 `0x` 前缀后 10 字符，超过 IV `maxKeyLength=8`；是否在别处先剥前缀未逐行确认 | 真实导入闭环中键是否被拒 / 截断 | 上传测试：在副本上跑"导出→关闭→导入→另存 GXT"闭环，观察校验报错 |
| B18 | 59,634 键全量驻留下的首开 / 编辑响应 | 底层全量驻留、无磁盘分页；无 59k 键实测数据 | 本机实机打开 base `chinese.gxt` 的耗时与内存占用 | 上传测试：编译后真机打开三份 gxt，记录首开时间 / 内存 / 大表编辑响应 |
| B19 | `calculateGTA4Hash` 兜底哈希是否与游戏 IV 实际校验一致 | 自定义乘性哈希（乘子 1025），非标准 CRC32；新增具名键命中情况未验证 | 新增具名键在游戏内是否被正确解析 / 命中 | 上传测试：新增一条具名键 gxt，进游戏观察文本是否显示；优先走 `IVTKEY.lst` 映射 |
| B20 | GXTStudio 仓库 LICENSE 实际条款 | 根目录无 LICENSE / COPYING；README 仅写"免费开源"，未标 SPDX | 仓库许可页具体条款（MIT / GPL / Apache / 保留所有权利） | 联网核实 GitHub 仓库 `Lzh102938/GXTStudio` 许可页；必要时联系作者确认 |
| B21 | base / TLAD 键名反解覆盖率 | 已测 TBoGT 20,712 / 23,910 ＝ 86.6%；base / TLAD 覆盖率未另算 | 两份 JSONL 中可反解为可读名的键数 | 脚本复用 `keylist_IVTKEY.lst` 对 base / TLAD 键做覆盖率统计 |
| B22 | GXTStudio 保存后结构往返一致性 | 读路径吻合、写路径两遍重算偏移 ＋ 保留原 CRC，但未实测保存后与原文件逐块比对 | 保存后表偏移 / 内联名 / UTF-16 终止符 / CRC 是否逐块一致 | 上传测试：副本上保存后重新解析，逐块比对偏移、内联名分布与条目文本 |
| B23 | 我方三章外置 gxt 能否被引擎自带解析器读取 | `zchs_base.gxt` 2,709,976 B / `zchs_TLAD.gxt` 796,424 B / `zchs_TBoGT.gxt` 978,944 B，均回环 PASS、逐条文本 0 不一致，但尚未部署到游戏 | 引擎 `0x8C6780` 对我方 gxt 的解析 / 加载结果 | 上传测试：隔离宿主 → 真机部署，日志留 `[ERROR] gxt load failed` 并回落原版；分章节切换验证取到各自 gxt |

