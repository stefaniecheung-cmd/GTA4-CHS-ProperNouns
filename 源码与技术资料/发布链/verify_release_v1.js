/* verify_release_v1.js - v1.0 发布包 + 项目收尾文件夹 离线校验。
   断言：载荷/回滚基底与 成品包v7 逐字节一致；安装.bat 纯ASCII+CRLF 且含原补丁检测与链接；
   卸载.bat 与 v7 一致；声明/使用说明/更新日志 必需文案逐字在位；对照表与未翻译清单同源于工程权威文件；
   项目收尾四文档齐备；未生成 zip。 */
const fs = require('fs');
const PROJ = 'E:/SteamLibrary/steamapps/common/Grand Theft Auto IV/汉化补丁工程/';
const B = PROJ + '03-补丁构建/';
const V7 = B + '成品包v7/';
const REL = PROJ + 'GTA4汉化补丁之补丁（含AI翻译）v1.0/';
const FIN = PROJ + '项目收尾/';
let OK = 0, FAIL = 0;
function chk(c, m) { if (c) { OK++; console.log('  [OK]   ' + m); } else { FAIL++; console.log('  [FAIL] ' + m); } }
const ex = p => fs.existsSync(p);
const eq = (a, b) => ex(a) && ex(b) && fs.readFileSync(a).equals(fs.readFileSync(b));
const rd = p => ex(p) ? fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, '') : '';

console.log('=== 1. 载荷与回滚基底 == 成品包v7 ===');
const PAY = [
  'plugins/GTA4.CHS/char_table.dat', 'plugins/mapfix.asi',
  'update/pc/textures/fonts.wtd', 'update/TLAD/pc/textures/fonts.wtd', 'update/TBoGT/pc/textures/fonts.wtd',
  'update/common/text/american.gxt', 'update/TLAD/common/text/american.gxt', 'update/TBoGT/common/text/american.gxt',
  '_ORIGINAL_char_table.dat', '_ORIGINAL_fonts_pc.wtd', '_ORIGINAL_fonts_tlad.wtd', '_ORIGINAL_fonts_tbogt.wtd',
  '_ORIGINAL_american.gxt', '_ORIGINAL_american_tlad.gxt', '_ORIGINAL_american_tbogt.gxt',
];
for (const p of PAY) chk(eq(REL + p, V7 + p), p + ' == 成品包v7');

console.log('=== 2. 安装.bat / 卸载.bat（GBK 中文提示 + 自动定位 + 原补丁检测）===');
const decGbk = p => new TextDecoder('gbk').decode(fs.readFileSync(p));
for (const f of ['安装.bat', '卸载.bat']) {
  const raw = fs.readFileSync(REL + f);
  const t = decGbk(REL + f);
  chk(raw.includes(Buffer.from('\r\n')) && !/[^\r]\n/.test(t), f + ' CRLF');
  chk(/^@echo off\r?\nchcp 936 >nul/.test(t), f + ' 首行 chcp 936（GBK 中文提示）');
  chk(t.includes('[错误]') && t.includes('[完成]'), f + ' 中文提示在位');
  chk(!fs.readFileSync(REL + f).every(x => x < 128), f + ' 非纯 ASCII（确为中文编码）');
  chk(!t.includes('GTA4.CHS-master') && !t.includes('汉化补丁工程'), f + ' 不引用工程/源码目录（识别只认游戏目录 GTA4.CHS.asi）');
  chk(t.includes(':trygame') && t.includes('GTAIV.exe'), f + ' 自动定位（GTAIV.exe 存在性判定）');
  chk(t.includes('Rockstar Games\\Grand Theft Auto IV') && t.includes('libraryfolders.vdf') && t.includes('Software\\Valve\\Steam'), f + ' 注册表+Steam 库列表探测');
  chk(t.includes('%PKG%..'), f + ' 相对路径探测（放游戏目录内也兼容）');
}
const it = decGbk(REL + '安装.bat');
chk(it.includes('if exist "!GAME!\\plugins\\GTA4.CHS.asi" goto orig_ok') && it.includes('if exist "!GAME!\\GTA4.CHS.asi" goto orig_ok'), '原补丁检测：plugins 子目录优先 + 根目录兜底（原补丁实际装 plugins\\）');
chk(it.includes('https://github.com/ckeleshi/GTA4.CHS') && it.includes('https://b9348.pages.dev/'), 'GitHub/官网链接在位');
chk(it.includes('未检测到原汉化补丁'), '未检出中文报错在位');
chk(it.includes('exit /b 1') && it.includes(':orig_ok'), '未检出即中止');
chk(it.includes('_ORIGINAL_char_table.dat') && it.includes('mapfix.asi'), '安装覆盖 7 文件+mapfix');
const ut = decGbk(REL + '卸载.bat');
chk(ut.includes('_ORIGINAL_') && /del \/f \/q "!GAME!\\plugins\\mapfix.asi"/.test(ut), '卸载还原+删 mapfix（绝对路径）');
chk(ut.includes('set "FAILED=0"') && ut.includes('exit /b 1'), '卸载失败计数与中止');
chk(it.includes('set "FAILED=0"') && it.includes('attrib -r ') && it.includes('exit /b 1'), '安装失败计数+只读清除+中止');
chk(it.includes('被解压进了游戏目录本身') && it.includes('PKGN') && it.includes('GAMEN'), '防呆：包解压进游戏目录时明确提示并中止');

console.log('=== 3. 声明.txt ===');
const sm = rd(REL + '声明.txt');
chk(sm.includes('本补丁由 Non-ID、华 借助 AI 工具制作'), '制作声明（Non-ID、华 + AI 工具）逐字在位');
chk(sm.includes('ghh213014@163.com'), '反馈邮箱在位');
chk(sm.includes('免责声明') && sm.includes('一切后果由使用者自负'), '免责声明在位');
chk(sm.includes('基于 GTA4 简中补丁 2024-09-13 版 制作'), '基于原补丁声明在位');
chk(sm.includes('无名汉化组') && sm.includes('贴吧吧友') && sm.includes('接棒'), '原补丁沿革（无名汉化组立项→贴吧吧友接棒完工）在位');
chk(sm.includes('本汉化补丁仅供交流学习使用，任何组织或个人不得将此用于任何形式的商业目的，对此产生的一切后果由使用者自负，本组将不对此负任何责任。'), '原汉化补丁声明逐字保留（含"本组将不对此负任何责任"全句）');
chk(sm.includes('不收费') && sm.includes('不引入任何破解'), '免费+不引入破解');
chk(!sm.includes('本补丁是官方'), '不自称官方');

console.log('=== 4. 使用说明.txt / 更新日志.txt ===');
const sy = rd(fs.existsSync(REL + '使用说明（必读）.txt') ? REL + '使用说明（必读）.txt' : REL + '使用说明.txt');
for (const k of ['必须先安装原汉化补丁（2024-09-13 版', '安装.bat', '卸载.bat', '未检测到原汉化补丁', '自动定位游戏本体', 'github.com/ckeleshi/GTA4.CHS', 'mapfix.asi', '问号', '杀毒', '莱尔･里瓦斯 (Lyle)', '未翻译内容清单']) chk(sy.includes(k), '使用说明含: ' + k.slice(0, 30));
const ul = rd(REL + '更新日志.txt');
chk(ul.includes('v1.0') && ul.includes('初版'), '更新日志 v1.0 初版');
chk(ul.includes('1,611') && ul.includes('洛佩兹') && ul.includes('自由城') && ul.includes('3,559') && ul.includes('体检修复') && ul.includes('v7f') && ul.includes('12,372'), '更新日志关键数字在位');

console.log('=== 5. 对照表与未翻译清单同源 ===');
chk(eq(REL + '翻译对照表.md', PROJ + '翻译对照表-最新.md'), '发布包 翻译对照表.md == 翻译对照表-最新.md');
chk(eq(REL + '未翻译内容清单.tsv', FIN + '未翻译内容清单.tsv'), '发布包 未翻译内容清单.tsv == 项目收尾版');
chk(eq(FIN + '翻译对照表-最新.md', PROJ + '翻译对照表-最新.md'), '项目收尾 对照表副本一致');
const un = rd(FIN + '未翻译内容清单.tsv').split(/\r?\n/);
chk(un[0] === '类别\t原文\t出处\t不翻译原因', '未翻译清单表头正确');
chk(un.length - 2 === 9347, '未翻译清单数据行数 ' + (un.length - 2));
const bom = fs.readFileSync(FIN + '未翻译内容清单.tsv');
chk(bom[0] === 0xEF && bom[1] === 0xBB && bom[2] === 0xBF, '未翻译清单带 BOM');

console.log('=== 6. 项目收尾四文档 ===');
for (const f of ['翻译对照表-最新.md', '未翻译内容清单.tsv', '项目日志.md', '技术原理.md']) chk(ex(FIN + f) && fs.statSync(FIN + f).size > 1000, '项目收尾/' + f);

console.log('=== 7. 源码与技术资料 ===');
const SRC_REL = REL + '源码与技术资料/';
const SRC = [
  'README.md', '技术原理.md', '项目日志.md',
  'mapfix/mapfix.cpp', 'mapfix/zone_table.h', 'mapfix/build_mapfix.bat', 'mapfix/gen_zone_table_v7.js', 'mapfix/verify_mapfix.js',
  'procdiag/procdiag.cpp', 'procdiag/build_procdiag.bat', 'procdiag/check_reloc.js',
  '工具脚本/gxt_io.js', '工具脚本/zone_map.js', '工具脚本/wtd_font.js', '工具脚本/render_glyphs.ps1',
  '文本引擎/build_m2_patch.js', '文本引擎/build_m10_gxt.js', '文本引擎/build_v7.js',
  '发布链/gen_release_v1.js', '发布链/verify_release_v1.js',
];
let srcN = 0;
for (const p of SRC) if (ex(SRC_REL + p)) srcN++;
chk(srcN === SRC.length, '源码与技术资料 20 文件齐备（' + srcN + '/' + SRC.length + '）');
chk(eq(SRC_REL + 'README.md', PROJ + '项目收尾/源码与技术资料-README.md'), 'README 导览 == 项目收尾 master');
chk(eq(SRC_REL + '技术原理.md', PROJ + '项目收尾/技术原理.md'), '技术原理.md == 项目收尾原件');
chk(eq(SRC_REL + '项目日志.md', PROJ + '项目收尾/项目日志.md'), '项目日志.md == 项目收尾原件');
chk(eq(SRC_REL + 'mapfix/mapfix.cpp', PROJ + '01-逆向草稿/procdiag/mapfix.cpp'), 'mapfix.cpp == 工程原件');
chk(eq(SRC_REL + '发布链/gen_release_v1.js', PROJ + '01-逆向草稿/gen_release_v1.js'), '发布链/gen_release_v1.js 自收录 == 工程原件');
chk(eq(SRC_REL + '发布链/verify_release_v1.js', PROJ + '01-逆向草稿/verify_release_v1.js'), '发布链/verify_release_v1.js 自收录 == 工程原件');
const srcAll = [];
(function walkS(d) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = d + '/' + e.name; if (e.isDirectory()) walkS(p); else srcAll.push(p); } })(SRC_REL);
chk(srcAll.length === 20, '源码与技术资料 实际文件数 = ' + srcAll.length + '（应为 20）');
chk(!srcAll.some(p => /\.(asi|obj|exe|dll|wtd|gxt|dat|log)$/i.test(p)), '不含二进制/日志文件');
chk(rd(REL + 'README.md').includes('源码与技术资料'), '包根 README 的"技术资料"节在位');
chk(rd(fs.existsSync(REL + '使用说明（必读）.txt') ? REL + '使用说明（必读）.txt' : REL + '使用说明.txt').includes('源码与技术资料'), '使用说明本包内容含源码资料一行');

console.log('=== 8. 封包状态 ===');
const zips = fs.readdirSync(PROJ).filter(f => /v1\.0.*\.zip$/i.test(f));
chk(zips.length === 0, '未生成 zip（用户自行压缩）' + (zips.length ? ': ' + zips.join(',') : ''));

console.log('');
console.log('================ verify_release_v1: ' + OK + ' OK / ' + FAIL + ' FAIL ================');
process.exit(FAIL ? 1 : 0);
