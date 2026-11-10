@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
title GTA4 旧汉化 / 死文件 扫描清理
echo ============================================================
echo   GTA4 旧汉化 / 死文件  扫描清理
echo   作用：识别其它旧汉化补丁 / 自研 hook 遗留 / 残留字典图集，
echo         隔离到游戏目录旁的隔离文件夹（不直接删除），
echo         不影响原版多语言文件与其它图形 / 玩法 MOD。
echo ============================================================
echo.
set "PKG=%~dp0"
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
powershell -NoProfile -ExecutionPolicy Bypass -File "%PKG%清理旧汉化.ps1" -Game "!GAME!"
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