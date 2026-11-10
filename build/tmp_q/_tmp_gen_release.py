# -*- coding: utf-8 -*-
"""生成发布包 安装.bat / 卸载.bat（GBK + CRLF，三级定位游戏目录）。
本包自洽：自带主补丁 GTA4.CHS.asi 与整个 plugins\\GTA4.CHS 数据文件夹，
另含 mapfix.asi 与 7 个翻译资产（字符表 + 三章字库图集 + 三章译文字典）。
卸载：还原 update 目录 6 个原版基底，删除主 asi、CHS 文件夹、mapfix.asi。"""
import os

REL = r"C:\Game\gta4-chs\release\GTA4-CHS-zh"

# 卸载时还原为原版基底的 update 目录文件（原版游戏有对应文件）
RESTORE = [
    (r"update\pc\textures\fonts.wtd", "_ORIGINAL_fonts_pc.wtd"),
    (r"update\TLAD\pc\textures\fonts.wtd", "_ORIGINAL_fonts_tlad.wtd"),
    (r"update\TBoGT\pc\textures\fonts.wtd", "_ORIGINAL_fonts_tbogt.wtd"),
    (r"update\common\text\american.gxt", "_ORIGINAL_american.gxt"),
    (r"update\TLAD\common\text\american.gxt", "_ORIGINAL_american_tlad.gxt"),
    (r"update\TBoGT\common\text\american.gxt", "_ORIGINAL_american_tbogt.gxt"),
]

# 安装时直接覆盖的插件/数据文件（无原版基底，卸载随主补丁移除）
INSTALL_COPY = [
    r"plugins\GTA4.CHS.asi",
    r"plugins\GTA4.CHS\char_table.dat",
    r"plugins\GTA4.CHS\whm_table.dat",
    r"plugins\GTA4.CHS\custom_translations.json",
    r"plugins\mapfix.asi",
]

LOCATE = [
    "rem ---- 自动定位游戏本体（以 GTAIV.exe 为准）----",
    'set "GAME="',
    'set "CAND=%PKG%.."',
    "call :trygame",
    'set "CAND=%PKG%..\\..\\GTAIV"',
    "call :trygame",
    'set "CAND=%PKG%..\\..\\..\\GTAIV"',
    "call :trygame",
    "if not defined GAME (",
    '  if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (set "REGK=HKLM\\SOFTWARE\\WOW6432Node\\Rockstar Games\\Grand Theft Auto IV") else (set "REGK=HKLM\\SOFTWARE\\Rockstar Games\\Grand Theft Auto IV")',
    '  for /f "skip=2 tokens=2*" %%a in (\'reg query "!REGK!" /v InstallFolder 2^>nul\') do set "CAND=%%b"',
    "  if defined CAND call :trygame",
    ")",
    'if not defined GAME for /f "tokens=2*" %%a in (\'reg query "HKCU\\Software\\Valve\\Steam" /v SteamPath 2^>nul\') do set "STEAM=%%b"',
    'if not defined STEAM set "STEAM=C:\\Program Files (x86)\\Steam"',
    "if not defined GAME (",
    '  set "STEAM=!STEAM:/=\\!"',
    '  call :trysteam "!STEAM!"',
    '  set "VDF=!STEAM!\\steamapps\\libraryfolders.vdf"',
    '  if exist "!VDF!" for /f "tokens=2" %%p in (\'findstr /c:"path" "!VDF!"\') do call :trylib %%p',
    ")",
    "if not defined GAME (",
    "  echo [错误] 未能自动定位游戏本体（找不到 GTAIV.exe）。",
    "  echo        解决办法任选其一：",
    "  echo        1. 把本文件夹放进 GTA4 游戏目录，GTAIV.exe 旁边，再运行；",
    "  echo        2. 先用 Steam 启动过一次游戏，让注册表留下路径，再运行。",
    "  echo.",
    "  pause",
    "  exit /b 1",
    ")",
    'echo [信息] 游戏目录：!GAME!',
    "echo.",
]

LOCATE_SUBS = [
    ":trysteam",
    'set "CAND=%~1\\steamapps\\common\\Grand Theft Auto IV\\GTAIV"',
    "call :trygame",
    "exit /b 0",
    "",
    ":trylib",
    'set "LIB=%~1"',
    'set "LIB=!LIB:\\\\=\\!"',
    'call :trysteam "!LIB!"',
    "exit /b 0",
    "",
    ":trygame",
    "if defined GAME exit /b 0",
    'if exist "%CAND%\\GTAIV.exe" set "GAME=%CAND%" & exit /b 0',
    'if exist "%CAND%\\GTAIV\\GTAIV.exe" set "GAME=%CAND%\\GTAIV"',
    "exit /b 0",
]

copy_plugin_ops = "\r\n".join(
    f'set "REL={rel}"\r\ncall :copy_plugin' for rel in INSTALL_COPY
)
restore_ops = "\r\n".join(
    f'set "REL={rel}"\r\nset "BAK={bak}"\r\ncall :back' for rel, bak in RESTORE
)

INSTALL = [
    "@echo off",
    "chcp 936 >nul",
    "setlocal enabledelayedexpansion",
    "title GTA4 三章简中汉化包 安装",
    "echo ============================================================",
    "echo   GTA4 三章简中汉化包  安装程序",
    "echo   内容：主补丁 GTA4.CHS.asi + 字符表 + 三章字库图集 +",
    "echo         三章译文字典 gxt + 地图区名修复插件 mapfix.asi",
    "echo   本包自带汉化补丁本体，无需另装原补丁",
    "echo   支持自动定位游戏目录，无需把本文件夹放进游戏目录",
    "echo ============================================================",
    "echo.",
    'set "PKG=%~dp0"',
    'set "FAILED=0"',
    *LOCATE,
    "rem ---- 防呆：包被解压进游戏目录本身时，源=目标 ----",
    'for %%I in ("%PKG%.") do set "PKGN=%%~fI"',
    'for %%I in ("!GAME!.") do set "GAMEN=%%~fI"',
    'if /i "!PKGN!"=="!GAMEN!" (',
    "  echo [错误] 检测到补丁包被解压进了游戏目录本身（安装.bat 与 GTAIV.exe 在同一个目录）。",
    "  echo        请把压缩包重新解压到一个【独立文件夹】，再双击其中的 安装.bat。",
    "  echo.",
    "  pause",
    "  exit /b 1",
    ")",
    "rem ---- 复制主补丁、数据文件与翻译资产 ----",
    copy_plugin_ops,
    "echo.",
    'if not "!FAILED!"=="0" (',
    "  echo [错误] 有 !FAILED! 个文件写入失败，补丁未完整安装！",
    "  echo        常见原因：",
    "  echo        1. 游戏或 Steam 正在运行：请全部关闭后重新运行本程序；",
    "  echo        2. 目标文件只读 / 被云盘同步占用：右键游戏目录属性，取消只读；",
    "  echo        3. 权限不足：右键本安装.bat，选择“以管理员身份运行”；",
    "  echo        4. 杀毒软件拦截：查看杀软日志，把游戏目录加入白名单后重试。",
    "  echo        诊断信息——游戏目录：!GAME!",
    "  pause",
    "  exit /b 1",
    ")",
    "echo [完成] 全部文件安装成功，启动游戏即可。",
    "echo        如需还原，双击本文件夹里的 卸载.bat。",
    "pause",
    "exit /b 0",
    "",
    *LOCATE_SUBS,
    "",
    ":copy_plugin",
    'if not exist "!GAME!\\plugins" mkdir "!GAME!\\plugins"',
    'attrib -r "!GAME!\\%REL%" >nul 2>nul',
    'copy /y "%PKG%%REL%" "!GAME!\\%REL%" >nul',
    'if errorlevel 1 (echo [失败] %REL% —— 系统返回： & copy /y "%PKG%%REL%" "!GAME!\\%REL%" & set /a FAILED+=1) else (echo [成功] %REL%)',
    "exit /b 0",
    "",
]

UNINSTALL = [
    "@echo off",
    "chcp 936 >nul",
    "setlocal enabledelayedexpansion",
    "title GTA4 三章简中汉化包 卸载",
    "echo ============================================================",
    "echo   GTA4 三章简中汉化包  卸载程序",
    "echo   功能：还原 update 目录 6 个原版基底，删除主补丁 GTA4.CHS.asi、",
    "echo         plugins\\GTA4.CHS 数据文件夹与 mapfix.asi",
    "echo ============================================================",
    "echo.",
    'set "PKG=%~dp0"',
    'set "FAILED=0"',
    *LOCATE,
    "rem ---- 还原 update 目录原版基底 ----",
    restore_ops,
    "rem ---- 删除主补丁与数据文件夹 ----",
    'if exist "!GAME!\\plugins\\GTA4.CHS.asi" (del /f /q "!GAME!\\plugins\\GTA4.CHS.asi" && echo [成功] 已删除 plugins\\GTA4.CHS.asi || (echo [失败] 删除 plugins\\GTA4.CHS.asi 失败 & set /a FAILED+=1))',
    'if exist "!GAME!\\plugins\\GTA4.CHS" (rmdir /s /q "!GAME!\\plugins\\GTA4.CHS" && echo [成功] 已删除 plugins\\GTA4.CHS 文件夹 || (echo [失败] 删除 plugins\\GTA4.CHS 文件夹失败 & set /a FAILED+=1))',
    'if exist "!GAME!\\plugins\\mapfix.asi" (del /f /q "!GAME!\\plugins\\mapfix.asi" && echo [成功] 已删除 plugins\\mapfix.asi || (echo [失败] 删除 plugins\\mapfix.asi 失败 & set /a FAILED+=1))',
    "echo.",
    'if not "!FAILED!"=="0" (',
    "  echo [错误] 有 !FAILED! 个文件还原 / 删除失败（常见原因：游戏/Steam 正在运行、文件只读、权限不足、杀软拦截）。",
    "  echo        请关闭游戏与 Steam 后，右键本卸载.bat 选择“以管理员身份运行”再试。",
    "  pause",
    "  exit /b 1",
    ")",
    "echo [完成] 已还原为原版英文状态。",
    "pause",
    "exit /b 0",
    "",
    *LOCATE_SUBS,
    "",
    ":back",
    'if not exist "%PKG%%BAK%" echo [错误] 找不到备份 %BAK% ，请勿删除补丁文件夹里的 _ORIGINAL_ 文件。 & pause & exit 1',
    'attrib -r "!GAME!\\%REL%" >nul 2>nul',
    'copy /y "%PKG%%BAK%" "!GAME!\\%REL%" >nul',
    'if errorlevel 1 (echo [失败] %REL% —— 系统返回： & copy /y "%PKG%%BAK%" "!GAME!\\%REL%" & set /a FAILED+=1) else (echo [还原] %REL%)',
    "exit /b 0",
    "",
]


def write_gbk_bat(path, lines):
    text = "\r\n".join(lines)
    data = text.encode("gbk")
    # GBK 往返一致性校验
    assert data.decode("gbk") == text, "GBK 往返不一致：" + path
    with open(path, "wb") as f:
        f.write(data)
    print(os.path.basename(path), "GBK", len(data), "字节，往返一致")


write_gbk_bat(os.path.join(REL, "安装.bat"), INSTALL)
write_gbk_bat(os.path.join(REL, "卸载.bat"), UNINSTALL)
print(">>> bat 生成完成")
