# -*- coding: utf-8 -*-
"""生成发布包文档：使用说明 / 更新日志 / 声明 / README + 有意保留英文清单。
txt 为 UTF-8 BOM + CRLF；README.md 为 UTF-8 LF。"""
import os, shutil, csv, io

REL = r"C:\Game\gta4-chs\release\GTA4-CHS-zh"
DATA = r"C:\Game\gta4-chs\data"

def wtxt(name, text):
    p = os.path.join(REL, name)
    crlf = text.replace("\n", "\r\n")
    with open(p, "wb") as f:
        f.write(b"\xEF\xBB\xBF" + crlf.encode("utf-8"))
    print(name, len(crlf.encode("utf-8")), "B (BOM+CRLF)")

def wmd(name, text):
    p = os.path.join(REL, name)
    with open(p, "wb") as f:
        f.write(text.encode("utf-8"))
    print(name, len(text.encode("utf-8")), "B")

USAGE = """============================================================
  GTA4 三章简中汉化包 — 使用说明（必读）
============================================================

【这是什么】
在简中补丁（GTA4.CHS.asi，无名汉化组立项、GTA4 贴吧吧友接手完成）基础上，
替换三章译文字典、扩容中文字库，并附带地图区名修复插件。覆盖三章：
本体 / 失落与诅咒(TLAD) / 夜生活之曲(TBoGT)。本包自带主补丁本体，
无需另装原补丁。

【前置条件（重要）】
1. 游戏：GTA4 完整版 1.2.0.59（三合一）。
2. 本包已包含汉化补丁 GTA4.CHS.asi 及其数据文件夹，解压安装即可，
   不需要再单独下载原补丁。

【安装】
0. 把压缩包解压到一个【独立文件夹】（不要解压进游戏目录、也别把文件合并进去）。
1. 确认游戏与 Steam 没有在运行。
2. （仅目标机器装过其它旧汉化 / 老版汉化包时）先双击 清理旧汉化.bat：
   扫描疑似旧汉化 ASI、数据目录、外置字库，以及基础层与 update 层的残留
   字典 / 图集 / 汉化索引（chinese.gxt、fonts_chs.wtd、content_chs.dat 等），
   列出清单后经你确认再隔离到游戏目录旁的隔离文件夹（不直接删除，可随时拷回）。
3. 双击 安装.bat —— 自动定位游戏本体（依次尝试：补丁文件夹相对位置 →
   Rockstar 注册表 → Steam 注册表与库列表），不要求把本文件夹放进游戏目录。
4. 看到「[完成] 全部文件安装成功」即成功；全部提示为中文。
5. 启动游戏。
安装时复制主补丁 GTA4.CHS.asi 与 plugins\\GTA4.CHS 数据文件夹（字符表 +
whm_table.dat + custom_translations.json），覆盖三章字库图集与译文字典，
并安装 plugins\\mapfix.asi。包内 _ORIGINAL_* 为英文原版基底（三章译文字典 +
三章字库图集，共 6 个），供卸载时把 update 层显式还原成英文原版；字符表属
补丁数据目录，卸载随整个 plugins\\GTA4.CHS 删除，不另留基底。

【跨机器 / 备份目录移植】
- 先核对目标游戏版本与本包一致（三合一完整版）；版本不同不要直接铺。
- 推荐顺序：先跑 清理旧汉化.bat 隔离旧汉化残留 → 进游戏确认是干净英文原版、
  能读档 → 再跑 安装.bat → 进游戏抽查本体 / TLAD / TBoGT 菜单、字幕、手机网页。
- 本包只动上表列出的 plugins 与 update 文件；原版多语言 gxt、我方 american*
  字典与 fonts.wtd、update\\GTA IV 资源套及其它图形 / 玩法 MOD 不会被清理脚本误伤。
- 隔离目录为游戏目录下 `_chs_old_isolated_<时间戳>`，含《隔离清单.txt》
  （归类 / 相对路径 / 大小 / MD5 前 12 位）；确认新补丁显示正常后再手动删除。

【SteamOS / Linux（Proton 跑 Windows 版）】
- 前提：游戏为 Steam 安装的 Windows 版、经 Proton 运行；且 Windows 版
  ASI/ScriptHook 加载器（FusionFix / dinput8 那套）已在 Proton 下装好并能加载
  .asi。本包数据资产与 asi 文件与 Windows 版完全相同，只是安装脚本换成 bash。
- 在解压目录的终端里依次执行（无需 chmod，直接用 bash 调起）：
    1. 先清旧汉化：`bash cleanup_old_zh.sh`（预览清单，确认后输入 Y 隔离；
       加 `--apply` 可跳过询问直接隔离）。
    2. 安装：`bash install.sh`；卸载：`bash uninstall.sh`。
- 脚本自动扫描桌面版与 Flatpak 版 Steam 库目录及 libraryfolders.vdf 多库；
  定位不到时手动指定：`GTA4_DIR=/路径/到/Grand\\ Theft\\ Auto\\ IV bash install.sh`。
- 游戏目录在 Linux 文件系统的 Steam 库内（如
  `~/.local/share/Steam/steamapps/common/Grand Theft Auto IV`），Proton 直接读取，
  不要把文件拷进 compatdata 的 wine prefix。
- 限制：若为 Linux 原生移植（非 Proton），PE 格式 .asi 无法被原生进程加载，
  本包的 asi 与 hook 链不适用；数据资产能否被原生版读取需另行验证。

【卸载 / 回退】
双击 卸载.bat：用 _ORIGINAL_* 英文原版基底，把 update 目录的三章字库图集与
译文字典逐项拷回还原为英文原版，再删除主补丁 GTA4.CHS.asi、
plugins\\GTA4.CHS 数据文件夹（含字符表）与 mapfix.asi，回到干净的英文原版状态，
其它图形 / 玩法 MOD 不受影响。请勿删除文件夹里的 _ORIGINAL_* 文件。

【本包内容】
  安装.bat / 卸载.bat                  Windows 安装与回退（自动定位游戏目录）
  清理旧汉化.bat / 清理旧汉化.ps1      Windows 扫描隔离其它旧汉化补丁与死文件（不直删）
  install.sh / uninstall.sh / cleanup_old_zh.sh  Linux/SteamOS(Proton) 对应脚本
  plugins\\GTA4.CHS.asi                 汉化补丁主程序（二进制未改动）
  plugins\\GTA4.CHS\\char_table.dat    允许字符表（3,624 字，含新增 44 个 CJK 用字）
  plugins\\GTA4.CHS\\whm_table.dat      游戏内网页译文替换表（沿用原补丁）
  plugins\\GTA4.CHS\\custom_translations.json  补丁设置项覆盖（沿用原补丁）
  plugins\\mapfix.asi                   暂停地图区名修复插件
  update\\pc\\textures\\fonts.wtd       本体字库图集
  update\\TLAD\\pc\\textures\\fonts.wtd 失落与诅咒字库图集
  update\\TBoGT\\pc\\textures\\fonts.wtd 夜生活之曲字库图集
  update\\common\\text\\american.gxt    本体译文字典
  update\\TLAD\\common\\text\\american.gxt 失落与诅咒译文字典
  update\\TBoGT\\common\\text\\american.gxt 夜生活之曲译文字典
  _ORIGINAL_* ×6                        卸载回退基底（英文原版：三章 gxt + 三章图集）
  声明.txt / 更新日志.txt               版权免责 / 版本记录
  有意保留英文清单.tsv                   按口径保留英文的条目与原因

【翻译口径】
- 主角 Niko、Roman 相关称呼按口径保留英文。
- 人名 / 地名 / 昵称 / 任务赛道名译；界面菜单、纯多人独占内容、制作名单、
  真实人物与品牌名不译。
- 需要玩家照抄键入的姓名字段保留英文，关键提示句为中英双语。
- 对白粗口按口语中译；控制码（~z~ ~n~ ~s~ 等）随原文保留，不改配色。

【已知事项】
- 主补丁 GTA4.CHS.asi 为第三方二进制、本包未改动；若出现源于该 asi 自身的
  问题（卡顿、接口行为等），需等上游汉化补丁更新 asi 文件，本包只交付翻译数据资产。
- 商标与重音符号（™ ¬ ® © 　 ／ 以及 é á ç 等拉丁重音）先走原生拉丁字体；
  若真机显示为方块/问号，再另行收进中文字库。
- 中文为固定等宽排版，所有汉字同一字宽，新增 44 字与旧字同宽，不存在
  按字取宽或回退全角宽的问题；whm_table.dat 是游戏内网页的整串译文
  替换表，与单字渲染无关，无需为新字改动。

【常见问题】
1. 安装.bat 提示「未能自动定位游戏本体」
   → 把本文件夹放进 GTA4 游戏目录（GTAIV.exe 旁边）再运行；或先用 Steam
     启动过一次游戏让注册表留下路径。仍失败可右键「以管理员身份运行」。
2. 游戏里部分中文变成问号 ?
   → 字库文件没装上：重新双击 安装.bat；若装过其它字库类 mod 请先移除。
3. 暂停地图区名显示乱码 / 错字
   → mapfix.asi 没装上或被杀毒软件隔离。确认游戏目录 plugins\\mapfix.asi
     存在，必要时加入杀软白名单后重装。
4. 安装提示「有 N 个文件写入失败」
   → 关闭游戏与 Steam 后重跑；游戏目录取消只读；右键安装.bat「以管理员
     身份运行」；杀软拦截就加白名单。全部文件显示 [成功] 才算装好。
5. 某些内容仍是英文
   → 属于有意不译的范围（菜单、线上多人、制作名单、真实品牌名等），
     逐条见《有意保留英文清单.tsv》。
6. 包被解压进了游戏目录本身
   → 把压缩包重新解压到一个独立文件夹再安装即可（安装.bat 会自动找游戏
     目录，不需要放进游戏目录；解压进去反而装不上、卸载会把补丁还原掉）。
"""

CHANGELOG = """============================================================
  GTA4 三章简中汉化包 — 更新日志
============================================================

v2.1（2026-11-10，一键移植 / 跨平台打包改造）
  - 安装脚本补齐 update 层 6 个覆盖文件：三章 american.gxt + 三章 fonts.wtd，
    与卸载脚本的 _ORIGINAL_* 还原项一一对应（此前安装只铺了 plugins 侧文件）。
  - 新增旧汉化 / 死文件扫描隔离：
      Windows  清理旧汉化.bat + 清理旧汉化.ps1
      Linux    cleanup_old_zh.sh
    疑似旧汉化 ASI、数据目录、外置字库，以及基础层与 update 层的残留字典 /
    图集 / 汉化索引（chinese.gxt、fonts_chs.wtd、content_chs.dat 等）先隔离到
    `_chs_old_isolated_<时间戳>/`（不直接删除，附《隔离清单.txt》），
    原版多语言 gxt、我方 american* 字典与 fonts.wtd、update\\GTA IV 资源套及其它图形/玩法 MOD 不被误伤。
  - 新增 SteamOS / Linux（Proton 跑 Windows 版）一键脚本：
      install.sh / uninstall.sh / cleanup_old_zh.sh，与 Windows 包同一套文件、
    同构目录；自动定位桌面/Flatpak Steam 库及 libraryfolders.vdf 多库，
    定位不到可用 GTA4_DIR= 手动指定。
  - 前置游戏版本口径更新为 1.2.0.59（三合一）。
  - 回滚基底更正为英文原版：包内 _ORIGINAL_* 三章 gxt + 三章图集取自未汉化的
    基础层原版（此前误带旧汉化备份，卸载会退回旧中文）；卸载显式拷回 update 层
    还原英文。移除冗余的字符表基底（字符表随补丁目录删除即可）。
  - 主补丁 GTA4.CHS.asi 仍为第三方二进制、未改动；若有源于该 asi 自身的问题，
    需等上游汉化补丁更新 asi 文件，本包只交付翻译数据资产。

v2.0（2026-11-10，译文字典 + 字库扩容）
  译文字典（三章定稿，相对 v1.0 补完包）：
    - 中文改译 / 润色：11,440 条
    - 英译中（我方新译）：3,276 条
    - 回退英文：102 条
    - 纯符号 / 标点差异：27 条
    - 差异条目合计：14,845 条
    - 三章条目数：本体 59,661 / TLAD 18,557 / TBoGT 23,911；
      含中文条目：本体 38,315 / TLAD 10,718 / TBoGT 13,381。
  字库扩容：
    - 允许字符表 3,580 → 3,624，新增 44 个 CJK 译名用字。
    - 三章字库图集按新表重排，整张 BC3/DXT5 回写；旧字模离线校验
      墨量偏差 ≤0.06%，旧字笔画 IoU >0.982。
    - 缺字「厩」经改译避开（stable → 马棚），不入字表。
  质量闸：
    - 三章 gxt 条目 0 缺 0 多；控制码（~z~ ~n~ ~s~ 等）随原文守恒；
      独有键核查通过；回环打包 0 不一致。
  附带：
    - 主补丁 GTA4.CHS.asi 随包提供，二进制未改动；
      whm_table.dat、custom_translations.json 沿用原补丁。
    - 沿用 mapfix.asi（暂停地图区名修复）。
"""

DECL = """============================================================
  GTA4 三章简中汉化包 — 声明
============================================================

【免责声明】
本补丁按"现状"免费提供，仅供学习交流使用。制作者不对使用本补丁产生的
任何直接或间接损失负责（包括但不限于游戏崩溃、存档损坏、系统故障），
一切后果由使用者自负。本补丁为非官方同人修改，与 Rockstar Games /
Take-Two Interactive 无任何关联。

【基于原补丁制作】
本包是基于 GTA4 简中补丁（GTA4.CHS.asi）制作的汉化整合包。该原补丁由
无名汉化组于 2016 年底立项，2019 年停工后由 GTA4 贴吧吧友接棒续作完工。
本包附带原补丁的 GTA4.CHS.asi 本体，其二进制未做改动；我方只替换
译文字典、字符表与字库图集，whm_table.dat 与 custom_translations.json
沿用原补丁。

【原汉化补丁声明（逐字保留）】
本汉化补丁仅供交流学习使用，任何组织或个人不得将此用于任何形式的商业
目的，对此产生的一切后果由使用者自负，本组将不对此负任何责任。

【版权与分发】
本包仅供交流学习、免费分发；不重新打包原补丁、不自称官方汉化、不收费、
不引入任何破解。原补丁署名与声明已如上逐字保留。

【随附原版资源说明】
包内 _ORIGINAL_* 为三章英文原版译文字典与字库图集，仅用于卸载时把 update 层
还原为英文原版；本包不提供游戏本体、不含任何破解或付费内容。
"""

README = """# GTA4 简中补丁之补丁（含 AI 翻译）v2.1

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
"""

wtxt("使用说明（必读）.txt", USAGE)
wtxt("更新日志.txt", CHANGELOG)
wtxt("声明.txt", DECL)
wmd("README.md", README)

# 有意保留英文清单：合并 keep_en.tsv（保留英文条目）+ no_translate.tsv（数字/符号）
out = os.path.join(REL, "有意保留英文清单.tsv")
header = "chapter\ttable\tcrc\tenglish\treason\n"
rows = []
for src in ["keep_en.tsv", "no_translate.tsv"]:
    p = os.path.join(DATA, src)
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    for ln in lines[1:]:
        row = ln.split("\t")
        if len(row) >= 5 and any(c.strip() for c in row):
            rows.append("\t".join(row[:5]))
with open(out, "wb") as f:
    f.write(b"\xEF\xBB\xBF" + (header + "\n".join(rows)).encode("utf-8"))
print("有意保留英文清单.tsv", len(rows), "行")
print(">>> 文档生成完成")
