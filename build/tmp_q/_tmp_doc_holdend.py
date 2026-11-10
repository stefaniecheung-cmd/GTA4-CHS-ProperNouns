# -*- coding: utf-8 -*-
import io, shutil, os

D1 = r"C:\Game\gta4-chs\docs\润色线-进度存档.md"
D2 = r"C:\Game\gta4-chs\docs\润色流水线-已知坑.md"

sec1 = """
## 挂起项集中结案（2026-11-09 23:58）

### 一、挂起表 6 条：全部结案

关键做法：**不靠导出预览猜，改用队列 english 列 + 三语原版 gxt（american / french / german / italian / spanish）交叉定案。**

| crc | 原文实况 | 定案译文 |
|---|---|---|
| `E50E2243` | 完整：`After I've finished with them, they'll look like they've been dragged through the fucking desert.`（此前以为截断，实为预览截断） | 等我完事儿，她们会像被拖过他妈一片沙漠一样惨。 |
| `CC495487` | `Can you now?` | 你现在就能买了？ |
| `1AEDA761` | `When a book is called "Guns,`（**原文本身就在书名中途断句**，引号未闭合，下一条接后半） | 当一本书的名字叫「枪炮， |
| `96E75BE0` | `DIALOGUE MISSING`（配音缺失占位符，非台词） | 对话缺失 |
| `BBC92791` | 完整：`...and an occasional catamite,`（此前以为截断） | 啊，他是人民公仆，是个大善人，是个牛皮大王，偶尔还当个男宠， |
| `5D478FFD` | `DIALOGUE MISSING` | 对话缺失（与上条统一） |

要点：
- **6 条里有 3 条根本不是截断**，是导出预览按字数截的假象。判断方法：直接读队列 `english` 列（字段完整），或用 `parse_gxt` 读三章原版 gxt。
- `catamite` 原译「小受」改为「男宠」——圈内用语不合讽刺政客的语境。
- 两条 `DIALOGUE MISSING` 统一「对话缺失」，「丢失」改「缺失」；不必写成英文占位符（中文不影响游戏显示，且 qa 不报未译）。

### 二、语义待定 3 条

| crc | 原文 | 结论 |
|---|---|---|
| `DB14B1D9` | `E mio.` | **结案不改**：意大利语「(这)是我的」，意/法原文都保留 `E mio`，官方西语译 `Soy yo`（是我）；现译「是我。」准确 |
| `2BB5C8D7` | `Cold man.` | 改「你可真冷血。」（意 Che tristezza / 法 C'est bas / 西 Hombre frío 三语都指向责备） |
| `5B2EBAE5` | `Go. Roll the bitch!` | 改「去。把音响轰起来！」（意 Pompa il volume / 法 Fais péter le son / 西 Dale caña 都把 roll 解成「开音响」，原译「闪亮登场」无据） |

**方法论**：这三条靠三语平行官方译本定案，比查词义可靠——`roll` 在英语里歧义大，但三个译者的理解一致指向音响音量。

### 三、EULA 8 条统一口径

原文共 8 条（`4E1B5834` / `3593E024` / `4AA60BF6` / `140BB621` / `0770EBC5` / `015AE632` / `1D3BDEAC` / `60DA4833`）。统一了：

1. **删第三方署名行**：`4AA60BF6` 末尾的「~n~~n~汉化文本更新日期：2022-09-29」原文没有，按「原文没有的不许自加」删除。
2. **`Microsoft集团公司` → `Microsoft 集团旗下各公司`**：原译是把 `the Microsoft group of companies` 直拼又缺空格。
3. **`娱乐软件协会`两侧空格去掉**；**`依授权使用`补出授权方**（`经 Microsoft 授权使用`）。
4. **半角逗号统一全角**，去掉英文逗号直译残留的「, 以及」。
5. **同源两条统一**：`1D3BDEAC` 与 `60DA4833` 原文**逐字相同**，此前译文不同（用词「租赁」有无、「比赛/活动」、`~n~` 位置），现统一为同一份，且补上原译漏掉的 `rental`（租赁）。`4AA60BF6` 与 `3593E024` 原文亦逐字相同，同样统一。
6. `¬` 商标符号**保留**（原文有）；`4E1B5834` 原文是 `Take-Two Interactive Software`（无 Inc.），`0770EBC5` 原译多补的 `Inc.` 去掉。

### 四、打码与自加符号 6 条

| crc | 问题 | 处理 |
|---|---|---|
| `6AB51CC9` | 原译「〇逼」打码，原文是 `the C word`（避讳说法） | 改「那个 C 字」——保住避讳又留住 C 的指代 |
| `47E6FBE7` | 译文「小卒*」多个星号，原文 `You're only an associate Phil remember that.` 无星号 | 删星号 |
| `446D60CD` / `D0EF060D` | `sandwich maker` 误译「擀面杖」；`*` 与括注「(形似缩小的火箭)」均自加 | 改「三明治机」；删星号与括注 |
| `DCFE1114` / `9D2C1F60` | `mug tree` 译「茶杯架」可，但 `*` 与括注「(形似缩小的衣帽架)」自加；`eh -` 语气丢失 | 改「呃，厨房里那个杯架，还记得吧？」；删星号与括注 |

排查结果：全库含 `〇/○/●/＊` 打码条目**只剩 1 条**（`6AB51CC9`，已处理）。其余含 `*` 的行是原文自带（如 `WEAZL5|7DC3A773` 的 `* Protect / * Serve / * Freedom` 列表符）或垃圾邮件乱码串，均不动。

### 五、顺带发现并处理的结构问题

`zh_global.tsv` 里存在 **chapter 字段为空的旧行**，且同 crc 可能有带章新行并存。`apply_zh.load_global` 的规则是 `if not ch or ch == chapter` → 空 chapter 行**对三章都生效**，且同 crc 时**后出现的那行覆盖前面的**。

- 本次新建的 6 行是按 chapter 归属写入的，但表里原有 chapter 为空的同 crc 旧行仍在，形成重复。
- 已删除 5 行（`47E6FBE7`、`446D60CD`、`DCFE1114`、`9D2C1F60`、`D0EF060D` 的空 chapter 旧行），删前已确认每 crc 都有带章的正确替代行。
- 覆盖表备份：`assets_backup\\覆盖表_zh_global_20261109_p2hold.tsv`（1,124,536 B）。
- **存量仍有 2,209 行 chapter 为空、约 145 个 crc 重复**。这批属 P3/P4 早期遗留，是否按「全部补齐 chapter」重构一遍需用户拍板——补错会让原本跨章通用的译名被锁进单章。

### 六、数值

| 项 | 值 |
|---|---|
| `apply_zh` base / TLAD / TBoGT | 9,717 / 2,500 / 2,830 |
| `zchs_base_tr.gxt` | 2,670,666 B |
| `zchs_TLAD_tr.gxt` | 778,444 B |
| `zchs_TBoGT_tr.gxt` | 973,648 B |
| `qa_gate` | 检查 14,125 条，错误 0，警告 17 |
| `zh_global.tsv` | 13,315 行 |
| 审读日志 | 12,278 行 |

仍未部署到游戏侧（build 与 p49725 不一致）。

### 七、挂起表归档

- 已处理 9 条（8 条改 + 1 条确认原译正确）→ `data\\review\\挂起待拍板_已处理_20261109.tsv`
- 主表只留 **1 条**：跨章 crc 冲突 `62F4C1EF`（需覆盖表支持复合键，属结构性改动，待拍板）

### 备份

- `挂起待拍板.tsv.bak_before_p2hold`
- `润色线-断点.json.bak_before_p2hold`
- `assets_backup\\覆盖表_zh_global_20261109_p2hold.tsv`
"""

sec2 = """
## 坑 47：导出预览的「截断」不一定是原文截断

挂起表里三条被判「原文被截断」的条目（`E50E2243`、`BBC92791`、`1AEDA761`），逐一回读后发现：

- `E50E2243` / `BBC92791`：**原文是完整的**，只是导出预览按字数截断（`...dragged through the fuc[---]`、`and an occasional...`）。
- `1AEDA761`：`When a book is called "Guns,` —— **原文真的就在书名中途断句**（引号未闭合，下一条接书名后半）。

判据与做法：
- 别相信预览行的 `[---]（原文截断）` 标注，直接读 `上游润色_队列.tsv` 的 `english` 列（该列是完整字段），或 `parse_gxt` 读三章原版 `american.gxt`。
- 原文真断句时，译文要在**同一个断点**断开，并保留未闭合的引号形态；不要替它补全书名。

## 坑 48：覆盖表里 chapter 为空的行对三章都生效，且同 crc 是「后行覆盖前行」

`apply_zh.load_global` 的判定是 `if c and z and (not ch or ch == chapter)`，并且 `out[c] = z` 逐行赋值。

后果两条：
1. **chapter 为空的行对所有章生效**——一个想只在 base 生效的译名，会顺带作用到 TLAD / TBoGT。
2. **同 crc 出现两行时，文件里靠后的那行生效**——新写入的行追加在尾部，所以「新行」会赢；但如果手工调序或删行，胜负会反转。

本次踩到的具体事故：`fixes` 按 `chapter=TLAD` 写入 `446D60CD` 后，表里原有的空 chapter 旧行（`擀面杖…*`）依然在，形成同 crc 重复。已删 5 行重复旧行解决。

处置原则：
- 写入前先 grep 该 crc 是否已有空 chapter 行；有就**同时删旧行**，不要只加新行。
- 存量仍有 2,209 行空 chapter / 约 145 个重复 crc，属早期遗留；批量补 chapter 有把「跨章通用译名」误锁进单章的风险，需先拍板再动。

## 坑 49：三语平行官方译本是判歧义原文的硬证据

`Go. Roll the bitch!` 一条，英语里 roll 歧义极大（滚动 / 开拍 / 开音响 / 开车）。查同 crc 的意/法/西三语官方译文：`Pompa il volume` / `Fais péter le son` / `Dale caña` —— 三者一致指向「把音响放起来」，据此定案「去。把音响轰起来！」

`E mio.` 同理：意/法原文都保留 `E mio`（意大利语），西语官方译作 `Soy yo`（是我）→ 现译「是我。」正确，可以结案不改。

做法：`parse_gxt` 读同目录的 `american.gxt` / `french.gxt` / `german.gxt` / `italian.gxt` / `spanish.gxt`，按同一 crc 取同表同键对比。判歧义优先信三个独立译者的一致理解，其次信词典义。

## 坑 50：中文省略号 `…` 会被 CHAR_MAP 转成三个半角点

`apply_zh.CHAR_MAP` 把 `U+2026 …` 映射成 `...`（ASCII 三点，因为 `…` 不在图集内）。所以写「那个……」进表后，游戏里显示的是「那个......」。

- 需要停顿语气时用「呃，」「，」等替代，不要靠省略号。
- 注意 `CHAR_MAP` 同时把 `·`→`･`、`（）`→`()`、`“”`→`「」`；写 fixes 时按最终显示形态想一遍。
"""

for p, sec in ((D1, sec1), (D2, sec2)):
    shutil.copy2(p, p + ".bak_before_p2hold")
    with io.open(p, "ab") as f:
        f.write(("\n" + sec).encode("utf-8"))
    print(os.path.basename(p), os.path.getsize(p))
