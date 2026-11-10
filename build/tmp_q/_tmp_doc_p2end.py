# -*- coding: utf-8 -*-
import io, shutil, os

D1 = r"C:\Game\gta4-chs\docs\润色线-进度存档.md"
D2 = r"C:\Game\gta4-chs\docs\润色流水线-已知坑.md"

sec1 = """
## P2 队列收尾（2026-11-09 23:40）

P2 = 1,113 条（TBoGT|MAIN 的 Email / 短信长句，含缩写、俚语、`xx` 签名）。从 0 起按每批 100 条推进（末批 113 条），共 12 批。

### 构建读数（P2 全部落表后）

| 项 | 值 |
|---|---|
| `apply_zh` base | 9,709 条 |
| `apply_zh` TLAD | 2,497 条 |
| `apply_zh` TBoGT | 2,826 条 |
| `zchs_base_tr.gxt` | 2,670,198 B（524 表 / 59,661 条，逐条比对不一致 0） |
| `zchs_TLAD_tr.gxt` | 778,434 B |
| `zchs_TBoGT_tr.gxt` | 973,622 B |
| `qa_gate` | 合计：检查 14,109 条，错误 0，警告 17 |
| 审读日志 | 12,254 行 |
| `zh_global.tsv` | 13,304 行（不含表头） |

17 条警告仍全是既有多换行常驻豁免（拍板 B3 不改）。

### 断点值

- `p2{total 1113, offset_done 1113, remaining 0, next_from 1114}`
- `passed_offset 58157`、`remaining 0`
- `counts{zh_global_rows 13304, review_log_rows 12254, qa "合计：检查 14109 条，错误 0，警告 17"}`
- `build{applied {base 9709, TLAD 2497, TBoGT 2826}, gxt_base_tr 2670198, deployed false}`
- 写入时间戳 `2026-11-09 23:40:00`；`notes_log` 追加 offset 1113 一条
- 备份 `润色线-断点.json.bak_before_p2end`

### 部署状态

**未部署**。游戏侧仍是 p49725（base 2,669,910 / TLAD 778,430 / TBoGT 973,552），build 与游戏侧不一致：base 差 40,288 B，TLAD 差 4 B，TBoGT 差 70 B。`deploy.txt` 未追加 P2 记录。

### P2 段集中修正的语义类型

1. **Niko / Nicky / Niko boy / Nicky boy → 「尼克」**，本段共 60+ 条（`1A18D884`、`468C7256`、`3040169E`、`36EBA91D`、`A360A35B`、`D37EFAB8`、`0D4F2C21`、`545AD7CB`、`8DC44A9D`、`CAC6DAF7` 等）。
2. **`cousin` → 「堂弟」**，原译「堂兄」全部改正（`0BDB49AD`、`7AFC1039`、`F4DE0F7B`、`8DC44A9D`、`0907366D`、`BFAA142A`）。
3. **车型专名保留英文**：`Karin Dilettante`（原译「Karin 半吊子」/「Kirin 半吊子」，`A22DE81F`、`04A0ACE8`）、`Turismo`（原译「远途」，`E76C1C27`）。
4. **专名不意译**：`Playboy X`（原译「花花公子」，`C4CD5B35`）。
5. **UI 按键名并置缺连接词**：原文 `~PAD_LEFT~ and ~PAD_RIGHT~` 被译成 `~PAD_LEFT~~PAD_RIGHT~`，中文缺「和/或」。本段集中修 20+ 条（`AF48013E`、`D16B4584`、`DE1BE189`、`104CF09E`、`75C2D709`、`A1220845`、`042B0B7E`、`DEB64095`、`FDF87F19`、`56ECAEFE`、`D585B63F`、`E86F200A`、`11F4F816`、`22492C46`、`322CF8C7`、`41CF96C1`、`618FCDC3`、`41034C6C`、`9BD783C6`、`DAF046C8`、`CCB22A4C`）。
6. **`leave X` 漏译宾语**（试衣间「不买这件离开」）：鞋/帽/眼镜/衣/裤子共 8 条（`104CF09E`、`75C2D709`、`A1220845`、`042B0B7E`、`DEB64095`、`FDF87F19`、`56ECAEFE`、`D585B63F`、`E86F200A`、`F50BA9C6`、`F84D9348`）。
7. **`skip at extra cost` / `skip` 被一律译成「跳过动画」**：实为「跳过这段行程」，共 7 条（`83A2478B`、`2FC9CC29`、`A6FD0E40`、`2FC9CC29`、`5950208D`、`115F90AD`、`4BFC85E6`、`698ABFB2`）。
8. **原文没有的自加内容**：`885AD568` 自加「但将无法解锁成就」；`9AC78535`/`3317050A`/`93930840` 自加「桌面右下角」；`CCB22A4C` 自加 `~n~`。
9. **短信口语接反**：`0806`（priciest vibrator 句）、`0870`（anti-climax 译「渐渐衰亡」）、`0717`（`ain't got no one else who wants 2 hang` 译「没有别人好找了」）、`204BC596`（"I'd rather you fucked a thousand men" 译「横扫千军…风情万种」）、`C569CE23`（`mean colors` 译「成色不太好」）。
10. **打码条目转正**：`8CE49EAA` 原译「打爆他的〇〇蛋」，按原文直译去掉 `〇`。

### 本段新增的三条坑（已同步写入 `润色流水线-已知坑.md`）

- fixes 正文以 `~z~~x~` 开头会被 `fix_ctrl` 再套一层，必须剥掉开头标签；`safe_append` 的「剥离开头重复标签」只处理重复，不处理单层。
- 按键名并置（`~A~~B~`）在中文里必须补「和 / 或」，否则读不成句；但不得为此增删标签本身。
- `skip` 的宾语是「这段行程」，不是「动画」；同一批里 `holding/pressing` 也要分别译「长按 / 按」。

### 备份清单

- `润色线-断点.json.bak_before_p2end`
- `润色线-进度存档.md.bak_before_p2end`
- `润色流水线-已知坑.md.bak_before_p2end`
"""

sec2 = """
## 坑 44：fixes 正文不能以颜色标签开头（P2 段复现）

写 fixes 时若把原文开头的 `~z~~x~` 原样带到「新译正文」里，`fix_ctrl` 会再补一层，触发 `E [控制符]`。

- `safe_append.py` 打印的「剥离 N 处开头重复标签」只处理**重复**标签（`~z~~z~`），**不处理单层**。
- 正确做法：新译正文只写纯文本，开头标签交给 `fix_ctrl` 按原文补；落表前用一段字符串 replace 自查一遍。
- 本段 `0301` 批（`268103EA` / `269D16C4` / `2C97F610`）就是先踩再当场剥掉的。

## 坑 45：按键名并置必须补「和 / 或」，但不得增删标签

原文 `Use ~PAD_LEFT~ and ~PAD_RIGHT~ to browse shoes.` 逐字直译成 `用~PAD_LEFT~~PAD_RIGHT~浏览鞋子` 后，中文读不成句（两个标签直接贴在一起）。

- 判据：英文里用 `and` / `or` / `+` 连接两个键名，中文对应位置就要有「和」/「或」。
- 但补的是**连接词**，不是标签：标签数量、顺序、颜色码一律照原文，不许加 `~s~` 分隔。
- 同类还有 `~INPUT_VEH_EXIT~/~INPUT_PICKUP~` 后面 `leave X` 的宾语（「不买鞋离开」），漏了宾语就成了「离开」。

## 坑 46：`skip` 的宾语是「这段行程」

带司机 / 出租车的 UI 文案里 `Press ACCEPT to skip` / `to skip at extra cost` 指的是**跳过这段路上行程**，不是跳过动画。本段一次性修了 8 条「跳过动画」（`83A2478B`、`A6FD0E40`、`5950208D`、`115F90AD`、`4BFC85E6` 等）。

- 同一批里 `holding ~X~` 与 `pressing ~X~` 也要分开译「长按 / 按」，原译一律写成「长按」（`B8D3F4D5` 对照 `04B93AC0`）。
"""

for p, sec, tag in ((D1, sec1, "进度存档"), (D2, sec2, "已知坑")):
    shutil.copy2(p, p + ".bak_before_p2end")
    with io.open(p, "ab") as f:
        f.write(("\n" + sec).encode("utf-8"))
    print(tag, os.path.getsize(p))
