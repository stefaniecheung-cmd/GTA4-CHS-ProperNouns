# 04 · GXTStudio 工具链评估（改 GXT 格式 + 润色中文汉化）

> 评估对象：本地源码 `C:\Game\_tools\gxtstudio_src\GXTStudio-main`（C++ / Qt6，作者 Lzh10_慕黑，自称 III.VC.SAGXTExtracter 替代品）。
> 评估方式：只读源码 + 只读二进制探针，**未编译、未安装、未联网下载新版**；未改动 `gxt_out\` 与游戏目录任何文件。探针脚本：`C:\Game\_tools\chs_re\gxt_probe.py`、`keylist_coverage.py`。
> 证据标注：`【源码】`= 直接读源码得到的确定事实（附文件 / 类 / 函数）；`【实测】`= 本机二进制或数据文件实测；`【推断】`= 基于代码结构 / 经验的判断，尚未上机验证。

---

## 1. 一句话结论

**GXTStudio 可以作为「人工逐条校对 / 润色」的桌面 UI 辅助工具，但不能作为本项目「程序化批量流水线」的主干；中文字形补齐它帮不上忙。** 我们的批量抽取、对齐、未译识别、回写 GXT 仍应走自己的脚本（复用它的解析思路或解析代码），GXTStudio 只在需要人工看上下文、改个别条目时打开对照。

| 用途 | 判定 | 前提 / 缺口 |
|---|---|---|
| 打开三份 `chinese.gxt` 人工校对、改文案、撤销重做、正则搜索 | **有条件可用** | 需先在本机编译出可执行文件；键名仅约 86.6% 能反解成可读名，其余显示为 `0xCRC` |
| 保存后结构不被改坏（表偏移 / 内联表名 / UTF-16 终止符） | **读路径吻合，写路径需上机回归** | 源码两遍算偏移、保留原 CRC；但未实测保存后与原文件逐块比对 |
| 吃我们的 `JSONL / gap TSV` 做批量翻译再回写 | **不能直接接** | 原生只认 TXT（compiler / 普通文本 / 自定义模板），无 CSV / TSV / JSON 导入导出；CLI 也是单文件 TXT 往返 |
| 用内置 AI 只翻未译项、带术语表跑批量 | **不能满足** | 翻译只作用于勾选行；无术语表 / 词典文件；无「跳过已译 / 空值」开关；模型与端点基本写死 |
| 补中文字形（字模 / 字宽 / 加字） | **不能** | DAT 编辑器只维护「码点 ↔ 图集行列」映射，不碰字模位图、不改字宽；TXD 仅导出不编辑 |
| 覆盖层 `update\chineseFF.gxt` 与 base 的同键覆盖关系 | **不建模** | 每个标签页只装一个扁平 GXT，没有 base+overlay 合并 / 覆盖优先级概念 |

---

## 2. 格式实现核对（对照我们已实测的 IV 结构）

我们的事实基线：魔数 `0x00100004`（LE：version=4, bits=16）→ `TABL`+u32 size（12 字节/项：8 字节表名 + u32 偏移，524 张表）→ 每张表 [可选 8 字节内联表名] + `TKEY`+u32 size（u32 offset + u32 crc，8 字节/项）+ `TDAT`+u32 size（UTF-16LE，offset 为字节偏移，文本以 `0x0000` 结尾）；键是 CRC 哈希而非名字。

### 2.1 读路径（解析）

| 结构点 | 源码实现 | 与我们基线是否吻合 |
|---|---|---|
| 文件头识别 | `GXTParser::parse()`，`GXTParser.cpp:596-617`：读前 4 字节解 `version`/`bits`，`version==4 && bits==16` 判为 `GTA_IV`，随后 `fseek(4)` 跳过头部 | 【源码】吻合；对应魔数 `0x00100004` |
| TABL 条目 | `GXTParser.cpp:925-935`：`struct TblEntry { char name[8]; uint32_t offset; }`，12 字节/项 | 【源码】吻合 |
| 可选内联表名 | `GXTParser.cpp:949-959`：先 peek 8 字节，若不是 `TKEY` 就跳过 8 字节（`hasTableName=true`） | 【源码】吻合「可选 8 字节内联表名」 |
| TKEY 条目（SA/IV） | `GXTParser.cpp:1044-1052`：逐项读 `offset`(u32) + `crc`(u32)，8 字节/项 | 【源码】吻合 |
| TDAT 编码 | `GXTParser.cpp:1068-1106`：`bitsPerChar==16` 走 UTF-16LE，`offset/2` 转 u16 索引，二分找下一个 `0x0000` 终止；IV 分支**强制** `WideCharToMultiByte(CP_UTF8)`，不再回退猜测编码（`:1096` 注释） | 【源码】吻合；中文 UTF-16LE 解码路径明确 |
| 键的存储 | `GXTParser.cpp:1105`：`tabl.entries.push_back({u32_to_hex(crcs[i]), val})`，键存为十六进制 CRC 串 | 【源码】吻合「键是哈希不是名字」 |
| 表 / 条目规模 | 解析全程 `std::vector` 动态 `reserve`，未见表数或条目数硬上限；唯一计数上限在辅助 DAT 解析 `parseDAT`（`GXTParser.cpp:1929`，count>2,000,000 拒识），与 GXT 无关 | 【源码】524 表 / 59,634 键不存在截断上限 |

### 2.2 写路径（保存）

| 结构点 | 源码实现 | 评估 |
|---|---|---|
| 两遍计算偏移 | `GXTEditor::saveAsGTA_IV()`，`GXTEditor.cpp:1640-1797`：第一遍 `:1679-1706` 算每张表偏移 / TKEY 大小 / TDAT 大小；第二遍 `:1726-1773` 写数据，最后 `:1776-1784` 回填 TABL 表名与偏移 | 【源码】偏移是重算的，不是照搬旧文件；结构可重建 |
| 文件头 | `:1709-1712` 写 `version=4`、`bits=16` | 【源码】吻合 IV 头 |
| 内联表名 | `:1687-1690`、`:1731-1736`：**非 MAIN 表**写 8 字节补零表名；MAIN 不写 | 【源码】与实测一致（见 2.3）；但这是「MAIN 无内联、其余都有」的固定假设，若原文件某张非 MAIN 表本就无内联名，保存时会被补上——【推断】属低概率边界，需回归确认 |
| TKEY 哈希回填 | `:1746-1754`：键能按十六进制解析（`std::stoul(...,16)`）就**保留原哈希**；解析不成才查 `IVTKEY` 映射，再不行用 `calculateGTA4Hash` 兜底 | 【源码】现有条目往返保留原 CRC；新增 / 改名条目才依赖哈希映射 |
| TDAT 编码与终止符 | `:1768-1771`：`utf8_to_utf16le` 转码后写数据，再补 `\0\0`（UTF-16 null） | 【源码】吻合 UTF-16LE + 双字节终止 |
| 偏移口径 | `:1756`、`:1760`：`currentDataOffset` 按字节累加（UTF-16 字节数 + 2），相对 TDAT 数据区起始 | 【源码】与「offset 是字节偏移」一致 |

### 2.3 本机二进制实测（探针 `gxt_probe.py`，只读）

| 文件 | 大小 | 表数 | 条目数 | 带内联名的表 | 头 version/bits |
|---|---|---|---|---|---|
| `common\text\chinese.gxt`（base） | 2,977,612 B | 524 | 59,634 | 523（仅 MAIN 无） | 4 / 16 |
| `TLAD\common\text\chinese.gxt` | 820,498 B | 142 | 18,557 | 141 | 4 / 16 |
| `TBoGT\common\text\chinese.gxt` | 995,302 B | 163 | 23,910 | 162 | 4 / 16 |
| `update\common\text\chineseFF.gxt`（覆盖层） | 4,324 B | 1（MAIN） | 84 | 0 | 4 / 16 |

【实测】三张主文件的头、TABL、内联名分布、TKEY 8 字节项、UTF-16 终止与源码读路径假设一一对应；探针解出的条目数与 `summary.json`（base 59,634 / TLAD 18,557 / TBoGT 23,910）一致。

### 2.4 哈希口径的一个待核实点

【源码】`GXTEditor.cpp:927-951` 的 `calculateGTA4Hash` 是自定义乘性哈希（A-Z 转小写、`\`→`/`、乘子 1025），**不是** `:128-150` / `:886-899` 的标准 CRC32；标准 CRC32 / JOAAT / JAMCRC 另用于 SA / GXT2 等版本。我们基线记录「IV 键为 CRC32」。对**现有条目往返**无影响（保留原 CRC）；但对**新增具名键**，兜底哈希是否与游戏实际校验一致，本地未验证。【推断】IV 新增键应优先走 `keylist\IVTKEY.lst` 映射，不要依赖兜底哈希。

---

## 3. 大文件与性能

- 【源码】`GXTEditor::loadFromFile()`（`GXTEditor.cpp:37-62`）调用 `parser.parse(path)` 后，把所有表 / 条目**整份复制**进内存 `tables` 向量；`parseWithMemoryMap()`（`GXTParser.cpp:1204`）虽存在，但加载入口未走内存映射。
- 【源码】UI 模型 `GXTTableModel`（`GXTTableModel.h:103` 起）继承 `QAbstractTableModel`，显示层有 `RowCache` 与 `buildPartialDisplayCache(firstRow,lastRow)`（`:193`）只构建可见区域缓存；但底层数据仍是全量驻留，**不是磁盘分页 / 懒加载**。
- 【源码】解析与保存各有后台线程：`ParseWorker`、`SaveWorker`（`SaveWorker.h:52`），带进度回调。
- 【实测】base 2.98 MB / 59,634 键；按 Qt `QString` 估算全量驻留约几十 MB 量级。【推断】这个量级在现代 PC 上不会卡死，60k 行的表格模型也在其设计范围内（`SmartTranslator.h:79` 任务上限 50,000、`QList` 上限 100,000 也侧面说明按万级条目设计）；但**没有**针对 59k 键的实测数据，首开 / 全量替换时的卡顿程度需上机确认。
- 【源码】未发现按条目数截断的逻辑；风险不在「截断」，而在全量驻留下大表编辑时的 UI 响应。

---

## 4. 覆盖层与多文件往返

- 【源码】每个 `FileTab` 持有单一 `filePath` 与一份 `tables` / `noTablEntries`（`SaveWorker.h:33-49`）；代码中没有 `update\` 目录扫描、没有 base/overlay 双层结构、没有同键优先级合并模型。
- 【源码】唯一的「合并」是 GUI 内把多个 **TXT** 文本合并进当前标签页：`GXTStudio::importAndMergeTxtFiles()`（`GXTStudio.cpp:3431`），冲突时弹 `ConflictDialog` 逐条选择「替换 / 跳过」（`:4149-4179`）。这是文本级人工合并，不是 GXT 覆盖层语义。
- 【实测】覆盖层 `update\common\text\chineseFF.gxt` 仅 1 张 MAIN 表、84 条；同目录还有 `americanFF/CV/RR/1.gxt` 等小文件。游戏运行时由加载顺序决定同键取值，这套关系 GXTStudio 不记录。
- 结论：【源码】把 `chineseFF.gxt` 单独打开、单独保存，它仍是一个独立小 GXT；**不会**自动与 base 对齐，也不会标注某键来自覆盖层。若我们要维护「base + 覆盖层」双层文本，必须在自己的脚本里建模。

---

## 5. 字体 / DAT 字库能力（能否补中文字形）

### 5.1 工具里有两类「DAT」，别混淆

| 类别 | 源码 | 内容 |
|---|---|---|
| 辅助文本 DAT（hash/offset/text） | `GXTParser::parseDAT()`，`GXTParser.cpp:1908`；`DATEntry{hash,offset,text}`（`GXTParser.h:191-195`） | 结构类似 GXT 的键值文本表，**不是字库** |
| 字符映射表 DAT（码点 ↔ 图集行列） | `CharTableParser`，`CharTableParser.h:15-25` / `CharTableParser.cpp` | 编辑器真正能改的「字库」 |

### 5.2 字符映射表到底能改什么

- 【源码】VC 版：`loadGtaVc()`（`CharTableParser.cpp:13-52`）读 `0x10000×2` 字节映射，每项 `(row,col)`；`saveGtaVc()`（`:120-166`）反向写回 65536 项表，未用位置填 `(63,63)`。
- 【源码】IV 版：`loadGtaIv()`（`:54-118`）按 UTF-32LE 码点序列读字符列表，64 列网格排布；`saveGtaIv()`（`:168-206`）收集有效码点重新写出。
- 【源码】`CharTableData.cells`（`CharTableParser.h:11`）是 `QVector<uint16_t>` 码点网格；**结构里没有字模位图、没有字宽 / 间距 / kerning 字段**。
- 【源码】图集纹理走 `TXDExporter`（`TXDExporter.h:109-122`），接口只有 `exportTxd` / `exportTxdWithImages` / 异步导出，**没有导入或改像素的接口**。

### 5.3 结论

【源码】GXTStudio 的 DAT 编辑只能增删「某个 Unicode 码点是否出现在字体图集的第几行第几列」，即维护码点清单与映射；**不能编辑字模像素、不能新增图集里不存在的字形、不能改字宽**。中文字形不够时，它顶不上——字形 / 字宽问题仍要在字体图集（TXD / 字体替换）或我们自己的绘制层解决。README 所称「编辑 DAT 字库」（`README.md:55`，屏蔽 ASCII 与重复字符）指的也是这层码点录入，不是改字模。

---

## 6. 流水线衔接：导出 / 导入 / AI / 批处理

### 6.1 交换格式（与我们 `gxt_out\` 的对接）

- 【源码】原生导出只有文本：
  - GXT-compiler 格式：`GXTEditor::saveAsGXTCompilerFormat()`（`GXTEditor.cpp:803-861`），`[KEY]` / `[KEY:TABLE]` + 文本；8 位十六进制键自动加 `0x` 前缀（`:841-852`）。
  - 普通文本：`saveAsText()`，`[TABLE]` + `KEY=VALUE`。
  - 自定义模板导出：`GXTStudio.cpp:5163-5213`，占位符仅 `%key%` `%value%` `%table%` `%tabl%`，产物仍是按行渲染的 **TXT**。
- 【源码】导入只认 TXT：`importTxtFile()`（`GXTStudio.cpp:2312`）、合并 `importAndMergeTxtFiles()`（`:3431`）、自定义规则 `importCustomFormatFile()`（`:3152`）。
- 【源码】全仓检索：`CSV` / `TSV` / `JSONL` 无任何解析或导出实现；`JSON` 仅出现在 `DebugConfigDialog.h:87,112` 的调试配置文件过滤器里。
- 【实测】我们 `gxt_out\` 的资产：
  - `text_american.jsonl` / `text_chinese.jsonl`：当前落盘内容为 **TBoGT 单份**（23,911 / 23,910 行，163 张表），schema `{"t": 表名, "crc": 8位大写十六进制, "s": 文本}`。
  - `gap_base.tsv` / `gap_TBoGT.tsv` / `gap_TLAD.tsv`：表头 `table / crc / english`。
  - `summary.json`：base zh 59,634 / en 59,661（缺 27）/ ascii_only 26,983；TLAD 18,557 / 18,557 / 8,649；TBoGT 23,910 / 23,911 / 缺 1 / 11,119。
- 对接判断：【源码】我们的 JSONL / TSV **不能被 GXTStudio 直接吃**；要走它，必须先写一层转换器把 JSONL/TSV 排成它的 compiler TXT，润色后再从 TXT 导回 GXT。中间这层格式转换、键值对齐、未译标记仍得自己写。

### 6.2 导入键名校验（往返的一个摩擦点）

- 【源码】`validateImportKeyName()`（`GXTStudio.cpp:2157-2174`）：键非空、长度 ≤ `maxKeyLength`、字符仅限字母 / 数字 / `_` / `-`；IV 的 `maxKeyLength=8`（`:3246`）。
- 【源码】导出时十六进制键会被加上 `0x` 前缀（`GXTEditor.cpp:841-852`）；`0x` + 8 位 = 10 字符，且 `x` 虽合法，但长度会超过 IV 的 8 字符上限。
- 【推断】compiler TXT 自导出再导入时，`0x` 前缀键可能在 IV 下被长度校验拦下；是否在别处先剥前缀，本地未逐行确认。**结论：TXT 往返需上机实测一次「导出→关闭→导入→另存 GXT」闭环**，不要默认键能原样回来。

### 6.3 内置 AI 翻译

| 维度 | 源码事实 |
|---|---|
| 服务商 / 端点 | 【源码】`SmartTranslator.cpp:104-109`：写死 `deepseek`（`https://api.deepseek.com/chat/completions`）与 `xiaomi`（`https://api.xiaomimimo.com/v1/chat/completions`）；免费通道走 Google 非官方端点 / MyMemory（`GoogleFreeTranslator.cpp:201,240,387`） |
| 可配置项 | 【源码】API Key、模型、系统提示词、批次提示词（`{contents}` 占位）、批次大小 / 并发 / 重试（`SmartTranslator.h:84-96`、`TranslateConfigDialog.cpp:371-405`）；模型清单基本固定（`TranslateConfigDialog.cpp:64-73`），对话框未暴露自定义端点 URL |
| 术语表 / 一致性 | 【源码】无独立术语表 / 词典文件；术语一致性只能写进系统提示词文本（`TranslateConfigDialog.cpp:27,86`） |
| 只翻未译项 | 【源码】翻译入口 `translateSelectedRows` 作用于**当前勾选 / 选定行**（`GXTStudio.cpp:7085-7146, 9311-9371`）；未见「自动跳过空值 / 跳过已译 / 跳过与英文相同」的开关。要只翻未译，需先用搜索 / 过滤手动圈出范围 |
| 格式保护 | 【源码】`NLLBTextProtector`（`NLLBTextProtector.h:19-29`）翻译前把 `~r~`/`~k~`/`%d` 等替换成 `[Tn]` 占位、译后还原，保护颜色 / 按键 / 占位符 |
| 在线依赖 | 【源码】云端 API 与免费端点都需联网；更新检查也走在线接口（`AboutDialog.cpp:690,802`）。无离线翻译模型 |

### 6.4 命令行 / 批处理

- 【源码】`main.cpp:134` `runCliMode()` 提供无 UI 命令：`--gxt2txt`（`:172`）、`--txt2gxt`（`:246`）、`--gendat` / `--gendattxt` / `--dattxt2dat` / `--dat2dattxt`（`:411,500,573,683`）、`--info`（`:758`）。
- 【源码】CLI 每条命令处理**单个文件**；批量导出 / 批量并行解析只在 GUI（`GXTStudio.cpp:1595` `batchExport`、`:2127`）。
- 【推断】CLI 可用于脚本里做一次 GXT↔TXT 转换，但中间格式仍是 TXT，且无 JSONL/CSV 通道；把它接进我们的自动化流水线，仍需自写格式适配层。

---

## 7. 风险与授权

### 7.1 许可（发布 / 改造前必须先核实）

- 【实测】源码根目录**没有** `LICENSE` / `COPYING` 文件；仅随附的第三方子模块带许可：`qwindowkit-main\LICENSE`、`syscmdline\LICENSE`。`README.md:99` 仅写「本软件免费开源」，**未标注 SPDX 协议**（MIT / GPL / Apache 等）。
- 【推断】在未取得明确授权前，默认「保留所有权利」：把它的二进制或源码打包进我们的发布包、二次改造后再分发，都存在授权风险。若要复用其解析代码，需先到其 GitHub 仓库（`AboutDialog.cpp:340` 指向 `Lzh102938/GXTStudio`）核实 LICENSE 条款，或直接联系作者确认。
- 【源码】第三方子模块 `qwindowkit` 另有自己的许可，复用核心时需一并遵守。

### 7.2 平台与依赖

- 【源码】`CMakeLists.txt:44-52`：Qt6 Core / Gui / Widgets / Concurrent / Network；C++17（`:15`）；MSVC 2022 x64（`:37-39`）；`qwindowkit` 以子目录编入（`:58`）；WebP 为 `REQUIRED`（`:73`），zlib 可选（`:76`）。
- 【源码】构建路径写死本机：Qt 在 `D:/Qt/6.11.1/msvc2022_64`（`:7`）、vcpkg 在 `D:/vcpkg/installed/x64-windows`（`:64,67`），可用 `CMAKE_PREFIX_PATH` / `VCPKG_INSTALL_DIR` 覆盖。
- 【源码】`app.manifest` 声明 `amd64`，supportedOS 含 Win7 / 8 / 8.1 / 10 / 11。【推断】manifest 声明 Win7，但 Qt6 运行时实际官方支持区间偏 Win10+；本机是 Win10/11 环境，不构成阻碍，跨系统分发时需注意。
- 【源码】源码树完整：核心 `.cpp/.h`、`keylist\IVTKEY.lst`（91,248 条映射，实测）、`font\`、`qwindowkit-main\` 均在；未见缺失子模块目录。【推断】具备在装齐 Qt6 + vcpkg 依赖后编译的条件，但本机按约束未编译验证。

### 7.3 键名反解覆盖率

- 【实测】`keylist\IVTKEY.lst` 共 91,248 条「名字 ↔ 哈希」映射；对落盘的 TBoGT 中文 23,910 键，可反解为可读名的 20,712 条，**覆盖率 86.6%**；其余约 13.4% 在界面上只能显示 `0xCRC`。
- 【推断】base / TLAD 的覆盖率需用对应 JSONL 另算；未命中的键不影响保存（保留原 CRC），只影响人工校对时的可读性。

---

## 8. 对我们现有资产的直接可用性判断

我们的盘子：base 59,634 键（英文 59,661，缺 27）、TLAD 18,557、TBoGT 23,910；中文侧 26,713 条与英文逐字节相同（约 45% 实际未译，题给基线）；`summary.json` 的 `ascii_only` 为 base 26,983 / TLAD 8,649 / TBoGT 11,119。

| 我们的环节 | 能否接 GXTStudio | 说明 |
|---|---|---|
| 已抽取的 JSONL / gap TSV 对齐结果 | **不能直接接** | 无 JSONL/TSV 通道；需自写转换器排成 compiler TXT 才能进它的界面 |
| 45% 未译条目的批量补译 | **不建议用它跑主干** | 无「只翻未译」开关、无术语表、端点写死且依赖联网；批量一致性与可复现性不如我们自己的脚本 + 可控翻译接口 |
| 人工逐条润色、看上下文、改个别长文本 | **可作为辅助 UI** | 表格 / 正则搜索 / 撤销重做 / 颜色标记预览（`TextRenderWidget`）可用；前提是先编译出可执行文件并跑通 TXT 往返闭环 |
| 三份主文件 + 覆盖层的整体回写 | **不能由它独立承担** | 无覆盖层建模、无批量 CLI、格式往返需转换层；回写 GXT 仍应以我们自己的脚本为准 |
| 字形 / 缺字补齐 | **不能** | 只维护码点映射，不碰字模与字宽 |

【推断】现实分工：**抽取 / 对齐 / 未译识别 / 批量翻译 / 回写 GXT 走我们自己的 Python 脚本**；GXTStudio 仅在人工复核阶段打开对应 GXT（或转换出的 TXT）做上下文对照与个别条目修改，改完仍回到脚本流程落盘，避免把中间状态锁进它的工程格式。

---

## 9. 若要复用 / 二次开发，成本与替代做法

### 9.1 可借鉴的源码资产

- 【源码】IV 解析 / 保存结构清晰：`GXTParser.cpp`（读）、`GXTEditor.cpp::saveAsGTA_IV`（写）、`utf8_to_utf16le_vector`（`GXTEditor.cpp:76-95`）、CRC32 / 哈希表实现。若我们自己写解析器，可对照其 TABL/TKEY/TDAT 偏移与内联名处理。
- 【源码】`keylist\IVTKEY.lst` 91,248 条名字↔哈希映射，可直接被我们的脚本读取，用于把 CRC 反解成可读键名（覆盖率见 7.3）。

### 9.2 二次开发成本（若硬要基于它改）

- 【推断】要补：JSONL/CSV 导入导出、「只翻未译 / 跳过已译」过滤、术语表挂载、base+overlay 合并模型、自定义翻译端点；CLI 扩成多文件批处理。这些都要改 Qt UI 层与 `SmartTranslator`，且受 7.1 授权约束。
- 【推断】相比之下，我们已有 `gxt_out\` 的 JSONL/TSV 脚本链路，围绕自有脚本加一个 GXT 读写模块，比改造这套 Qt 工程更可控、可回归、可进 CI。

### 9.3 替代做法

1. **解析 / 回写**：自写 Python IV GXT 读写器（结构已在第 2 节逐条核对），直接产出 / 消费我们的 JSONL；CRC、偏移、内联名在脚本里显式处理并做往返校验。
2. **人工校对**：需要图形界面时再用 GXTStudio 打开对照；或在自有脚本上做一个简单的双栏（英 / 中）校对表。
3. **批量翻译**：自有脚本按 `gap_*.tsv` 圈定未译项，走可控翻译接口，术语表以独立文件维护，结果回写 JSONL 后再打包 GXT。
4. **字形**：单列字体图集 / 字宽方案评估，不依赖本工具。

---

## 10. GXTStudio 结论

### 能做什么

1. 【源码】打开 IV 格式 GXT，按 TABL/TKEY/TDAT 解析 UTF-16LE 文本，支持多标签、正则搜索 / 过滤、撤销重做、颜色与按键标记预览。
2. 【源码】保存 IV GXT 时两遍重算表偏移与 TDAT 偏移，现有条目保留原 CRC，UTF-16LE + 双字节终止符写回。
3. 【源码】提供单文件 CLI（`--gxt2txt` / `--txt2gxt` / `--info` 等），可在脚本里做一次 GXT↔TXT 转换。
4. 【源码】内置在线 AI 翻译（MiMo / DeepSeek / 免费 Google 端点），带批次、并发、重试、占位符保护。
5. 【源码】可编辑字符映射 DAT 的码点↔行列清单，并导出 TXD 图集图片供查看。

### 不能做什么

1. 【源码】不能直接吃我们的 JSONL / TSV，也不导出 CSV/TSV/JSON；交换格式只有 TXT。
2. 【源码】无「只翻未译 / 跳过已译」开关，无术语表文件，翻译只作用于勾选行，端点与模型基本写死。
3. 【源码】不建模 `update\` 覆盖层与 base 的同键覆盖关系；每个标签页只装一个扁平 GXT。
4. 【源码】不能编辑字模位图、不能加图集外字形、不能改字宽；TXD 仅导出。
5. 【实测】根目录无 LICENSE，二进制 / 源码再分发与改造的授权未明；全量驻留、无磁盘分页，59k 键的实际流畅度未上机验证。

### 建议怎么用

1. 【推断】定位为**人工复核辅助 UI**：批量抽取、对齐、翻译、回写仍走自有脚本；仅在需要看上下文、改个别条目时打开对照。
2. 【推断】若试用，先在副本上跑通「GXT → TXT → 改 → 导回 GXT」闭环，重点核对 `0x` 前缀键是否被导入校验拦截、保存后表偏移与内联名是否一致。
3. 【推断】复用其 `IVTKEY.lst` 映射与解析思路到自有脚本；改造其 Qt 工程前先核实 LICENSE。
4. 【推断】字形 / 字宽问题另立方案，不纳入本工具链。
5. 【推断】不把它作为发布包内的依赖组件；授权与可编译性未核实前，不向最终汉化包捆绑其产物。

---

### 附：本次评估未决项（上机后补）

- 【未确定】`0x` 前缀十六进制键在 IV 导入时是否被 8 字符长度校验拦截；卡在哪：`GXTStudio.cpp:2157-2174` 与 `:3246`，需一次真实导入回归。
- 【未确定】59,634 键全量驻留下的首开 / 编辑响应；缺：本机实机打开 base `chinese.gxt` 的耗时与内存数据。
- 【未确定】`calculateGTA4Hash` 兜底哈希是否与游戏 IV 实际校验一致；缺：新增具名键在游戏内的实测命中。
- 【未确定】仓库 LICENSE 实际条款；缺：联网核实 GitHub 仓库许可页（本次按约束未联网拉取）。
