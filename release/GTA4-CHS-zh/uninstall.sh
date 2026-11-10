#!/usr/bin/env bash
# GTA4 三章简中汉化包 — Linux/SteamOS 卸载脚本
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
restore "update/pc/textures/fonts.wtd" "_ORIGINAL_fonts_pc.wtd"
restore "update/TLAD/pc/textures/fonts.wtd" "_ORIGINAL_fonts_tlad.wtd"
restore "update/TBoGT/pc/textures/fonts.wtd" "_ORIGINAL_fonts_tbogt.wtd"
restore "update/common/text/american.gxt" "_ORIGINAL_american.gxt"
restore "update/TLAD/common/text/american.gxt" "_ORIGINAL_american_tlad.gxt"
restore "update/TBoGT/common/text/american.gxt" "_ORIGINAL_american_tbogt.gxt"

rm -f "$GAME/plugins/GTA4.CHS.asi" && echo "[成功] 删除 plugins/GTA4.CHS.asi"
rm -rf "$GAME/plugins/GTA4.CHS" && echo "[成功] 删除 plugins/GTA4.CHS"
rm -f "$GAME/plugins/mapfix.asi" && echo "[成功] 删除 plugins/mapfix.asi"

if [ "$FAILED" -ne 0 ]; then
  echo "[错误] 有 $FAILED 个文件还原 / 删除失败，请关闭游戏后重试。"
  exit 1
fi
echo "[完成] 已还原为原版英文状态。"
