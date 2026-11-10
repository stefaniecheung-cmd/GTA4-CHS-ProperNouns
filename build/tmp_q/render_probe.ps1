# Render probe: Noto Sans SC Bold in 64x66 cell, report bbox/ink. Pure ASCII, code points passed in.
Add-Type -AssemblyName System.Drawing

$src = @'
using System;
public static class G {
  public static long[] Stats(byte[] b, int w, int h) {
    int minx=int.MaxValue,maxx=-1,miny=int.MaxValue,maxy=-1,ink=0;
    for(int y=0;y<h;y++){int rb=y*w*4+3;
      for(int x=0;x<w;x++){byte a=b[rb+x*4]; if(a>0){if(x<minx)minx=x; if(x>maxx)maxx=x; if(y<miny)miny=y; if(y>maxy)maxy=y; ink+=a;}}}
    return new long[]{minx==int.MaxValue?-1:minx,maxx,miny==int.MaxValue?-1:miny,maxy,ink};
  }
}
'@
Add-Type -TypeDefinition $src -Language CSharp

$CellW=64; $CellH=66
$fam=(New-Object System.Drawing.Text.InstalledFontCollection).Families | Where-Object { $_.Name -eq 'Noto Sans SC' }
$sf=[System.Drawing.StringFormat]::GenericTypographic
$brush=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255,255,255,255))
$raw=New-Object byte[] ($CellW*$CellH*4)
$rect=New-Object System.Drawing.Rectangle(0,0,$CellW,$CellH)

$size=[single]$args[0]; $dx=[single]$args[1]; $dy=[single]$args[2]
$cps=@(0x7684,0x662F,0x6211,0x4F60,0x4EBA,0x4E2D,0x5927,0x4E2A)
$font=New-Object System.Drawing.Font($fam,$size,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
Write-Output ("font.Name=" + $font.Name + " size=" + $size + " dx=" + $dx + " dy=" + $dy)

foreach($cp in $cps){
  $glyph=[char]::ConvertFromUtf32($cp)
  $bmp=New-Object System.Drawing.Bitmap($CellW,$CellH,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g=[System.Drawing.Graphics]::FromImage($bmp)
  $g.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.Clear([System.Drawing.Color]::FromArgb(0,0,0,0))
  $g.DrawString($glyph,$font,$brush,$dx,$dy,$sf)
  $g.Dispose()
  $data=$bmp.LockBits($rect,[System.Drawing.Imaging.ImageLockMode]::ReadOnly,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  [System.Runtime.InteropServices.Marshal]::Copy($data.Scan0,$raw,0,$raw.Length)
  $bmp.UnlockBits($data)
  $st=[G]::Stats($raw,$CellW,$CellH)
  $w=$st[1]-$st[0]+1; $h=$st[3]-$st[2]+1
  Write-Output ("U+{0:X4}  x[{1},{2}] y[{3},{4}] w={5} h={6} ink={7}" -f $cp,$st[0],$st[1],$st[2],$st[3],$w,$h,$st[4])
  $out=Join-Path $PSScriptRoot ("probe_{0:X4}.png" -f $cp)
  $bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
}
$font.Dispose()
