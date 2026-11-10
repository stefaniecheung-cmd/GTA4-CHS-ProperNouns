#!/usr/bin/env bash
# GTA4 三章简中汉化包 — Linux/SteamOS(Proton Windows 版) 安装脚本
set -euo pipefail
PKG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GAME="${GTA4_DIR:-}"

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
copy_file "plugins/GTA4.CHS.asi"
copy_file "plugins/GTA4.CHS/char_table.dat"
copy_file "plugins/GTA4.CHS/whm_table.dat"
copy_file "plugins/GTA4.CHS/custom_translations.json"
copy_file "plugins/mapfix.asi"

echo "---- 覆盖三章字典与字库图集（update 层）----"
copy_file "update/pc/textures/fonts.wtd"
copy_file "update/TLAD/pc/textures/fonts.wtd"
copy_file "update/TBoGT/pc/textures/fonts.wtd"
copy_file "update/common/text/american.gxt"
copy_file "update/TLAD/common/text/american.gxt"
copy_file "update/TBoGT/common/text/american.gxt"

if [ "$FAILED" -ne 0 ]; then
  echo "[错误] 有 $FAILED 个文件写入失败，请确认游戏已关闭、目录可写后重试。"
  exit 1
fi
echo "[完成] 全部文件安装成功，启动游戏即可。卸载运行 uninstall.sh。"
