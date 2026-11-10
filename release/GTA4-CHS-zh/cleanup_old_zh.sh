#!/usr/bin/env bash
# GTA4 旧汉化 / 死文件扫描隔离（Linux/SteamOS）。默认预览并询问，--apply 直接隔离。
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
