# GTA4 旧汉化 / 死文件扫描隔离脚本（由发布包生成）
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
