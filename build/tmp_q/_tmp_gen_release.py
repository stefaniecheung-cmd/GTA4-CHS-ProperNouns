# -*- coding: utf-8 -*-
"""生成发布包 安装.bat / 卸载.bat（GBK + CRLF，三级定位游戏目录）。
本包自洽：自带主补丁 GTA4.CHS.asi 与整个 plugins\\GTA4.CHS 数据文件夹，
另含 mapfix.asi 与 7 个翻译资产（字符表 + 三章字库图集 + 三章译文字典）。
卸载：还原 update 目录 6 个原版基底，删除主 asi、CHS 文件夹、mapfix.asi。"""
import os, hashlib

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

# 安装时覆盖的 update 原版文件（三章字典 + 三章图集；卸载用 _ORIGINAL_ 还原）
INSTALL_OVERWRITE = [
    r"update\pc\textures\fonts.wtd",
    r"update\TLAD\pc\textures\fonts.wtd",
    r"update\TBoGT\pc\textures\fonts.wtd",
    r"update\common\text\american.gxt",
    r"update\TLAD\common\text\american.gxt",
    r"update\TBoGT\common\text\american.gxt",
]

# Linux/SteamOS(Proton) 相对路径（正斜杠），与 Windows 包同一套文件
LN_PLUGIN = [
    "plugins/GTA4.CHS.asi",
    "plugins/GTA4.CHS/char_table.dat",
    "plugins/GTA4.CHS/whm_table.dat",
    "plugins/GTA4.CHS/custom_translations.json",
    "plugins/mapfix.asi",
]
LN_OVERWRITE = [
    "update/pc/textures/fonts.wtd",
    "update/TLAD/pc/textures/fonts.wtd",
    "update/TBoGT/pc/textures/fonts.wtd",
    "update/common/text/american.gxt",
    "update/TLAD/common/text/american.gxt",
    "update/TBoGT/common/text/american.gxt",
]
LN_RESTORE = [
    ("update/pc/textures/fonts.wtd", "_ORIGINAL_fonts_pc.wtd"),
    ("update/TLAD/pc/textures/fonts.wtd", "_ORIGINAL_fonts_tlad.wtd"),
    ("update/TBoGT/pc/textures/fonts.wtd", "_ORIGINAL_fonts_tbogt.wtd"),
    ("update/common/text/american.gxt", "_ORIGINAL_american.gxt"),
    ("update/TLAD/common/text/american.gxt", "_ORIGINAL_american_tlad.gxt"),
    ("update/TBoGT/common/text/american.gxt", "_ORIGINAL_american_tbogt.gxt"),
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
copy_over_ops = "\r\n".join(
    f'set "REL={rel}"\r\ncall :copy_over' for rel in INSTALL_OVERWRITE
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
    "rem ---- 复制主补丁与 plugins 数据文件 ----",
    copy_plugin_ops,
    "rem ---- 覆盖三章字典与字库图集（update 层）----",
    copy_over_ops,
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
    ":copy_over",
    'for %%F in ("!GAME!\\%REL%") do set "OD=%%~dpF"',
    'if not exist "!OD!" mkdir "!OD!"',
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


CLEAN = [
    "@echo off",
    "chcp 936 >nul",
    "setlocal enabledelayedexpansion",
    "title GTA4 旧汉化 / 死文件 扫描清理",
    "echo ============================================================",
    "echo   GTA4 旧汉化 / 死文件  扫描清理",
    "echo   作用：识别其它旧汉化补丁 / 自研 hook 遗留 / 残留字典图集，",
    "echo         隔离到游戏目录旁的隔离文件夹（不直接删除），",
    "echo         不影响原版多语言文件与其它图形 / 玩法 MOD。",
    "echo ============================================================",
    "echo.",
    'set "PKG=%~dp0"',
    *LOCATE,
    'powershell -NoProfile -ExecutionPolicy Bypass -File "%PKG%清理旧汉化.ps1" -Game "!GAME!"',
    "pause",
    "exit /b 0",
    "",
    *LOCATE_SUBS,
]

PS1 = r'''# GTA4 旧汉化 / 死文件扫描隔离脚本（由发布包生成）
# 参数: -Game 游戏目录; -Apply 直接隔离（默认先预览并询问）
param(
  [Parameter(Mandatory=$true)][string]$Game,
  [switch]$Apply
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path (Join-Path $Game "GTAIV.exe"))) {
  Write-Host "[错误] 目录下找不到 GTAIV.exe：$Game"
  return
}

$stamp = Get-Date -Format "yyyyMMddHHmmss"
$isoRoot = Join-Path $Game ("_chs_old_isolated_" + $stamp)

# 我方补丁白名单（相对路径，小写比较）
$keep = @("plugins\gta4.chs.asi", "plugins\mapfix.asi")
$keepDirs = @("plugins\gta4.chs")
# 原版多语言 gxt 基名（不视为汉化残留）
$origLang = @("french", "german", "italian", "japanese", "russian", "spanish")

function Get-Rel([string]$full) {
  return $full.Substring($Game.Length).TrimStart('\')
}

$hits = New-Object System.Collections.ArrayList

# 1. plugins 下疑似旧汉化 ASI
$plug = Join-Path $Game "plugins"
if (Test-Path $plug) {
  Get-ChildItem $plug -File -Filter *.asi -ErrorAction SilentlyContinue | ForEach-Object {
    $rel = (Get-Rel $_.FullName).ToLower()
    if ($keep -contains $rel) { return }
    $bn = $_.BaseName.ToLower()
    if ($bn -match 'chs|chinese|gta4cn|hant|hans|hanzi|^zh|_zh|zh_') {
      [void]$hits.Add([pscustomobject]@{ Path=(Get-Rel $_.FullName); Size=$_.Length; Kind="旧汉化 ASI" })
    }
  }
  # 2. plugins 下疑似旧汉化数据目录
  Get-ChildItem $plug -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $rel = (Get-Rel $_.FullName).ToLower()
    if ($keepDirs -contains $rel) { return }
    $dn = $_.Name.ToLower()
    if ($dn -match 'chs|chinese|gta4cn|hant|hans|glyph|^font') {
      $sum = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
      [void]$hits.Add([pscustomobject]@{ Path=(Get-Rel $_.FullName); Size=[int64]$sum; Kind="旧汉化数据目录" })
    }
  }
}

# 3. 游戏根目录外置汉化目录
Get-ChildItem $Game -Directory -ErrorAction SilentlyContinue | ForEach-Object {
  $dn = $_.Name.ToLower()
  if ($dn -match '^(chs|chinese|zh|gta4cn|hant|hans)$') {
    $sum = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    [void]$hits.Add([pscustomobject]@{ Path=$_.Name; Size=[int64]$sum; Kind="外置汉化目录" })
  }
}

# 4. 基础层 + update 层残留非标准名字典 / 图集 / 汉化索引
#    （跳过隔离目录、update\GTA IV 资源套、原版多语与我方 american 字典）
Get-ChildItem $Game -Recurse -File -Include *.gxt,*.wtd,*.dat -ErrorAction SilentlyContinue | ForEach-Object {
  $rel = Get-Rel $_.FullName
  $low = $rel.ToLower()
  if ($low -like '_chs_old_isolated_*') { return }
  if ($low -like 'update\gta iv\*') { return }
  $bn = $_.BaseName.ToLower()
  if ($origLang -contains $bn) { return }
  if ($bn -like 'american*') { return }
  if ($bn -match 'chinese|zchs|_chs|gta4cn|hant|hanzi|_cn') {
    [void]$hits.Add([pscustomobject]@{ Path=$rel; Size=$_.Length; Kind="残留字典/图集/索引" })
  }
}

# 5. 根目录外置字库 / 字形文件
Get-ChildItem $Game -File -ErrorAction SilentlyContinue | Where-Object {
  $_.Extension.ToLower() -in @(".ttf", ".otf") -or $_.Name.ToLower() -in @("glyphs.dat", "glyphs.bin")
} | ForEach-Object {
  [void]$hits.Add([pscustomobject]@{ Path=$_.Name; Size=$_.Length; Kind="外置字库/字形" })
}

if ($hits.Count -eq 0) {
  Write-Host "未发现旧汉化 / 死文件残留，目录干净。"
  return
}

Write-Host ("发现 {0} 项疑似旧汉化 / 死文件：" -f $hits.Count)
$hits | ForEach-Object { Write-Host ("  [{0}] {1}  ({2} B)" -f $_.Kind, $_.Path, $_.Size) }
Write-Host ""

$doApply = $Apply
if (-not $Apply) {
  $ans = Read-Host "是否将以上项目隔离到隔离文件夹？(Y/N，默认 N)"
  $doApply = ($ans.Trim().ToUpper() -eq "Y")
}

if (-not $doApply) {
  Write-Host "已取消，未移动任何文件。"
  return
}

New-Item -ItemType Directory -Force $isoRoot | Out-Null
$lines = @("隔离清单  生成时间: $(Get-Date)", "游戏目录: $Game", "")
foreach ($h in $hits) {
  $src = Join-Path $Game $h.Path
  $dst = Join-Path $isoRoot $h.Path
  if (Test-Path $src) {
    $dstDir = Split-Path $dst -Parent
    New-Item -ItemType Directory -Force $dstDir | Out-Null
    Move-Item $src $dst -Force
    $md5 = ""
    if (-not (Test-Path $dst -PathType Container)) {
      try { $md5 = (Get-FileHash $dst -Algorithm MD5).Hash.Substring(0,12).ToLower() } catch {}
    }
    $lines += ("{0}`t{1}`t{2}`t{3}" -f $h.Kind, $h.Path, $h.Size, $md5)
  }
}
$report = Join-Path $isoRoot "隔离清单.txt"
$lines | Set-Content -Encoding UTF8 $report
Write-Host ""
Write-Host ("已隔离到: {0}" -f $isoRoot)
Write-Host "清单: 隔离清单.txt。请进游戏验证显示正常后，再手动删除该隔离目录。"
'''

# ---- Linux/SteamOS(Proton) bash 脚本 ----
LN_LOCATE = r'''
locate_game() {
  local roots=(
    "$HOME/.local/share/Steam/steamapps/common/Grand Theft Auto IV"
    "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Grand Theft Auto IV"
  )
  local vdf lib
  for vdf in \
    "$HOME/.local/share/Steam/steamapps/libraryfolders.vdf" \
    "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/libraryfolders.vdf"; do
    [ -f "$vdf" ] || continue
    while IFS= read -r lib; do
      lib="${lib//\\\\//}"
      roots+=("$lib/steamapps/common/Grand Theft Auto IV")
    done < <(grep -oP '"path"\s*"\K[^"]+' "$vdf" 2>/dev/null || true)
  done
  local r
  for r in "${roots[@]}"; do
    if [ -f "$r/GTAIV.exe" ]; then GAME="$r"; return 0; fi
    if [ -f "$r/GTAIV/GTAIV.exe" ]; then GAME="$r/GTAIV"; return 0; fi
  done
  return 1
}
'''

LN_INSTALL = r'''#!/usr/bin/env bash
# GTA4 三章简中汉化包 — Linux/SteamOS(Proton Windows 版) 安装脚本
set -euo pipefail
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GAME="${GTA4_DIR:-}"
''' + LN_LOCATE + r'''
if [ -z "$GAME" ]; then locate_game || true; fi
if [ -z "$GAME" ] || [ ! -f "$GAME/GTAIV.exe" ]; then
  echo "[错误] 未能自动定位游戏目录（找不到 GTAIV.exe）。"
  echo "       可手动指定：GTA4_DIR=/路径/到/Grand\ Theft\ Auto\ IV bash install.sh"
  exit 1
fi
echo "[信息] 游戏目录：$GAME"

if [ "$PKG" = "$GAME" ]; then
  echo "[错误] 补丁包不能解压进游戏目录本身，请解压到独立文件夹再运行。"
  exit 1
fi

FAILED=0
copy_file() {
  local rel="$1"
  mkdir -p "$GAME/$(dirname "$rel")"
  if cp -f "$PKG/$rel" "$GAME/$rel"; then
    echo "[成功] $rel"
  else
    echo "[失败] $rel"
    FAILED=$((FAILED+1))
  fi
}

echo "---- 安装主补丁与 plugins 数据 ----"
''' + "\n".join(f'copy_file "{r}"' for r in LN_PLUGIN) + r'''

echo "---- 覆盖三章字典与字库图集（update 层）----"
''' + "\n".join(f'copy_file "{r}"' for r in LN_OVERWRITE) + r'''

if [ "$FAILED" -ne 0 ]; then
  echo "[错误] 有 $FAILED 个文件写入失败，请确认游戏已关闭、目录可写后重试。"
  exit 1
fi
echo "[完成] 全部文件安装成功，启动游戏即可。卸载运行 uninstall.sh。"
'''

LN_UNINSTALL = r'''#!/usr/bin/env bash
# GTA4 三章简中汉化包 — Linux/SteamOS 卸载脚本
set -euo pipefail
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GAME="${GTA4_DIR:-}"
''' + LN_LOCATE + r'''
if [ -z "$GAME" ]; then locate_game || true; fi
if [ -z "$GAME" ] || [ ! -f "$GAME/GTAIV.exe" ]; then
  echo "[错误] 未能自动定位游戏目录（找不到 GTAIV.exe）。"
  echo "       可手动指定：GTA4_DIR=/路径/到/Grand\ Theft\ Auto\ IV bash uninstall.sh"
  exit 1
fi
echo "[信息] 游戏目录：$GAME"

FAILED=0
restore() {
  local rel="$1" bak="$2"
  if [ ! -f "$PKG/$bak" ]; then echo "[错误] 缺少基底 $bak（请勿删除 _ORIGINAL_ 文件）"; FAILED=$((FAILED+1)); return; fi
  mkdir -p "$GAME/$(dirname "$rel")"
  if cp -f "$PKG/$bak" "$GAME/$rel"; then echo "[还原] $rel"; else echo "[失败] $rel"; FAILED=$((FAILED+1)); fi
}
''' + "\n".join(f'restore "{rel}" "{bak}"' for rel, bak in LN_RESTORE) + r'''

rm -f "$GAME/plugins/GTA4.CHS.asi" && echo "[成功] 删除 plugins/GTA4.CHS.asi"
rm -rf "$GAME/plugins/GTA4.CHS" && echo "[成功] 删除 plugins/GTA4.CHS"
rm -f "$GAME/plugins/mapfix.asi" && echo "[成功] 删除 plugins/mapfix.asi"

if [ "$FAILED" -ne 0 ]; then
  echo "[错误] 有 $FAILED 个文件还原 / 删除失败，请关闭游戏后重试。"
  exit 1
fi
echo "[完成] 已还原为原版英文状态。"
'''

LN_CLEAN = r'''#!/usr/bin/env bash
# GTA4 旧汉化 / 死文件扫描隔离（Linux/SteamOS）。默认预览并询问，--apply 直接隔离。
set -euo pipefail
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GAME="${GTA4_DIR:-}"
''' + LN_LOCATE + r'''
if [ -z "$GAME" ]; then locate_game || true; fi
if [ -z "$GAME" ] || [ ! -f "$GAME/GTAIV.exe" ]; then
  echo "[错误] 找不到 GTAIV.exe，可用 GTA4_DIR=... 指定。"; exit 1
fi

APPLY=0; [ "${1:-}" = "--apply" ] && APPLY=1
STAMP="$(date +%Y%m%d%H%M%S)"
ISODEPOT="$GAME/_chs_old_isolated_$STAMP"

keep_file="plugins/gta4.chs.asi plugins/mapfix.asi"
keep_dir="plugins/gta4.chs"
orig_lang="french german italian japanese russian spanish"
hits=()
add_hit() { hits+=("$1|$2|$3"); }

# 1. plugins 下疑似旧汉化 ASI
if [ -d "$GAME/plugins" ]; then
  for f in "$GAME/plugins"/*.asi; do
    [ -e "$f" ] || continue
    rel="${f#$GAME/}"; low="$(echo "$rel" | tr 'A-Z' 'a-z')"
    case " $keep_file " in *" $low "*) continue;; esac
    bn="$(basename "$f" .asi | tr 'A-Z' 'a-z')"
    if [[ "$bn" =~ chs|chinese|gta4cn|hant|hans|hanzi|^zh|_zh|zh_ ]]; then
      add_hit "旧汉化 ASI" "$rel" "$(stat -c%s "$f")"
    fi
  done
  # 2. plugins 下疑似旧汉化数据目录
  for d in "$GAME/plugins"/*/; do
    [ -d "$d" ] || continue
    rel="${d#$GAME/}"; rel="${rel%/}"; low="$(echo "$rel" | tr 'A-Z' 'a-z')"
    [ "$low" = "$keep_dir" ] && continue
    dn="$(basename "$d" | tr 'A-Z' 'a-z')"
    if [[ "$dn" =~ chs|chinese|gta4cn|hant|hans|glyph|^font ]]; then
      sz="$(find "$d" -type f -printf '%s\n' | awk '{s+=$1} END{print s+0}')"
      add_hit "旧汉化数据目录" "$rel" "$sz"
    fi
  done
fi

# 3. 游戏根目录外置汉化目录
for d in "$GAME"/*/; do
  [ -d "$d" ] || continue
  dn="$(basename "$d" | tr 'A-Z' 'a-z')"
  case "$dn" in
    chs|chinese|zh|gta4cn|hant|hans)
      rel="${d#$GAME/}"; rel="${rel%/}"
      sz="$(find "$d" -type f -printf '%s\n' | awk '{s+=$1} END{print s+0}')"
      add_hit "外置汉化目录" "$rel" "$sz";;
  esac
done

# 4. 基础层 + update 层残留非标准名字典 / 图集 / 汉化索引
#    （跳过隔离目录、update/GTA IV 资源套、原版多语与我方 american 字典）
while IFS= read -r f; do
  rel="${f#$GAME/}"; low="$(echo "$rel" | tr 'A-Z' 'a-z')"
  case "$low" in _chs_old_isolated_*|update/gta\ iv/*) continue;; esac
  bn="$(basename "$f" | sed 's/\.[^.]*$//' | tr 'A-Z' 'a-z')"
  case " $orig_lang " in *" $bn "*) continue;; esac
  case "$bn" in american*) continue;; esac
  if [[ "$bn" =~ chinese|zchs|_chs|gta4cn|hant|hanzi|_cn ]]; then
    add_hit "残留字典/图集/索引" "$rel" "$(stat -c%s "$f")"
  fi
done < <(find "$GAME" -type f \( -iname '*.gxt' -o -iname '*.wtd' -o -iname '*.dat' \) ! -path '*/_chs_old_isolated_*')

# 5. 根目录外置字库 / 字形文件
for f in "$GAME"/*.ttf "$GAME"/*.otf "$GAME"/glyphs.dat "$GAME"/glyphs.bin; do
  [ -e "$f" ] || continue
  add_hit "外置字库/字形" "${f#$GAME/}" "$(stat -c%s "$f")"
done

if [ ${#hits[@]} -eq 0 ]; then
  echo "未发现旧汉化 / 死文件残留，目录干净。"; exit 0
fi

echo "发现 ${#hits[@]} 项疑似旧汉化 / 死文件："
for h in "${hits[@]}"; do IFS='|' read -r kind rel sz <<< "$h"; echo "  [$kind] $rel  ($sz B)"; done
echo

if [ "$APPLY" -ne 1 ]; then
  read -r -p "是否隔离以上项目？(Y/N，默认 N) " ans
  case "${ans:-N}" in Y|y) ;; *) echo "已取消，未移动任何文件。"; exit 0;; esac
fi

mkdir -p "$ISODEPOT"
report="$ISODEPOT/隔离清单.txt"
{ echo "隔离清单  生成时间: $(date)"; echo "游戏目录: $GAME"; echo; } > "$report"
for h in "${hits[@]}"; do
  IFS='|' read -r kind rel sz <<< "$h"
  src="$GAME/$rel"; dst="$ISODEPOT/$rel"
  [ -e "$src" ] || continue
  mkdir -p "$(dirname "$dst")"
  mv -f "$src" "$dst"
  md5=""
  if [ -f "$dst" ]; then md5="$(md5sum "$dst" | cut -c1-12)"; fi
  printf '%s\t%s\t%s\t%s\n' "$kind" "$rel" "$sz" "$md5" >> "$report"
done
echo
echo "已隔离到: $ISODEPOT"
echo "清单: 隔离清单.txt。进游戏验证正常后再手动删除该隔离目录。"
'''


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
write_gbk_bat(os.path.join(REL, "清理旧汉化.bat"), CLEAN)

# PS1 用 UTF-8 BOM + CRLF，保证 PowerShell 5.1 正确读取中文
ps1_path = os.path.join(REL, "清理旧汉化.ps1")
ps1_text = PS1.replace("\n", "\r\n")
with open(ps1_path, "wb") as f:
    f.write(b"\xEF\xBB\xBF" + ps1_text.encode("utf-8"))
print(os.path.basename(ps1_path), "UTF-8 BOM", len(ps1_text.encode("utf-8")), "字节")

def write_sh(name, text):
    p = os.path.join(REL, name)
    data = text.replace("\r\n", "\n").encode("utf-8")
    with open(p, "wb") as f:
        f.write(data)
    print(name, "UTF-8 LF", len(data), "字节")

write_sh("install.sh", LN_INSTALL)
write_sh("uninstall.sh", LN_UNINSTALL)
write_sh("cleanup_old_zh.sh", LN_CLEAN)

# ---- 方案 B：烘焙英文原版基底（卸载显式还原英文）----
# 基础层（common / TLAD / TBoGT 目录）未被汉化补丁覆盖，是本机可靠的英文原版。
# 旧包内 _ORIGINAL_* 经条目级解析为旧汉化备份，此处整体替换为基础层英文原版。
import shutil
GAME = r"C:\Game\Grand Theft Auto IV"
BAKE = [
    (r"common\text\american.gxt", "_ORIGINAL_american.gxt"),
    (r"TLAD\common\text\american.gxt", "_ORIGINAL_american_tlad.gxt"),
    (r"TBoGT\common\text\american.gxt", "_ORIGINAL_american_tbogt.gxt"),
    (r"pc\textures\fonts.wtd", "_ORIGINAL_fonts_pc.wtd"),
    (r"TLAD\pc\textures\fonts.wtd", "_ORIGINAL_fonts_tlad.wtd"),
    (r"TBoGT\pc\textures\fonts.wtd", "_ORIGINAL_fonts_tbogt.wtd"),
]

def _md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

for src_rel, dst in BAKE:
    src = os.path.join(GAME, src_rel)
    dstp = os.path.join(REL, dst)
    if not os.path.exists(src):
        raise SystemExit("缺少基础层原版文件：" + src)
    shutil.copyfile(src, dstp)
    if _md5(src) != _md5(dstp):
        raise SystemExit("基底拷贝哈希不一致：" + dst)
    print("基底", dst, "<-", src_rel, _md5(dstp)[:12])

# char_table.dat 属补丁数据目录，卸载随整个 plugins\GTA4.CHS 删除，无需原版基底；
# 旧包内冗余的 _ORIGINAL_char_table.dat 移除。
_ct = os.path.join(REL, "_ORIGINAL_char_table.dat")
if os.path.exists(_ct):
    os.remove(_ct)
    print("移除冗余 _ORIGINAL_char_table.dat")

print(">>> bat / ps1 / sh 生成完成")

# ---- 打包 + 回读校验 ----
import zipfile
RELROOT = os.path.dirname(REL)
PKG = "GTA4-CHS-zh"

def pack_zip(out):
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, _, files in os.walk(REL):
            for fn in files:
                fp = os.path.join(root, fn)
                arc = PKG + "/" + os.path.relpath(fp, REL).replace(os.sep, "/")
                z.write(fp, arc)

def _hash(p):
    b = open(p, "rb").read()
    return hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest(), len(b)

DISK = {}
for root, _, files in os.walk(REL):
    for fn in files:
        fp = os.path.join(root, fn)
        rel = PKG + "/" + os.path.relpath(fp, REL).replace(os.sep, "/")
        DISK[rel] = os.path.getsize(fp)

ZIPS = [
    os.path.join(RELROOT, "GTA4-CHS-zh-v2.1.zip"),
    os.path.join(RELROOT, "GTA4三章简中翻译资产包.zip"),
]
for z in ZIPS:
    pack_zip(z)
    md5, sha, n = _hash(z)
    with zipfile.ZipFile(z) as zf:
        names = {i.filename: i.file_size for i in zf.infolist()}
    assert set(names) == set(DISK), "条目不一致：" + z
    for k, v in DISK.items():
        assert names[k] == v, "大小不一致：" + k
    print("打包", os.path.basename(z), n, "B", "条目", len(names),
          "MD5", md5[:12], "回读大小逐项一致")
