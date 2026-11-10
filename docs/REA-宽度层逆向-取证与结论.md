# REA 逆向：旧汉化 `GTA4.CHS.asi` 的 hook 手法与宽度层机理

> 取证：2026-11-08 23:04 – 23:45
> 工具：REA 6.8.0 + Ghidra 12.1.4（Administrator）+ JDK 21
> 目标：`C:\Game\_tools\chs_re\GTA4.CHS.asi` 232,960 B / SHA256 `9437fe10…61588` / ImageBase `0x10000000` / 1,296 函数
> 方法：`rea analyze` → `rea decompile-all`（全部 1,296 函数伪代码落盘）→ 本地全文检索 + 二进制扫描

---

## 一、一句话结论

旧汉化**不是**逐个手写偏移去 hook，而是照抄了一份 **`gta_benchmark` / `gta_font` / `gta_game` / `gta_html` / `gta_mail_reply` 五模块源码的 C++ 框架**：每模块 `register_patches(batch_matching&)` 注册一批 lambda，每个 lambda 带一条**特征码字符串**，运行时用 pattern 在 `GTAIV.exe` 里批量匹配出所有命中地址（`std::vector<memory_pointer>`），再对每个地址写 5 字节 `E9 rel32` 装成自己的 handler。

**29 条特征码字符串完整躺在 `.rdata` 里，可以直接抄。**

---

## 二、源码结构（Ghidra 从 RTTI 恢复，非推测）

伪代码里直接显示了 MSVC 的 `std::_Func_impl_no_alloc<...>::vftable` 符号：

```cpp
std::_Func_impl_no_alloc<
  'void __cdecl gta_font::register_patches(batch_matching&)'::`2'::<lambda_6>,
  void,
  std::vector<memory_pointer, std::allocator<memory_pointer>> const&
>::vftable
```

由此得到五个模块与 patch 数量：

| 模块（命名空间） | patch 数量 | lambda 编号范围 |
|---|---|---|
| `gta_benchmark` | 1 | λ1 |
| **`gta_font`** | **14** | λ1 – λ14 |
| `gta_game` | 18 | λ1 – λ18 |
| `gta_html` | 7 | λ1 – λ7 |
| `gta_mail_reply` | 9 | λ1 – λ9 |

关键类型：
- `batch_matching` —— 批量特征码匹配器
- `memory_pointer` —— 地址包装
- `std::vector<memory_pointer> const&` —— 匹配结果集，作为 lambda 的入参

→ **一个 patch = 一条特征码 + 对每条命中的安装动作**。`gta_font` 用了 14 条，说明字体层需要 14 处干预。

---

## 三、安装器三件套（已反编译核对）

### 3.1 `FUN_10007680`（164 B）— 通用 inline hook 安装器

```c
undefined4 *FUN_10007680(undefined4 *slot, undefined1 *target, int handler, uint len)
{
  FUN_10006fd0(slot, target, len);                  // 读/备份原跳转
  if ((len & 0xff) == 0) { *target = 0xE9; }
  else {
      VirtualProtect(target, len & 0xff, 0x40 /* PAGE_EXECUTE_READWRITE */, &old);
      *target = 0xE9;
      VirtualProtect(target, len & 0xff, old, &x);  // 立即还原
  }
  FUN_100072d0(target + 1, handler, 4, len & 0xff); // 写 4 字节 rel32
  return slot;
}
```

- 写的是标准 5 字节 `E9 rel32`
- `VirtualProtect` 是**页粒度**，所以 `len=1` 实际也能写满 5 字节
- 恢复原保护属性是立即的，不能靠页已 RWX 绕过

### 3.2 `FUN_10006fd0`（320 B）— 取/备份原跳转

三种情形：
- 目标已是 `E8`/`E9` → 解析出跳转目标（防重复 hook）
- 目标已是 `FF15`/`FF25` → 读出指针
- 其它 → 返回 0

### 3.3 `FUN_100072d0` — 写 rel32 偏移

---

## 四、三处安装点（不是六处）

二进制实测：`FUN_10007680` 仅被 3 条 `call` 引用（0x100079A0 / 0x100079CD / 0x10007B9D），对应三个薄封装：

| 安装函数 | 大小 | 全函数体 | target | handler | len |
|---|---|---|---|---|---|
| `FUN_10007980` | 43 B | `FUN_10007680(&p, *(int*)*p + (-6), 0x10006210, 1)` | `*(int*)*p - 6` | `0x10006210` **测宽** | 1 |
| `FUN_100079B0` | — | `FUN_10007680(&p, *(void**)*p, 0x100061A0, 1)` | `*(void**)*p` | `0x100061A0` | 1 |
| `FUN_10007B80` | — | `FUN_10007680(&p, *(void**)*p, 0x10006A90, 1)` | `*(void**)*p` | `0x10006A90` | 1 |

> **推翻**：早前「6 个安装点」的说法。`0x100079A0` 与 `0x10007C30` 是同一模板的重复书写（`call → add esp,0x10 → ret 4` + 6 字节 `cc` 填充），不是独立点。

三个安装函数本身**没有任何 call 引用**，它们被放进一张 **C++ 对象表**（见下节）里，靠 `std::function` 机制被调用。

---

## 五、patch 描述表（`.rdata`）

表项 **28 字节（7 DWORD）**，共 **62 项**，位于 `.rdata` `0x10027638` – `0x10027Bxx` 区段（另有第二批在 `0x10027BC8` 起）。

单项布局：

| 偏移 | 内容 | 说明 |
|---|---|---|
| `+00` | `0x10007600` | 固定；`void __thiscall (void* this, char)` → 条件调用 `FUN_1001d4b5` |
| `+04` | `0x10007630` | 固定；`int __fastcall (int)` → `return p + 4` |
| `+08` | `0x1002E0xx` | 指向参数/描述块（递增） |
| `+0C` | `0x100078xx` | lambda 的 `vftable` 构造器 |
| `+10` | 同 `+0C` | 重复 |
| `+14` | `0x10007B80` 等 | **安装执行器** |
| `+18` | `0x10007Dxx` | lambda 的 `RTTI_Type_Descriptor` getter |

例（第 06 项，`0x10027880`）：

```
0x10007600 | 0x10007630 | 0x1002E020 | 0x10007880 | 0x10007880 | 0x10007B80 | 0x10007D10
```

对应 `gta_font::register_patches` 的 `lambda_6`：构造器 `FUN_10007880`（`*p = ...lambda_6...::vftable`）、安装器 `FUN_10007b80`（handler `0x10006A90`）、RTTI getter `FUN_10007d10`。

---

## 六、29 条特征码字符串（全部现成，可直接复用）

位于 `.rdata` `0x100276E0` – `0x10028448`，格式为空格分隔的十六进制字节，`?` 为通配。

```
0x100276E0  83 C0 E0 50 E8 ? ? ? ? D9 5C 24
0x10027700  6A 01 57 E8 ? ? ? ? D9 5C 24 30
0x10027720  EB 12 6A 01 57 E8 ? ? ? ? D9 5C 24 24
0x10027748  F3 0F 11 0C 24 E8 ? ? ? ? 8B 35
0x10027768  E8 ? ? ? ? 6A 01 57 E8 ? ? ? ? D9 5C 24 30
0x10027794  8B CE 50 E8 ? ? ? ? 80 3D ? ? ? ? 6A
0x10027984  8B 3D ? ? ? ? 8B 68 04 8B 30
0x100279A4  C7 45 00 ? ? ? ? C7 45 44 00 00 00 00
0x100279CC  83 3D ? ? ? ? ? 8B 01 0F 44 C2 89 01 B0 01 C2 08 00
0x10027A00  A1 ? ? ? ? 80 7C 24 08 00
0x10027A1C  0F B6 84 08 ? ? ? ? 66 0F 6E C0
0x10027A3C  F3 0F 59 05 ? ? ? ? 88 4C 24 12
0x10027A5C  8D AE ? ? ? ? 32 C0
0x10027A70  81 3D ? ? ? ? AD 7F 33 31
0x10027A8C  F3 0F 11 05 ? ? ? ? 66 0F 6E 84 24 AC 00 00
0x10027AB8  A1 ? ? ? ? 83 F8 FF 75 1E
0x10027AD4  83 EC 30 83 3D ? ? ? ? FF
0x10027AFC  8A 0D ? ? ? ? 0F B6 D1
0x10027E40  03 C3 57 50 68 ? ? ? ? E8
0x10027E5C  80 3D ? ? ? ? 6A F3 0F 10 05
0x10027F84  E8 ? ? ? ? 8D 44 24 08 50 56 E8
0x100280E4  C6 84 10 ? ? ? ? 3F
0x100280F8  56 50 68 ? ? ? ? E8
0x10028270  B9 ? ? ? ? F3 0F 11 44 24 54 E8
0x10028290  6A 00 68 ? ? ? ? F3 0F 58 44 24 20 F3 0F 11 44 24 4C
0x100282C8  6A 00 68 ? ? ? ? B9 ? ? ? ? F3 0F 11 44 24 20
0x100283F4  68 80 00 00 00 8D 44 24 50 50 68 ? ? ? ? E8
0x10028420  FF 35 ? ? ? ? E8 ? ? ? ? 83 C4 0C 50 E8
0x10028448  6A 3C 05 ? ? ? ? 50 68 ? ? ? ? E8
```

**最值得注意的第一条** `83 C0 E0 50 E8 ? ? ? ?` = `add eax,-0x20; push eax; call rel32` —— 这正是引擎测宽里 `FUN_10006120(ch - 0x20)` 那一句的形态（`sub` 用 `add eax, -0x20` 实现）。也就是说旧汉化**直接从测宽函数内部那一条指令切进去**，而不是替换整个函数。

---

## 七、宽度层机理：为什么汉字只有 3.1 px

### 7.1 测宽入口 `FUN_10006210`（892 B）

签名 `float10 __cdecl (ushort* str, char, char)`。逐 UTF-16 字符循环：

- `0x20`（空格）/ 普通字符 → `FUN_10006120(ch - 0x20)` 累加行宽
- `0x7E / 0x807E`（`~`）→ `FUN_10006b50` 解析标签
  - id 落在 `0x100–0x12C`（45 个颜色类）→ `DAT_10037b04 - 0x3FC + id*4` 取字宽 × 字体缩放
  - 其它 → `FUN_1000bee0` / `FUN_10006ae0`
  - `id > 999` 再补 `*DAT_10037afc`
- 标签内 `0x6E`（`n`，`~n~`）→ `max` 后当前行宽归零

返回**最长行宽**。

### 7.2 单字宽 `FUN_10006120`（127 B）—— 症结

```c
float10 FUN_10006120(uint ch)              // 调用方传 ch - 0x20
{
  if (FUN_10001d50((ch & 0xffff) + 0x20))               // 即 (ch+0x20) < 0x100
      return FUN_10006b20(&DAT_10037ad8, ch);           // 虚函数 (*(this+0x38))(ch) → 原始测宽

  f = FUN_10006b40(&DAT_10037ad8) & 0xff;               // 字体号
  return ((字宽表[ fontRec[0x28+f*0x48]*0x96 + fontRec[0x29+f*0x48] ] + 31.0)
          / *DAT_10037b00
          + fontRec[0x34+f*0x48])
         * fontRec[4+f*0x48];
}
```

`FUN_10001d50` 只有 12 字节：`return x < 0x100`。**它判的是 ASCII 半角区，不是汉字。**

→ 非 ASCII（全部汉字、全角标点）走兜底分支，而该分支**表达式里没有 `ch` 参与**，索引来自字体记录的两个字节字段。于是任何汉字都得到**同一个常量 advance**。

与真机日志 `chs\logs\fontdbg.txt`（2026-11-08 20:32:15）一致：4 个不同字形（idx 3114 / 3574 / 1630 / 1918），`Δx` 全部精确 **3.1186 px**，与字形无关；`Δy` 恒 −16.998 px（高度轴正常）。

### 7.3 字体记录（ASI 侧，步长 0x48）

| 偏移 | 用途 |
|---|---|
| `+0x04` / `+0x0C` | 宽度乘数（scale） |
| `+0x25` | 字宽表列参数（`FUN_100060A0`） |
| `+0x28` | 字宽表主索引（×0x96） |
| `+0x29` | 字宽表次索引 |
| `+0x2C` / `+0x34` | 额外加数 |

> 与 GTAIV 引擎侧 `fontRec + 0x240`（贴图槽）/ `+0x248`（U 除数 512）/ `+0x24C`(40.0) / `+0x250`(4.0) / `+0x254`(39.5) **不是同一套结构**，不要混用偏移。

### 7.4 三个 handler 的定位

| handler | 是否为函数入口 | 说明 |
|---|---|---|
| `0x10006210` | **是**（`FUN_10006210`，892 B） | 测宽主体 |
| `0x100061A0` | **否** | 落在 `FUN_10006120`（0x10006120–0x1000619E）之后的空隙 |
| `0x10006A90` | **否** | 落在 `FUN_10006a2d`（…–0x10006a87）与 `FUN_10006ad0` 之间的空隙 |

后两个只被数据引用、没有 call 引用，所以 Ghidra 不把它们识别成函数入口。**这是「跳到函数中间一条指令」的典型形态**，与第 6 节第一条特征码 `83 C0 E0 50 E8` 对得上。

---

## 八、给自研补丁的落地结论

1. **特征码不用自己造**：旧汉化 29 条 pattern 全在 `.rdata`，直接拿来用，命中语义已经被它验证过。
2. **hook 手法照抄即可**：`VirtualProtect(PAGE_EXECUTE_READWRITE)` → 写 `E9 rel32` → 立刻还原 → 备份原字节。不需要 IAT / VTable / 注入。
3. **宽度必须单独接管**：只重定向贴图与 UV 不够，非 ASCII 永远拿常量 advance。要 hook 的是**引擎侧测宽**（`0x91C7C0`，路径 B 在 `0x921537` 调用），不是 ASI 自己的逻辑。
4. **从函数中间切入是对的**：旧汉化那条 `add eax,-0x20; push eax; call` 就是在单字宽函数内部切，比替换整个函数风险小、躲开 prologue。
5. **`gta_font` 需要 14 处干预**，我们目前只覆盖了 1–2 处。宽度只是其中一环，UV 基址、贴图指针、字符表各占几处。
6. **汉字 advance 必须与图集格位一致**：当前 4096² / 128 列 / 每格 32 px，理论 advance 应按 `32 / 该字体 scale` 推导，不能拍数字。
7. **不要动 `[esp+XX]` 偏移**。宽度槽正确值是 `[esp+28h]`，且引擎原值本来就是 4.0/512（= 我们写的 32/4096），该写操作是 no-op，与「文字消失」无关。

---

## 九、仍未查清（下一窗口起点）

- **`0x100061A0` / `0x10006A90` 两个 handler 的具体语义**：它们只被数据引用，需要用字节反汇编（`rea instructions`）从这两个地址往下读，判断是「测宽变体」还是「UV / 贴图」。
- **每个 lambda 捕获的是哪条 pattern**：lambda 对象的捕获区在运行时构造，静态里对应 `0x1002E0xx` 那批描述块，需逐块解。
- **`0x10007600` / `0x10007630` 两个固定字段的真身**：前者 `__thiscall (void*, char)` 条件调用 `FUN_1001d4b5`；后者 `__fastcall (int) → p+4`。疑为 `std::function` 基类虚函数/迭代器辅助。
- **`batch_matching` 的匹配实现**：特征码如何解析（`?` 通配处理、命中偏移回填）。

---

## 十、环境与复跑

```powershell
$env:JAVA_HOME = "C:\Game\_tools\jdk\jdk-21.0.13+9"
$env:GHIDRA_INSTALL_DIR = "C:\Game\_tools\ghidra_12.1.4_PUBLIC"
$env:PATH = "$env:JAVA_HOME\bin;C:\Game\_tools\node24;C:\Game\_tools\npm-global;" + $env:PATH
# 必须 Administrator 启动（否则 native 自检报 DACL Win32 5）
```

- 每次 `rea` 调用都重新导入分析（Program ephemeral），单次 37–45 s
- **全量导出一次搞定**：`rea decompile-all <asi> --output <dir> --layout address`，1,296 函数 54 秒完成，产物在 `<dir>\functions\<VA>.c`（**目标目录必须不存在**，否则报 `Output directory already exists`）
- 输出结构因命令而异，取值前先 `Get-Member`

---

## 十一、取证文件索引

`C:\Game\_tools\`

| 文件 | 内容 |
|---|---|
| `_dl\dec_all\functions\*.c` | **全部 1,296 函数伪代码**（本地检索主力） |
| `_dl\dec_all\decompile-index.json` / `decompile-journal.jsonl` | 导出清单 |
| `_dl\rea_dc_installer_10007680.json` | 安装器 |
| `_dl\rea_dc_handler_10006210.json` | 测宽 handler |
| `_dl\rea_dc_handler_10006120.json` | 单字宽 |
| `_dl\rea_dc_handler_100060A0.json` | 单字宽变体 |
| `_dl\rea_d2_is_cjk_10001d50.json` | `return x < 0x100` |
| `_dl\rea_d2_cjk_width_10006b20.json` | 虚函数转发 |
| `_dl\rea_d2_saveorig_10006fd0.json` | 原跳转读取 |
| `_dl\rea_asi_analyze.json` | ASI 概览 |
| `_dl\rea_search_*.json` | GTAIV 地址硬编码扫描，**全 0 命中** |
| `_rea_decompall.ps1` / `_rea_asi_decomp.ps1` / `_rea_asi_cjk.ps1` | 提权取证脚本 |
| `p4_scan_calls.py` | 扫 `E8/E9` 调用目标 |
| `p4_dump_table.py` | patch 表解析 |
| `p4_sigs.py` | **特征码提取** |

---

*本文档所有结论均来自反编译伪代码与二进制实测。凡标注「未查清」的，均未推测填充。*
