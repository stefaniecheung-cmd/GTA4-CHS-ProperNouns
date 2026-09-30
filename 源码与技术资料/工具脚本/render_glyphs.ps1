# 渲染字形。像素统计走内联 C#（PowerShell 逐像素循环慢得没法用），
# 默认不落盘整幅画布 —— 之前那样每个文件被填到 26 MB，236 个就吃掉 6 GB。
# 用 FontFamily 对象而不是名字字符串：名字字符串会被 GDI+ 静默回落到默认字体。
param(
  [string]$Sizes = '64',
  [string]$CodePoints = '22269,27704',
  [string]$Weights = 'Regular,Bold',
  [string]$Hints = 'AntiAliasGridFit',
  [string]$OutSub = 'render',
  [string]$OnlyFamily = '',
  [switch]$WritePixels
)
# powershell -File 传参不会把 "1,2,3" 解析成数组，只能自己拆
$sizeList   = @($Sizes.Split(',')       | ForEach-Object { [int]$_ })
$cpList     = @($CodePoints.Split(',')  | ForEach-Object { [int]$_ })
$weightList = @($Weights.Split(','))
$hintList   = @($Hints.Split(','))
Add-Type -AssemblyName System.Drawing

$src = @'
using System;
public static class GlyphUtil {
    public static long[] Stats(byte[] b, int w, int h) {
        int minx = int.MaxValue, maxx = -1, miny = int.MaxValue, maxy = -1;
        long ink = 0;
        for (int y = 0; y < h; y++) {
            int rb = y * w * 4 + 3;
            for (int x = 0; x < w; x++) {
                byte a = b[rb + x * 4];
                if (a > 0) {
                    if (x < minx) minx = x;
                    if (x > maxx) maxx = x;
                    if (y < miny) miny = y;
                    if (y > maxy) maxy = y;
                    ink += a;
                }
            }
        }
        return new long[] { minx == int.MaxValue ? -1 : minx, maxx, miny == int.MaxValue ? -1 : miny, maxy, ink };
    }
    public static byte[] Alpha(byte[] b, int w, int h) {
        byte[] o = new byte[w * h];
        for (int i = 0; i < w * h; i++) o[i] = b[i * 4 + 3];
        return o;
    }
}
'@
Add-Type -TypeDefinition $src -Language CSharp

$CanvW = 160; $CanvH = 160; $OX = 32.0; $OY = 24.0
$outDir = Join-Path $PSScriptRoot $OutSub
if (Test-Path $outDir) { Remove-Item $outDir -Recurse -Force }
New-Item -ItemType Directory -Path $outDir | Out-Null

$fc = New-Object System.Drawing.Text.InstalledFontCollection
$cands = @()
foreach ($f in $fc.Families) {
  if ($OnlyFamily -ne '') { if ($f.Name -eq $OnlyFamily) { $cands += $f }; continue }
  $n = $f.Name
  $isCjkName = $false
  foreach ($fch in $n.ToCharArray()) { if ([int]$fch -gt 127) { $isCjkName = $true; break } }
  if ($isCjkName -or $n -match '^(Noto|Source Han|MiSans|Microsoft YaHei|Microsoft JhengHei|Malgun|Yu Gothic|SimSun|SimHei|DengXian|MS Gothic|MS Mincho|Meiryo|Batang|Gulim|Dotum)') {
    $cands += $f
  }
}
Write-Output ("候选字族 " + $cands.Count + " 个")

$sf = [System.Drawing.StringFormat]::GenericTypographic
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255,255,255,255))
$rect = New-Object System.Drawing.Rectangle(0,0,$CanvW,$CanvH)
$raw = New-Object byte[] ($CanvW*$CanvH*4)

$manifest = New-Object System.Collections.ArrayList
$idx = 0
foreach ($fam in $cands) {
  foreach ($wname in $weightList) {
    $style = [System.Drawing.FontStyle]::$wname
    if (-not $fam.IsStyleAvailable($style)) { continue }
    foreach ($sz in $sizeList) {
      $font = $null
      try { $font = New-Object System.Drawing.Font($fam, [single]$sz, $style, [System.Drawing.GraphicsUnit]::Pixel) } catch { continue }
      foreach ($ht in $hintList) {
        foreach ($cp in $cpList) {
          $text = [char]::ConvertFromUtf32($cp)
          $bmp = New-Object System.Drawing.Bitmap($CanvW, $CanvH, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
          $g = [System.Drawing.Graphics]::FromImage($bmp)
          $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::$ht
          $g.Clear([System.Drawing.Color]::FromArgb(0,0,0,0))
          $g.DrawString($text, $font, $brush, [single]$OX, [single]$OY, $sf)
          $g.Dispose()
          $data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
          [System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $raw, 0, $raw.Length)
          $bmp.UnlockBits($data)
          $bmp.Dispose()

          $st = [GlyphUtil]::Stats($raw, $CanvW, $CanvH)
          $fname = '-'
          if ($WritePixels) {
            $fname = "r{0:d5}.bin" -f $idx
            [System.IO.File]::WriteAllBytes((Join-Path $outDir $fname), [GlyphUtil]::Alpha($raw, $CanvW, $CanvH))
          }
          [void]$manifest.Add(("{0}`t{1}`t{2}`t{3}`t{4}`t{5}`t{6}`t{7}`t{8}`t{9}`t{10}`t{11}`t{12}" -f `
            $idx, $fam.Name, $font.Name, $wname, $sz, $ht, $cp, $st[0], $st[1], $st[2], $st[3], $st[4], $fname))
          $idx++
        }
      }
      $font.Dispose()
    }
  }
}
Write-Output ("渲染 " + $idx + " 个样本")
$enc = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllLines((Join-Path $outDir 'manifest.tsv'), $manifest, $enc)
