# GTA4 三章简中汉化包 v2.1（一键移植 / 跨平台）

在民间简中补丁 `GTA4.CHS.asi` 基础上，完成三章译文字典定稿、中文字库扩容与地图区名修复的非官方整合包。**包内自带汉化补丁本体，解压安装即可，无需另装原补丁。** 覆盖本体 / 失落与诅咒 (TLAD) / 夜生活之曲 (TBoGT) 三章。免费发布，仅供交流学习，禁止任何商业用途；不含破解、不提供游戏本体。前置游戏版本 1.2.0.59。

> v2.1 工程源码与完整发布物见 `localization-v2` 分支；本仓库 fork 自 ghh-6 上游，可在网页端 Sync fork 跟随更新。Release 见 [v2.1](https://github.com/stefaniecheung-cmd/GTA4-CHS-ProperNouns/releases/tag/v2.1)。

## v2.1 变更（相对 v2.0）

- **安装脚本补齐 update 层 6 个覆盖文件**：三章 `american.gxt` + 三章 `fonts.wtd`，与卸载还原逐项对称。
- **回滚基底更正为英文原版**：`_ORIGINAL_*` 三章 gxt + 三章图集取自未汉化基础层，卸载显式拷回还原英文；移除冗余字符表基底。
- **新增旧汉化 / 死文件扫描隔离**：Windows `清理旧汉化.bat` / `.ps1`、Linux `cleanup_old_zh.sh`；残留字典 / 图集 / 汉化索引先隔离到 `_chs_old_isolated_<时间戳>/`，不直删并附清单；原版多语、我方 `american*` 字典与 `fonts.wtd`、其它图形/玩法 MOD 不误伤。
- **新增 SteamOS / Linux（Proton）一键脚本**：`install.sh` / `uninstall.sh` / `cleanup_old_zh.sh`，与 Windows 包同套文件、同构目录，自动定位 Steam 库。
- 主补丁 `GTA4.CHS.asi` 为第三方二进制、未改动；源于该 asi 自身的问题需等上游更新。

## 包内内容（29 条目）

- `plugins/GTA4.CHS.asi` —— 汉化补丁主程序（二进制未改动）
- `plugins/GTA4.CHS/char_table.dat` —— 允许字符表（3,624 字，含新增 44 个 CJK 用字）
- `plugins/GTA4.CHS/whm_table.dat`、`custom_translations.json` —— 沿用原补丁
- `plugins/mapfix.asi` —— 暂停地图区名修复
- `update/pc|TLAD|TBoGT/...` —— 三章字库图集 `fonts.wtd` 与译文字典 `american.gxt`
- 6 件 `_ORIGINAL_*` 英文原版基底（卸载回退用）
- Windows / Linux 安装、卸载、清理脚本；使用说明 / 更新日志 / 声明 / 有意保留英文清单

## 安装 / 卸载（摘要）

1. 把 zip 解压到**独立文件夹**（不要解压进游戏目录）。
2. Windows 双击 `安装.bat`；SteamOS/Proton 终端跑 `bash install.sh`。
3. 卸载：Windows `卸载.bat`；Linux `bash uninstall.sh`，还原到原版英文状态。
4. 装过其它旧汉化时，先跑清理脚本隔离残留。

## 校验信息

- 附件：`GTA4-CHS-zh-v2.1.zip`
- 大小：14,259,062 B
- MD5：`244b795d3375b2b81c27f9ff69a7ae21`
- SHA256：`d5bd918fe6ab5c4858ac76d65f1f6ef990157ec5f79fe8b6c8b9d1f2f6a3309a`

## 翻译口径

主角 Niko、Roman 相关称呼保留英文；人名 / 地名 / 昵称 / 任务赛道名译，界面菜单、纯多人独占、制作名单、真实人物与品牌名不译；需照抄键入的姓名字段保留英文；控制码随原文守恒。

## 声明

本补丁为非官方同人修改，与 Rockstar Games / Take-Two Interactive 无任何关联；仅供交流学习、免费分发，不重新打包原补丁、不自称官方汉化、不收费、不引入破解；原补丁署名与声明已逐字保留。使用后果由使用者自负。