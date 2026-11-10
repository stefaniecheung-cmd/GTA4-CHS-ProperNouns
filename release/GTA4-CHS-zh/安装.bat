@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
title GTA4 三章简中汉化包 安装
echo ============================================================
echo   GTA4 三章简中汉化包  安装程序
echo   内容：主补丁 GTA4.CHS.asi + 字符表 + 三章字库图集 +
echo         三章译文字典 gxt + 地图区名修复插件 mapfix.asi
echo   本包自带汉化补丁本体，无需另装原补丁
echo   支持自动定位游戏目录，无需把本文件夹放进游戏目录
echo ============================================================
echo.
set "PKG=%~dp0"
set "FAILED=0"
rem ---- 自动定位游戏本体（以 GTAIV.exe 为准）----
set "GAME="
set "CAND=%PKG%.."
call :trygame
set "CAND=%PKG%..\..\GTAIV"
call :trygame
set "CAND=%PKG%..\..\..\GTAIV"
call :trygame
if not defined GAME (
  if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (set "REGK=HKLM\SOFTWARE\WOW6432Node\Rockstar Games\Grand Theft Auto IV") else (set "REGK=HKLM\SOFTWARE\Rockstar Games\Grand Theft Auto IV")
  for /f "skip=2 tokens=2*" %%a in ('reg query "!REGK!" /v InstallFolder 2^>nul') do set "CAND=%%b"
  if defined CAND call :trygame
)
if not defined GAME for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Valve\Steam" /v SteamPath 2^>nul') do set "STEAM=%%b"
if not defined STEAM set "STEAM=C:\Program Files (x86)\Steam"
if not defined GAME (
  set "STEAM=!STEAM:/=\!"
  call :trysteam "!STEAM!"
  set "VDF=!STEAM!\steamapps\libraryfolders.vdf"
  if exist "!VDF!" for /f "tokens=2" %%p in ('findstr /c:"path" "!VDF!"') do call :trylib %%p
)
if not defined GAME (
  echo [错误] 未能自动定位游戏本体（找不到 GTAIV.exe）。
  echo        解决办法任选其一：
  echo        1. 把本文件夹放进 GTA4 游戏目录，GTAIV.exe 旁边，再运行；
  echo        2. 先用 Steam 启动过一次游戏，让注册表留下路径，再运行。
  echo.
  pause
  exit /b 1
)
echo [信息] 游戏目录：!GAME!
echo.
rem ---- 防呆：包被解压进游戏目录本身时，源=目标 ----
for %%I in ("%PKG%.") do set "PKGN=%%~fI"
for %%I in ("!GAME!.") do set "GAMEN=%%~fI"
if /i "!PKGN!"=="!GAMEN!" (
  echo [错误] 检测到补丁包被解压进了游戏目录本身（安装.bat 与 GTAIV.exe 在同一个目录）。
  echo        请把压缩包重新解压到一个【独立文件夹】，再双击其中的 安装.bat。
  echo.
  pause
  exit /b 1
)
rem ---- 复制主补丁、数据文件与翻译资产 ----
set "REL=plugins\GTA4.CHS.asi"
call :copy_plugin
set "REL=plugins\GTA4.CHS\char_table.dat"
call :copy_plugin
set "REL=plugins\GTA4.CHS\whm_table.dat"
call :copy_plugin
set "REL=plugins\GTA4.CHS\custom_translations.json"
call :copy_plugin
set "REL=plugins\mapfix.asi"
call :copy_plugin
echo.
if not "!FAILED!"=="0" (
  echo [错误] 有 !FAILED! 个文件写入失败，补丁未完整安装！
  echo        常见原因：
  echo        1. 游戏或 Steam 正在运行：请全部关闭后重新运行本程序；
  echo        2. 目标文件只读 / 被云盘同步占用：右键游戏目录属性，取消只读；
  echo        3. 权限不足：右键本安装.bat，选择“以管理员身份运行”；
  echo        4. 杀毒软件拦截：查看杀软日志，把游戏目录加入白名单后重试。
  echo        诊断信息——游戏目录：!GAME!
  pause
  exit /b 1
)
echo [完成] 全部文件安装成功，启动游戏即可。
echo        如需还原，双击本文件夹里的 卸载.bat。
pause
exit /b 0

:trysteam
set "CAND=%~1\steamapps\common\Grand Theft Auto IV\GTAIV"
call :trygame
exit /b 0

:trylib
set "LIB=%~1"
set "LIB=!LIB:\\=\!"
call :trysteam "!LIB!"
exit /b 0

:trygame
if defined GAME exit /b 0
if exist "%CAND%\GTAIV.exe" set "GAME=%CAND%" & exit /b 0
if exist "%CAND%\GTAIV\GTAIV.exe" set "GAME=%CAND%\GTAIV"
exit /b 0

:copy_plugin
if not exist "!GAME!\plugins" mkdir "!GAME!\plugins"
attrib -r "!GAME!\%REL%" >nul 2>nul
copy /y "%PKG%%REL%" "!GAME!\%REL%" >nul
if errorlevel 1 (echo [失败] %REL% —— 系统返回： & copy /y "%PKG%%REL%" "!GAME!\%REL%" & set /a FAILED+=1) else (echo [成功] %REL%)
exit /b 0
