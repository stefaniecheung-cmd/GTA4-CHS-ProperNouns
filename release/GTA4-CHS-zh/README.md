# GTA4 简中补丁之补丁（含 AI 翻译）v2.1

在原版汉化补丁（GTA4.CHS.asi）之上补完专有名词与整句漏译的非官方整合包，**免费 / 非商业**。覆盖本体 / TLAD / TBoGT 三章，包内自带主补丁，无需另装原补丁。

## 内容

- 主补丁 `plugins/GTA4.CHS.asi`（二进制未改动）
- 字符表 `char_table.dat`（3,624 字，含新增 44 个 CJK 用字）
- `whm_table.dat`、`custom_translations.json`（沿用原补丁）
- 三章字库图集 `fonts.wtd`
- 三章译文字典 `american.gxt`（本体 / TLAD / TBoGT）
- `plugins/mapfix.asi` 暂停地图区名修复

## v2.1 变更

- 安装脚本补齐 update 层三章字典 + 三章图集共 6 个覆盖文件，与卸载还原逐项对称。
- 回滚基底更正为英文原版：`_ORIGINAL_*` 三章 gxt + 三章图集取自未汉化基础层，卸载显式拷回还原英文；移除冗余字符表基底。
- 新增旧汉化 / 死文件扫描隔离（Windows `清理旧汉化.bat`、Linux `cleanup_old_zh.sh`），隔离不直删。
- 新增 SteamOS/Linux（Proton）一键脚本 `install.sh` / `uninstall.sh` / `cleanup_old_zh.sh`。
- 前置版本口径更新为 1.2.0.59；主补丁 asi 为第三方二进制、未改动。

## 安装（摘要）

1. 把压缩包 **解压到独立文件夹**，Windows 双击 `安装.bat`；SteamOS/Proton 在终端跑 `bash install.sh`（自动定位 Steam 库目录，不必放进游戏目录）。
2. 卸载：Windows 双击 `卸载.bat`；Linux 跑 `bash uninstall.sh`，还原到原版英文状态。
3. 装过其它旧汉化时，先跑清理脚本（Windows `清理旧汉化.bat` / Linux `bash cleanup_old_zh.sh`）隔离残留。

详见 `使用说明（必读）.txt`、`更新日志.txt`、`声明.txt`、`有意保留英文清单.tsv`。

## 声明

免费发布，仅供交流学习，**禁止任何商业用途**；不含破解、主补丁二进制未改动、不提供游戏本体。使用后果由使用者自负。
