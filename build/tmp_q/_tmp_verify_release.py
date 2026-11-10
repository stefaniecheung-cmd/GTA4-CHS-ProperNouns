# -*- coding: utf-8 -*-
"""发布包离线校验：载荷/主补丁/数据文件/基底一致性 + bat 逻辑 + 文档文案。"""
import os, hashlib, io

G = r"C:\Game\Grand Theft Auto IV"
REL = os.path.join(G, r"gta4-chs\release\GTA4-CHS-zh")
W = os.path.join(G, r"gta4-chs\build\font_work")
REF = os.path.join(G, r"gta4-chs\reference\第三方补完包v1.0")

OK = 0; FAIL = 0
def chk(c, m):
    global OK, FAIL
    if c: OK += 1; print("  [OK]   " + m)
    else: FAIL += 1; print("  [FAIL] " + m)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def eq(a, b):
    return os.path.exists(a) and os.path.exists(b) and md5(a) == md5(b)

print("=== 1. 翻译资产 == 源产物 ===")
pay = [
    (os.path.join(W, "char_table_new.dat"), r"plugins\GTA4.CHS\char_table.dat"),
    (os.path.join(W, "fonts_pc_new.wtd"), r"update\pc\textures\fonts.wtd"),
    (os.path.join(W, "fonts_TLAD_new.wtd"), r"update\TLAD\pc\textures\fonts.wtd"),
    (os.path.join(W, "fonts_TBoGT_new.wtd"), r"update\TBoGT\pc\textures\fonts.wtd"),
    (os.path.join(G, r"update\common\text\american.gxt"), r"update\common\text\american.gxt"),
    (os.path.join(G, r"update\TLAD\common\text\american.gxt"), r"update\TLAD\common\text\american.gxt"),
    (os.path.join(G, r"update\TBoGT\common\text\american.gxt"), r"update\TBoGT\common\text\american.gxt"),
]
for src, rel in pay:
    chk(eq(src, os.path.join(REL, rel)), rel)

print("=== 2. 主补丁 / 数据文件 == 游戏目录现装 ===")
plug = [
    (r"plugins\GTA4.CHS.asi", "ae1f51ad4d8f"),
    (r"plugins\GTA4.CHS\whm_table.dat", "dccb297e9875"),
    (r"plugins\GTA4.CHS\custom_translations.json", "efebcc7f83fb"),
]
for rel, pref in plug:
    pkg = os.path.join(REL, rel)
    live = os.path.join(G, rel)
    chk(eq(pkg, live), rel + " == 现装")
    chk(md5(pkg).startswith(pref), rel + " 指纹 " + pref)

print("=== 3. mapfix.asi == 参考包 ===")
chk(eq(os.path.join(REF, r"plugins\mapfix.asi"), os.path.join(REL, r"plugins\mapfix.asi")), "plugins\\mapfix.asi")

print("=== 4. _ORIGINAL 基底 == pristine 参考 ===")
orig = [
    ("_ORIGINAL_char_table.dat", "_ORIGINAL_char_table.dat"),
    ("_ORIGINAL_fonts_pc.wtd", "_ORIGINAL_fonts_pc.wtd"),
    ("_ORIGINAL_fonts_tlad.wtd", "_ORIGINAL_fonts_tlad.wtd"),
    ("_ORIGINAL_fonts_tbogt.wtd", "_ORIGINAL_fonts_tbogt.wtd"),
    ("_ORIGINAL_american.gxt", "_ORIGINAL_american.gxt"),
    ("_ORIGINAL_american_tlad.gxt", "_ORIGINAL_american_tlad.gxt"),
    ("_ORIGINAL_american_tbogt.gxt", "_ORIGINAL_american_tbogt.gxt"),
]
for src, dst in orig:
    chk(eq(os.path.join(REF, src), os.path.join(REL, dst)), dst)

print("=== 5. bat 编码与定位逻辑 ===")
def dec(p):
    return open(p, "rb").read().decode("gbk")
for f in ["安装.bat", "卸载.bat"]:
    raw = open(os.path.join(REL, f), "rb").read()
    t = dec(os.path.join(REL, f))
    chk(b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b""), f + " CRLF")
    chk(t.startswith("@echo off\r\nchcp 936 >nul"), f + " 首行 chcp 936")
    chk(":trygame" in t and "GTAIV.exe" in t, f + " 自动定位")
    chk("Rockstar Games\\Grand Theft Auto IV" in t and "libraryfolders.vdf" in t, f + " 注册表+Steam 探测")
    chk("%PKG%.." in t, f + " 相对路径探测")
    chk(any(x > 127 for x in raw), f + " 非纯 ASCII（GBK 中文）")

it = dec(os.path.join(REL, "安装.bat"))
for rel in [r"plugins\GTA4.CHS.asi", r"plugins\GTA4.CHS\char_table.dat",
            r"plugins\GTA4.CHS\whm_table.dat", r"plugins\GTA4.CHS\custom_translations.json",
            r"plugins\mapfix.asi"]:
    chk(rel in it, "安装 复制 " + rel)
chk(":copy_plugin" in it, "安装 复制子过程")
chk("FAILED=0" in it and "attrib -r" in it and "exit /b 1" in it, "安装 失败计数+只读清除+中止")
chk("PKGN" in it and "GAMEN" in it, "安装 解压进游戏目录防呆")
chk("未检测到原汉化补丁" not in it, "安装 已移除强制预装检测")

ut = dec(os.path.join(REL, "卸载.bat"))
chk("_ORIGINAL_" in ut and ":back" in ut, "卸载 基底还原")
chk("GTA4.CHS.asi" in ut and "del /f /q" in ut, "卸载 删除主 asi")
chk("rmdir /s /q" in ut and r"plugins\GTA4.CHS" in ut, "卸载 删除 CHS 文件夹")
chk("mapfix.asi" in ut, "卸载 删除 mapfix")
chk("FAILED=0" in ut and "exit /b 1" in ut, "卸载 失败计数+中止")

print("=== 6. 文档关键文案 ===")
def rd(p):
    return open(p, "rb").read().decode("utf-8-sig")
for f, keys in {
    "使用说明（必读）.txt": ["无需另装原补丁", "GTA4.CHS.asi", "whm_table.dat", "安装.bat", "卸载.bat", "mapfix.asi", "问号", "_ORIGINAL_", "3,624"],
    "更新日志.txt": ["3,624", "44", "11,440", "3,276", "mapfix.asi", "GTA4.CHS.asi"],
    "声明.txt": ["免责", "一切后果由使用者自负", "GTA4.CHS.asi", "商业"],
    "README.md": ["mapfix.asi", "GTA4.CHS.asi", "安装.bat", "禁止任何商业用途"],
}.items():
    t = rd(os.path.join(REL, f))
    for k in keys:
        chk(k in t, f + " 含: " + k)

print("=== 7. 保留英文清单表头 ===")
lst = rd(os.path.join(REL, "有意保留英文清单.tsv"))
chk(lst.splitlines()[0] == "chapter\ttable\tcrc\tenglish\treason", "清单表头正确")
chk(len([x for x in lst.splitlines()[1:] if x.strip()]) > 100, "清单数据行 >100")

print("")
print("================ verify: %d OK / %d FAIL ================" % (OK, FAIL))
raise SystemExit(1 if FAIL else 0)
