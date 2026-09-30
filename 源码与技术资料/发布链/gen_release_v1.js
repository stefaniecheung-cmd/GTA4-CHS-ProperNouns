/* gen_release_v1.js - 生成 v1.0 发布文件夹《GTA4汉化补丁之补丁（含AI翻译）v1.0》。
   载荷 = 成品包v7（8 载荷 + 7 _ORIGINAL_*，逐字节复制）；
   安装.bat 重生成（v1.0 横幅 + 原补丁检测：无 GTA4.CHS.asi 则打印 GitHub/官网链接并中止）；
   文档：声明.txt / 使用说明.txt / 更新日志.txt（BOM+CRLF）+ 翻译对照表.md + 未翻译内容清单.tsv。
   同时把 翻译对照表-最新.md 复制进 项目收尾\。不生成 zip。 */
const fs = require('fs');
const path = require('path');
const PROJ = 'E:/SteamLibrary/steamapps/common/Grand Theft Auto IV/汉化补丁工程/';
const B = PROJ + '03-补丁构建/';
const V7 = B + '成品包v7/';
const REL = PROJ + 'GTA4汉化补丁之补丁（含AI翻译）v1.0/';
const FIN = PROJ + '项目收尾/';

fs.rmSync(REL, { recursive: true, force: true });
fs.mkdirSync(REL, { recursive: true });
fs.mkdirSync(FIN, { recursive: true });

/* 1) 载荷 + 回滚基底（与 成品包v7 逐字节一致） */
const PAY = [
  'plugins/GTA4.CHS/char_table.dat', 'plugins/mapfix.asi',
  'update/pc/textures/fonts.wtd', 'update/TLAD/pc/textures/fonts.wtd', 'update/TBoGT/pc/textures/fonts.wtd',
  'update/common/text/american.gxt', 'update/TLAD/common/text/american.gxt', 'update/TBoGT/common/text/american.gxt',
  '_ORIGINAL_char_table.dat', '_ORIGINAL_fonts_pc.wtd', '_ORIGINAL_fonts_tlad.wtd', '_ORIGINAL_fonts_tbogt.wtd',
  '_ORIGINAL_american.gxt', '_ORIGINAL_american_tlad.gxt', '_ORIGINAL_american_tbogt.gxt',
];
for (const p of PAY) {
  fs.mkdirSync(path.dirname(REL + p), { recursive: true });
  fs.copyFileSync(V7 + p, REL + p);
}
console.log('载荷+回滚基底 ' + PAY.length + ' 文件 <- 成品包v7');

/* 2) 安装.bat / 卸载.bat（GBK 编码 + chcp 936，中文提示；自动定位游戏目录；
      原补丁检测只认「定位到的游戏目录\GTA4.CHS.asi」，绝不引用 GTA4.CHS-master 源码目录） */
const { execFileSync } = require('child_process');
function writeGbkBat(p, text) {
  const crlf = text.replace(/\r?\n/g, '\r\n');
  let gbk;
  try {
    gbk = execFileSync('iconv', ['-f', 'UTF-8', '-t', 'GBK'], { input: Buffer.from(crlf, 'utf8'), maxBuffer: 1 << 24 });
  } catch (e) {
    throw new Error('iconv 转 GBK 失败（需 Git Bash 的 iconv 在 PATH）：' + e.message);
  }
  const back = new TextDecoder('gbk').decode(gbk);
  if (back !== crlf) throw new Error('GBK 往返不一致，拒绝写出：' + p);
  fs.writeFileSync(p, gbk);
  console.log(path.basename(p) + '（GBK 中文提示，' + gbk.length + ' 字节，往返校验一致）');
}

/* 定位逻辑（安装/卸载共用文本段）：
   方式1 相对路径（补丁夹在游戏目录/工程目录内）；方式2 Rockstar 注册表；方式3 Steam 注册表+库列表 vdf。
   所有候选都必须含 GTAIV.exe 才采纳（:trygame 同时兼容 根目录\GTAIV.exe 与 根目录\GTAIV\GTAIV.exe 两种形态）。 */
const LOCATE = [
  'rem ---- 自动定位游戏本体（以 GTAIV.exe 为准）----',
  'set "GAME="',
  'set "CAND=%PKG%.."',
  'call :trygame',
  'set "CAND=%PKG%..\\..\\GTAIV"',
  'call :trygame',
  'set "CAND=%PKG%..\\..\\..\\GTAIV"',
  'call :trygame',
  'if not defined GAME (',
  '  if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (set "REGK=HKLM\\SOFTWARE\\WOW6432Node\\Rockstar Games\\Grand Theft Auto IV") else (set "REGK=HKLM\\SOFTWARE\\Rockstar Games\\Grand Theft Auto IV")',
  '  for /f "skip=2 tokens=2*" %%a in (\'reg query "!REGK!" /v InstallFolder 2^>nul\') do set "CAND=%%b"',
  '  if defined CAND call :trygame',
  ')',
  'if not defined GAME for /f "tokens=2*" %%a in (\'reg query "HKCU\\Software\\Valve\\Steam" /v SteamPath 2^>nul\') do set "STEAM=%%b"',
  'if not defined GAME if not defined STEAM set "STEAM=C:\\Program Files (x86)\\Steam"',
  'if not defined GAME (',
  '  set "STEAM=!STEAM:/=\\!"',
  '  call :trysteam "!STEAM!"',
  '  set "VDF=!STEAM!\\steamapps\\libraryfolders.vdf"',
  '  if exist "!VDF!" for /f "tokens=2" %%p in (\'findstr /c:"path" "!VDF!"\') do call :trylib %%p',
  ')',
  'if not defined GAME (',
  '  echo [错误] 未能自动定位游戏本体（找不到 GTAIV.exe）。',
  '  echo        解决办法任选其一：',
  '  echo        1. 把本文件夹放进 GTA4 游戏目录，GTAIV.exe 旁边，再运行；',
  '  echo        2. 先用 Steam 启动过一次游戏，让注册表留下路径，再运行。',
  '  echo.',
  '  pause',
  '  exit /b 1',
  ')',
  'echo [信息] 游戏目录：!GAME!',
  'echo.',
].join('\r\n');

const LOCATE_SUBS = [
  ':trysteam',
  'set "CAND=%~1\\steamapps\\common\\Grand Theft Auto IV\\GTAIV"',
  'call :trygame',
  'exit /b 0',
  '',
  ':trylib',
  'set "LIB=%~1"',
  'set "LIB=!LIB:\\\\=\\!"',
  'call :trysteam "!LIB!"',
  'exit /b 0',
  '',
  ':trygame',
  'if defined GAME exit /b 0',
  'if exist "%CAND%\\GTAIV.exe" set "GAME=%CAND%" & exit /b 0',
  'if exist "%CAND%\\GTAIV\\GTAIV.exe" set "GAME=%CAND%\\GTAIV"',
  'exit /b 0',
].join('\r\n');

const ORIG_CHECK = [
  'rem ---- 检测原汉化补丁：认游戏目录 plugins\\GTA4.CHS.asi（原补丁实际安装位置），兼容根目录 ----',
  'if exist "!GAME!\\plugins\\GTA4.CHS.asi" goto orig_ok',
  'if exist "!GAME!\\GTA4.CHS.asi" goto orig_ok',
  'echo [错误] 未检测到原汉化补丁：游戏目录及其 plugins 子目录都缺少 GTA4.CHS.asi。',
  'echo        本补丁是补丁的补丁，必须先安装原汉化补丁',
  'echo        2024-09-13 版，无名汉化组立项、GTA4 贴吧吧友接手完成。',
  'echo.',
  'echo        原汉化补丁获取链接：',
  'echo        GitHub：https://github.com/ckeleshi/GTA4.CHS',
  'echo        官　网：https://b9348.pages.dev/',
  'echo.',
  'pause',
  'exit /b 1',
  ':orig_ok',
  'echo [信息] 已检测到原汉化补丁。',
  'echo.',
].join('\r\n');

const FILEOPS = [
  ['plugins\\GTA4.CHS\\char_table.dat', '_ORIGINAL_char_table.dat'],
  ['update\\pc\\textures\\fonts.wtd', '_ORIGINAL_fonts_pc.wtd'],
  ['update\\TLAD\\pc\\textures\\fonts.wtd', '_ORIGINAL_fonts_tlad.wtd'],
  ['update\\TBoGT\\pc\\textures\\fonts.wtd', '_ORIGINAL_fonts_tbogt.wtd'],
  ['update\\common\\text\\american.gxt', '_ORIGINAL_american.gxt'],
  ['update\\TLAD\\common\\text\\american.gxt', '_ORIGINAL_american_tlad.gxt'],
  ['update\\TBoGT\\common\\text\\american.gxt', '_ORIGINAL_american_tbogt.gxt'],
];
const installOps = FILEOPS.map(([rel, bak]) => 'set "REL=' + rel + '"\r\nset "BAK=' + bak + '"\r\ncall :one').join('\r\n');
const uninstallOps = FILEOPS.map(([rel, bak]) => 'set "REL=' + rel + '"\r\nset "BAK=' + bak + '"\r\ncall :back').join('\r\n');

const INSTALL = [
  '@echo off',
  'chcp 936 >nul',
  'setlocal enabledelayedexpansion',
  'title GTA4 汉化补完补丁 v1.0 安装',
  'echo ============================================================',
  'echo   GTA4 简中补丁之补丁（含AI翻译）v1.0  安装程序',
  'echo   内容：专有名词 + 1611 条整句补译 + 字库扩充 + 地图区名修复',
  'echo   前提：已安装原汉化补丁 2024-09-13 版；不修改 GTA4.CHS.asi',
  'echo   支持自动定位游戏目录，无需把本文件夹放进游戏目录',
  'echo ============================================================',
  'echo.',
  'set "PKG=%~dp0"',
  'set "FAILED=0"',
  LOCATE,
  ORIG_CHECK,
  'rem ---- 防呆：包被解压进游戏目录本身时，源=目标，copy 会报“文件无法自身复制” ----',
  'for %%I in ("%PKG%.") do set "PKGN=%%~fI"',
  'for %%I in ("!GAME!.") do set "GAMEN=%%~fI"',
  'if /i "!PKGN!"=="!GAMEN!" (',
  '  echo [错误] 检测到补丁包被解压进了游戏目录本身（安装.bat 与 GTAIV.exe 在同一个目录）。',
  '  echo        这样“复制到游戏目录”就变成了复制到自己，永远装不上；',
  '  echo        而且这种情况下运行 卸载.bat 会把补丁还原掉。',
  '  echo.',
  '  echo        解决办法：',
  '  echo        1. 把补丁 zip 重新解压到一个【独立文件夹】（例如桌面新建一个）；',
  '  echo        2. 双击那个文件夹里的 安装.bat —— 它会自动找到游戏目录，不需要放进游戏目录。',
  '  echo.',
  '  pause',
  '  exit /b 1',
  ')',
  installOps,
  'attrib -r "!GAME!\\plugins\\mapfix.asi" >nul 2>nul',
  'copy /y "%PKG%plugins\\mapfix.asi" "!GAME!\\plugins\\mapfix.asi" >nul',
  'if errorlevel 1 (echo [失败] plugins\\mapfix.asi —— 系统返回： & copy /y "%PKG%plugins\\mapfix.asi" "!GAME!\\plugins\\mapfix.asi" & set /a FAILED+=1) else (echo [成功] plugins\\mapfix.asi)',
  'echo.',
  'if not "!FAILED!"=="0" (',
  '  echo [错误] 有 !FAILED! 个文件写入失败，补丁未完整安装！',
  '  echo        常见原因：',
  '  echo        1. 游戏或 Steam 正在运行：请全部关闭后重新运行本程序；',
  '  echo        2. 目标文件只读 / 被云盘同步占用：右键游戏目录属性，取消只读；',
  '  echo        3. 权限不足：右键本安装.bat，选择“以管理员身份运行”；',
  '  echo        4. 杀毒软件拦截：查看杀软日志，把游戏目录加入白名单后重试。',
  '  echo        诊断信息——游戏目录：!GAME!',
  '  pause',
  '  exit /b 1',
  ')',
  'echo [完成] 全部文件安装成功，启动游戏即可。',
  'echo        如需还原，双击本文件夹里的 卸载.bat。',
  'pause',
  'exit /b 0',
  '',
  LOCATE_SUBS,
  '',
  ':one',
  'if not exist "!GAME!\\%REL%" echo [错误] 游戏目录缺少 %REL% ，原汉化补丁可能不完整。 & pause & exit 1',
  'if exist "%PKG%%BAK%" goto one_copy',
  'copy /y "!GAME!\\%REL%" "%PKG%%BAK%" >nul && echo [备份] %BAK%',
  ':one_copy',
  'attrib -r "!GAME!\\%REL%" >nul 2>nul',
  'copy /y "%PKG%%REL%" "!GAME!\\%REL%" >nul',
  'if errorlevel 1 (echo [失败] %REL% —— 系统返回： & copy /y "%PKG%%REL%" "!GAME!\\%REL%" & set /a FAILED+=1) else (echo [成功] %REL%)',
  'exit /b 0',
  '',
].join('\r\n');

const UNINSTALL = [
  '@echo off',
  'chcp 936 >nul',
  'setlocal enabledelayedexpansion',
  'title GTA4 汉化补完补丁 v1.0 卸载',
  'echo ============================================================',
  'echo   GTA4 简中补丁之补丁 v1.0  卸载程序',
  'echo   功能：把 7 个文件还原为原汉化补丁版本，并删除 mapfix.asi',
  'echo ============================================================',
  'echo.',
  'set "PKG=%~dp0"',
  'set "FAILED=0"',
  LOCATE,
  uninstallOps,
  'if exist "!GAME!\\plugins\\mapfix.asi" (del /f /q "!GAME!\\plugins\\mapfix.asi" && echo [成功] 已删除 plugins\\mapfix.asi || (echo [失败] 删除 plugins\\mapfix.asi 失败 & set /a FAILED+=1))',
  'echo.',
  'if not "!FAILED!"=="0" (',
  '  echo [错误] 有 !FAILED! 个文件还原失败（常见原因：游戏/Steam 正在运行、文件只读、权限不足、杀软拦截）。',
  '  echo        请关闭游戏与 Steam 后，右键本卸载.bat 选择“以管理员身份运行”再试。',
  '  pause',
  '  exit /b 1',
  ')',
  'echo [完成] 已还原为原汉化补丁，专有名词恢复英文。',
  'pause',
  'exit /b 0',
  '',
  LOCATE_SUBS,
  '',
  ':back',
  'if not exist "%PKG%%BAK%" echo [错误] 找不到备份 %BAK% ，请勿删除补丁文件夹里的 _ORIGINAL_ 文件。 & pause & exit 1',
  'attrib -r "!GAME!\\%REL%" >nul 2>nul',
  'copy /y "%PKG%%BAK%" "!GAME!\\%REL%" >nul',
  'if errorlevel 1 (echo [失败] %REL% —— 系统返回： & copy /y "%PKG%%BAK%" "!GAME!\\%REL%" & set /a FAILED+=1) else (echo [还原] %REL%)',
  'exit /b 0',
  '',
].join('\r\n');

writeGbkBat(REL + '安装.bat', INSTALL);
writeGbkBat(REL + '卸载.bat', UNINSTALL);

/* 3) 文档（BOM + CRLF） */
const wtxt = (p, s) => fs.writeFileSync(p, '\uFEFF' + s.replace(/\n/g, '\r\n'), 'utf8');

wtxt(REL + '声明.txt', `========================================================
  GTA4 简中补丁之补丁（含AI翻译）v1.0 — 声明
========================================================

【制作声明】
本补丁由 Non-ID、华 借助 AI 工具制作。

【免责声明】
本补丁按"现状"免费提供，仅供学习交流使用。制作者不对使用本补丁产生的
任何直接或间接损失负责（包括但不限于游戏崩溃、存档损坏、系统故障），
一切后果由使用者自负。本补丁为非官方同人修改，与 Rockstar Games /
Take-Two Interactive 无任何关联。

【反馈联系】
邮箱：ghh213014@163.com

【基于原补丁制作】
本补丁是基于 GTA4 简中补丁 2024-09-13 版 制作的补充层（"补丁的补丁"）。
该原补丁由 无名汉化组 于 2016 年底立项，2019 年停工后由 GTA4 贴吧吧友
接棒续作、于三年后完工（2024-09-13 版即其成果）。本补丁不包含原补丁的
任何文件，必须先安装原补丁才能使用；本补丁不修改、不替换原补丁的
GTA4.CHS.asi。

【原汉化补丁声明（逐字保留）】
本汉化补丁仅供交流学习使用，任何组织或个人不得将此用于任何形式的商业目的，对此产生的一切后果由使用者自负，本组将不对此负任何责任。

（原补丁署名：无名汉化组立项；名誉组长 倾城、公子；程序 Clans、MR；
翻译/校对/测试/宣传由 GTA4 贴吧吧友团队完成——完整名单见原补丁《汉化说明.txt》）

【版权与分发】
本补完包同样仅供交流学习、免费分发；不重新打包原补丁、不自称汉化、
不收费、不引入任何破解。原补丁署名与声明已如上逐字保留。
`);

wtxt(REL + '使用说明（必读）.txt', `========================================================
  GTA4 简中补丁之补丁（含AI翻译）v1.0 — 使用说明
========================================================

【这是什么】
在 GTA4 简中补丁 2024-09-13 版（无名汉化组立项、停工后由 GTA4 贴吧吧友
接手完成）之上，把原补丁故意保留英文的
人名/地名/车名等专有名词、以及约 1,600 句漏译的任务对白/电话/短信/邮件
补成中文。覆盖三章：本体 / 失落与诅咒(TLAD) / 夜生活之曲(TBoGT)。
附带一个独立小插件 mapfix.asi，修复暂停地图区名的乱码问题。

【前置条件（重要）】
1. 游戏：GTA4 完整版 1.2.0.43（三合一）。
2. 必须先安装原汉化补丁（2024-09-13 版，无名汉化组立项、GTA4 贴吧吧友接手完成）。
   安装.bat 会自动检测（认 GTA4.CHS.asi 文件）；检测不到会给出原补丁的
   GitHub 链接（https://github.com/ckeleshi/GTA4.CHS，官网
   https://b9348.pages.dev/）并中止安装。

【安装】
0. 把 zip 解压到一个【独立文件夹】（不要解压进游戏目录、也别把文件合并进去）。
1. 确认游戏没有在运行。
2. 双击 安装.bat —— 会自动定位游戏本体（依次尝试：补丁文件夹相对位置 →
   Rockstar 注册表 → Steam 注册表与 Steam 库列表），**不要求**把本文件夹
   放进游戏目录；当然放进 GTAIV 目录里也可以。
3. 看到「[完成] 全部文件安装成功」即成功；全部提示为中文。
4. 启动游戏。
安装.bat 会先检测原汉化补丁（认游戏目录 plugins\\GTA4.CHS.asi，兼容根目录）；检测不到会
给出原补丁的 GitHub/官网链接并中止，不会写入任何文件。
安装时覆盖 7 个文件（char_table.dat + 三章 fonts.wtd + 三章 american.gxt），
并新增 plugins\\mapfix.asi。覆盖前会把现有文件备份到本文件夹的 _ORIGINAL_*
（文件夹里已附带原版基底，备份不会被覆盖污染）。

【卸载/回退】
双击 卸载.bat：用 _ORIGINAL_* 把 7 个文件还原成原汉化补丁原版，并删除
mapfix.asi。请勿删除文件夹里的 _ORIGINAL_* 文件。
已装过旧版补完包（v4~v7 任一）的用户：直接双击本包 安装.bat 升级即可。

【本包内容】
  安装.bat / 卸载.bat            安装与回退
  plugins\\GTA4.CHS\\char_table.dat  允许字符名单（3,580 字，含新增的间隔号･与 62 个译名用字）
  plugins\\mapfix.asi             暂停地图区名修复插件
  update\\...\\fonts.wtd ×3       三章字库图（新增字形）
  update\\...\\american.gxt ×3    三章文本字典（专名+整句补译）
  _ORIGINAL_* ×7                 卸载回退基底（=原汉化补丁原版文件）
  声明.txt / 更新日志.txt        版权与免责声明 / 版本记录
  翻译对照表.md                  全部译名汇总（英中对照）
  未翻译内容清单.tsv             有意不翻译的内容+出处+原因（9,347 行）
  源码与技术资料\               核心源码与工程文档（技术原理/日志/插件源码与脚本）

【常见问题】
1. 安装.bat 提示「未检测到原汉化补丁」
   → 没装原汉化补丁。按提示里的 GitHub/官网链接先装原汉化补丁
     （2024-09-13 版），再重新双击 安装.bat。
2. 安装.bat 提示「未能自动定位游戏本体」
   → 把本文件夹放进 GTA4 游戏目录（GTAIV.exe 旁边）再运行；或先用 Steam
     启动过一次游戏让注册表留下路径。仍失败可右键「以管理员身份运行」。
3. 安装.bat 提示 游戏目录缺少 xxx 文件
   → 原补丁不完整，重装原补丁后再试。
4. 游戏里部分中文变成问号 ?
   → 字库文件没装上：重新双击 安装.bat；若装过其它字库类 mod 请先移除。
5. 暂停地图上的区名显示乱码/错字
   → plugins\\mapfix.asi 没装上或被杀毒软件隔离。确认游戏目录
     GTAIV\\plugins\\mapfix.asi 存在，必要时加入杀软白名单后重装。
6. 杀毒软件对 .asi/.bat 报警
   → mapfix.asi 是自研的地图修复插件（开源逻辑：只替换地图区名字符串指针，
     不注入、不联网）；.bat 只做文件复制。请自行判断后加白名单。
7. 开屏卡死/闪退一次
   → 游戏本体偶发 bug（隔离测试证实与本补丁无关），重进一次即可；若持续
     出现，先双击 卸载.bat 回退再排查其它 mod。
8. 某些内容仍是英文
   → 属于有意不翻译的范围（界面菜单词、线上多人内容、制作名单、游戏内
     网站、真实人物/品牌名等），逐条见《未翻译内容清单.tsv》。
9. 警察电脑输入名字的任务（Search and Delete）
   → 需要照抄键入的英文姓名字段特意保留了英文；关键提示句是中英双语
     「莱尔･里瓦斯 (Lyle)」，输入括号里的英文即可通关。
10. 提示「检测到补丁包被解压进了游戏目录本身」
   → 把 zip 重新解压到一个独立文件夹再安装即可（安装.bat 会自动找游戏目录，
     不需要放进游戏目录；解压进去反而装不上、且卸载会把补丁还原掉）。
11. 安装提示「有 N 个文件写入失败，补丁未完整安装」
   → 程序会把失败的文件和系统原始报错打出来。按提示排查：①关闭游戏与 Steam
     后重跑；②游戏目录取消只读（右键属性）；③右键安装.bat「以管理员身份运行」；
     ④杀软拦截就加白名单。全部文件显示 [成功] 才算装好。
12. 想核对某个译名
   → 见《翻译对照表.md》（含人名/区名/地名/二级地名/车名/剧情专名各节）。

【反馈】
邮箱：ghh213014@163.com（附截图与存档位置说明更好）
`);

wtxt(REL + '更新日志.txt', `========================================================
  GTA4 简中补丁之补丁（含AI翻译）— 更新日志
========================================================

v1.0（2026-09-19）初版
  首个对外发布版本，整合工程期全部成果（内部里程碑 M1~V7c）：
  - 人名中文化：三章字幕/短信/邮件/通讯录/警察数据库等，对照表人名节 584 条
    （Niko→尼克、Roman→罗曼、Luis Lopez→路易斯･洛佩兹…）。
  - 地名中文化：对白/短信里的区域与地点名；暂停地图 74 区名 + 进区弹窗 +
    HUD 区域名（靠附带的 mapfix.asi 修复地图乱码）。
  - 车名 166 条（HUD 与对白一致）、街名/桥名/二级地名 600+ 条。
  - 剧情专名补完：昵称/联系人/任务赛道名（Dog Meat→狗肉、Real Badman→
    真巴德曼、Squid Row→鱿鱼排…）。
  - 整句补译 1,611 条：原汉化补丁整句漏译的任务对白/电话/短信/邮件/指令句
    （本体 1,469 / TLAD 84 / TBoGT 58），AI 辅助翻译+人工三校验。
  - 字库扩充：允许字符 3,517→3,559（新增间隔号･与 41 个译名常用字，末位新增「锆」）。
  - 译名修订：Lopez 洛佩斯→洛佩兹；州名 Liberty 自由州→自由城。
  - 基底译法对齐 + 播报补全（v7f，用户拍板"与原汉化补丁既定译法冲突一律以原补丁为准"）：
    区名/站名改从原补丁对白一贯用法——Downtown→中心区、The Exchange→证交区、
    Middle Park→中心公园（东/西同）、Star Junction→星汇广场、Meadows Park→草地公园、
    Leaper's Bridge→纵身大桥、Firefly Projects→萤火虫公屋社区、Dukes Boulevard→
    公爵区大街、Grand Boulevard→格兰德大街、Funland→游乐园、Meadows Park & Ride→
    草地公园换乘停车场；并补全三章 110 条纯英文进区弹窗/问答地名（Beachgate→比奇盖特、
    Boabo→博阿博、Anger Bay→安格尔湾 等）。术语表同步；未翻译清单按 V7 实值重新核对
    （剔除 875 条已被后续层译掉的陈旧行）。
  - 字幕全量体检修复 140+ 处：弗朗西斯国际机场统一、对白车名与 HUD 一致、
    地铁站名标签全译（法兰克福地下站/锰西街站/舒特勒车站等）、圣迈克尔/凯奇/
    盖塔莱夫大厦/锆石大厦/杰克･豪泽/乘风破浪 等拍板译名、调试残留清理。
  - 防卡关处理：LCPD 警察数据库需键入的姓名字段保留英文，关键句双语提示。
  - 附带：安装/卸载 bat（**自动定位游戏目录**：相对路径/Rockstar 注册表/
    Steam 库列表三级探测，不要求放在游戏目录内；**全中文提示**；原补丁
    检测：未装时给出下载链接并中止；自动备份、一键还原）、
    翻译对照表、未翻译内容清单（12,372 行，注明原因）。
`);

/* 4) 对照表 + 未翻译清单（发布包 + 项目收尾 各一份） */
fs.copyFileSync(PROJ + '翻译对照表-最新.md', REL + '翻译对照表.md');
fs.copyFileSync(PROJ + '翻译对照表-最新.md', FIN + '翻译对照表-最新.md');
fs.copyFileSync(FIN + '未翻译内容清单.tsv', REL + '未翻译内容清单.tsv');
try { fs.rmSync(REL + '使用说明.txt', { force: true }); } catch (e) { }

/* 4b) README.md / 分享链接.txt / 地图区名对照表.md（复现用：随包一并产出，避免重跑生成器时丢失） */
const GH_REPO = 'https://github.com/ghh-6/GTA4-CHS-ProperNouns';
const GH_REL = GH_REPO + '/releases/tag/v1.0';
fs.writeFileSync(REL + 'README.md', [
  '# GTA4 简中补丁之补丁（含 AI 翻译）v1.0',
  '',
  '在原版简中补丁（2024-09-13 版，无名汉化组立项、GTA4 贴吧吧友接手完成）之上，补完**专有名词**与**整句漏译**的非官方增补包。',
  '',
  '## 内容',
  '',
  '- 人名进入中文：字幕/短信/邮件/通讯录/保龄球邀请/警察数据库/制作名单（三章）',
  '- 地名进入中文：对白与短信地名、暂停地图 74 区名（附 `mapfix.asi` 修复原版地图乱码）、HUD 区域名',
  '- 车名 166 条、街名/桥名/二级地名 600+ 条',
  '- 剧情整句补译 1,611 条（任务对白/电话/短信/邮件/指令句）',
  '- 字库扩充至 3,580 字（间隔号及 60+ 译名常用字）',
  '',
  '## 安装（摘要）',
  '',
  '1. **先装原版简中补丁**（必需）：' + GH_REPO.replace('GTA4-CHS-ProperNouns', 'ckeleshi/GTA4.CHS') + ' ／ https://b9348.pages.dev/',
  '2. 把 zip **解压到独立文件夹**，双击 `安装.bat`（自动定位游戏目录，不必放进游戏目录）。',
  '3. 卸载：双击 `卸载.bat` 还原到原版补丁状态。',
  '',
  '详见 `使用说明（必读）.txt`、`更新日志.txt`、`声明.txt`、`翻译对照表.md`、`未翻译内容清单.tsv`、`地图区名对照表.md`、`分享链接.txt`。',
  '',
  '## 技术资料（源码与原理）',
  '',
  '本包内 `源码与技术资料/` 收录核心源码与工程文档：',
  '',
  '- `技术原理.md` —— 三层架构、GXT 字典与哈希、字库白名单与补字工艺、mapfix 修复原理；',
  '- `项目日志.md` —— 开发历程与问题复盘；',
  '- `mapfix/`、`procdiag/` —— 地图修复插件与根因诊断工具的完整 C++ 源码 + 构建脚本；',
  '- `工具脚本/`、`文本引擎/`、`发布链/` —— GXT/字库工具、文本替换引擎、发布校验脚本。',
  '',
  '详见 `源码与技术资料/README.md`。',
  '',
  '## 声明',
  '',
  '免费发布，仅供交流学习，**禁止任何商业用途**；不含破解、不改动原补丁文件、不提供游戏本体。',
  '本包在原版补丁之上叠加，原补丁的一切著作权归其作者所有；使用后果由使用者自负。',
  '',
].join('\n'), 'utf8');
fs.writeFileSync(REL + '分享链接.txt', '\uFEFF' + [
  '# 分享链接（GTA4 汉化补丁之补丁 · 含AI翻译 v1.0）',
  '',
  '## 网盘（百度网盘）',
  '',
  '通过网盘分享的文件：**GTA4汉化补丁之补丁（含AI翻译）v1.0.zip**',
  '',
  '- 链接：https://pan.baidu.com/s/1YLMsVCKzbsIls-rxeBAvOQ?pwd=db7t',
  '- 提取码：**db7t**',
  '',
  '## GitHub',
  '',
  '- 仓库：' + GH_REPO,
  '- 发布页（Release）：' + GH_REL,
  '- **直接下载 zip**：https://github.com/ghh-6/GTA4-CHS-ProperNouns/releases/download/v1.0/GTA4-CHS-ProperNouns-v1.0.zip',
  '',
  '## 使用前必读',
  '',
  '1. **必须先安装原汉化补丁（2024-09-13 版）**——本补丁是"补丁的补丁"，不含原补丁文件。',
  '   原补丁获取：GitHub https://github.com/ckeleshi/GTA4.CHS ／ 官网 https://b9348.pages.dev/',
  '2. 把 zip **解压到一个独立文件夹**（不要解压进游戏目录），双击其中的 `安装.bat` ——',
  '   它会自动定位游戏本体，不需要放进游戏目录。',
  '3. 本补丁免费，仅供交流学习；请勿用于任何商业用途。详见包内 声明.txt。',
  '',
].join('\r\n'), 'utf8');
try { fs.copyFileSync(PROJ + '项目收尾/地图区名对照表.md', REL + '地图区名对照表.md'); } catch (e) { console.log('[警告] 地图区名对照表.md 复制失败：' + e.message); }
console.log('README.md + 分享链接.txt + 地图区名对照表.md 已随包产出');

/* 4c) 源码与技术资料（20 文件：mapfix/procdiag 源码 + 核心脚本 + 技术文档。
       README 导览 master 常驻 项目收尾\源码与技术资料-README.md；本生成器整目录重建，重跑不丢。 */
const SRC_FILES = [
  ['01-逆向草稿/procdiag/mapfix.cpp', 'mapfix/mapfix.cpp'],
  ['01-逆向草稿/procdiag/zone_table.h', 'mapfix/zone_table.h'],
  ['01-逆向草稿/procdiag/build_mapfix.bat', 'mapfix/build_mapfix.bat'],
  ['01-逆向草稿/procdiag/gen_zone_table_v7.js', 'mapfix/gen_zone_table_v7.js'],
  ['01-逆向草稿/procdiag/verify_mapfix.js', 'mapfix/verify_mapfix.js'],
  ['01-逆向草稿/procdiag/procdiag.cpp', 'procdiag/procdiag.cpp'],
  ['01-逆向草稿/procdiag/build_procdiag.bat', 'procdiag/build_procdiag.bat'],
  ['01-逆向草稿/procdiag/check_reloc.js', 'procdiag/check_reloc.js'],
  ['01-逆向草稿/gxt_io.js', '工具脚本/gxt_io.js'],
  ['01-逆向草稿/zone_map.js', '工具脚本/zone_map.js'],
  ['04-字库工程/wtd_font.js', '工具脚本/wtd_font.js'],
  ['04-字库工程/render_glyphs.ps1', '工具脚本/render_glyphs.ps1'],
  ['01-逆向草稿/build_m2_patch.js', '文本引擎/build_m2_patch.js'],
  ['01-逆向草稿/build_m10_gxt.js', '文本引擎/build_m10_gxt.js'],
  ['01-逆向草稿/build_v7.js', '文本引擎/build_v7.js'],
  ['01-逆向草稿/gen_release_v1.js', '发布链/gen_release_v1.js'],
  ['01-逆向草稿/verify_release_v1.js', '发布链/verify_release_v1.js'],
  ['项目收尾/技术原理.md', '技术原理.md'],
  ['项目收尾/项目日志.md', '项目日志.md'],
];
const SREL = REL + '源码与技术资料/';
for (const [src, dst] of SRC_FILES) {
  fs.mkdirSync(path.dirname(SREL + dst), { recursive: true });
  fs.copyFileSync(PROJ + src, SREL + dst);
}
fs.copyFileSync(FIN + '源码与技术资料-README.md', SREL + 'README.md');
console.log('源码与技术资料 ' + (SRC_FILES.length + 1) + ' 文件 <- 工程目录');
console.log('翻译对照表.md + 未翻译内容清单.tsv 已放入发布包与项目收尾');
console.log('>>> gen_release_v1 完成：' + REL);
