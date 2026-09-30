const fs = require('fs');
const { parseGxt, buildGxt } = require('./gxt_io.js');

const ROOT = 'E:\\SteamLibrary\\steamapps\\common\\Grand Theft Auto IV\\';
const PROJ = ROOT + '汉化补丁工程\\';
const OUT = PROJ + '03-补丁构建\\M2测试包\\';
const CHAR_TABLE = PROJ + '03-补丁构建\\M4b测试包\\plugins\\GTA4.CHS\\char_table.dat';

const tladBak = OUT + '_ORIGINAL_american_tlad.gxt';
const tbogtBak = OUT + '_ORIGINAL_american_tbogt.gxt';
const tladPrj = PROJ + '03-补丁构建\\备份原版\\american_tlad.gxt';
const tbogtPrj = PROJ + '03-补丁构建\\备份原版\\american_tbogt.gxt';
const tladBase = fs.existsSync(tladPrj) ? tladPrj : (fs.existsSync(tladBak) ? tladBak : ROOT + 'GTAIV\\update\\TLAD\\common\\text\\american.gxt');
const tbogtBase = fs.existsSync(tbogtPrj) ? tbogtPrj : (fs.existsSync(tbogtBak) ? tbogtBak : ROOT + 'GTAIV\\update\\TBoGT\\common\\text\\american.gxt');
if (tladBase.endsWith('american.gxt') && tladBase.includes('GTAIV')) console.log('!! DLC 真原版不存在，回退用游戏目录（若已装过 M2 则基底不干净）');
const SOURCES = [
  ['本体', PROJ + '03-补丁构建\\备份原版\\american.gxt', 'update\\common\\text\\american.gxt'],
  ['TLAD', tladBase, 'update\\TLAD\\common\\text\\american.gxt'],
  ['TBoGT', tbogtBase, 'update\\TBoGT\\common\\text\\american.gxt'],
];

const ct = fs.readFileSync(CHAR_TABLE);
const allowed = new Set();
for (let i = 0; i + 3 < ct.length; i += 4) allowed.add(ct.readUInt32LE(i));
const missing = s => [...s].filter(ch => {
  const c = ch.codePointAt(0);
  return c >= 0x80 && !allowed.has(c);
});

const rows = fs.readFileSync(PROJ + '02-英中对齐表\\人名译名表.tsv', 'utf8')
  .replace(/^﻿/, '').split('\n').slice(1).filter(Boolean)
  .map(l => { const p = l.split('\t'); return { en: p[0], zh: p[1], src: p[2] || '' }; });
const keys = rows.slice().sort((a, b) => b.en.length - a.en.length);
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const LOOK = { Francis: '(?!国际|International)' };
const regexOf = k => new RegExp('(?<![A-Za-z])' + esc(k.en) + (LOOK[k.en] || '') + '(?![A-Za-z])', 'g');
const RES = keys.map(regexOf);
const S1 = '\u0001', S2 = '\u0002', DOT = '･';
const SUB_GROUPS_BLOCK = new Set(['CREDIT', 'CREDIT1']);
const TRIM_PUNCT = /^[~\s　]+|[~\s　]+$/g;

function wholeEntry(s) {
  const t = s.replace(TRIM_PUNCT, '');
  let tail = '';
  let body = t;
  const m = t.match(/^(.*?)([，。、！？,!.?]+)$/);
  if (m && m[1]) { body = m[1]; tail = m[2]; }
  const direct = rows.find(r => r.en === body && r.zh !== r.en);
  if (direct) return direct.zh + tail;
  const parts = body.split(' ').filter(Boolean);
  if (!parts.length || parts.length > 4) return null;
  const zhs = parts.map(p => {
    const k = rows.find(r => r.en === p && r.zh !== r.en);
    return k ? k.zh : null;
  });
  if (zhs.some(z => !z)) return null;
  return zhs.join(DOT) + tail;
}

function substitute(s) {
  let out = s;
  for (let i = 0; i < keys.length; i++) out = out.replace(RES[i], S1 + i + S2);
  out = out.replace(new RegExp(S2 + ' ' + S1, 'g'), S2 + DOT + S1);
  out = out.replace(new RegExp(S1 + '(\\d+)' + S2, 'g'), (_, i) => keys[parseInt(i, 10)].zh);
  return out;
}

const changes = [];
const built = [];
for (const [tag, src, rel] of SOURCES) {
  const g = parseGxt(src);
  let nSub = 0, nWhole = 0;
  g.recs.forEach(r => {
    const gname = r.name.replace(/\0+$/, '');
    const blockSub = SUB_GROUPS_BLOCK.has(gname);
    r.items.forEach(it => {
      const s = it.s;
      if (!s) return;
      let neu = null;
      const w = wholeEntry(s);
      if (w && w !== s) { neu = w; nWhole++; }
      else if (!blockSub && /[一-鿿]/.test(s)) {
        const r2 = substitute(s);
        if (r2 !== s) { neu = r2; nSub++; }
      }
      if (neu !== null && neu !== s) {
        const oldBad = new Set(missing(s));
        const bad = missing(neu).filter(c => !oldBad.has(c));
        if (bad.length) {
          console.log('★ 字库硬闸: [' + tag + '] ' + (it.hash >>> 0).toString(16) + ' 新增表外字 ' + [...new Set(bad)].map(c => c + '/U+' + c.codePointAt(0).toString(16)).join(''));
          process.exit(1);
        }
        changes.push({ tag, g: gname, h: (it.hash >>> 0).toString(16), old: s, neu });
        it.s = neu;
      }
    });
  });
  const buf = buildGxt(g);
  built.push([tag, rel, buf]);
  console.log(tag + ': 替换 ' + nSub + ' 条 + 整条 ' + nWhole + ' 条 = ' + (nSub + nWhole) + ' 条；原 ' + g.len + ' B -> 新 ' + buf.length + ' B');
}

// M1 台账复现检查
const ledger = fs.readFileSync(PROJ + '03-补丁构建\\M1改动明细.tsv', 'utf8')
  .replace(/^﻿/, '').split('\n').slice(1).filter(Boolean)
  .map(l => { const p = l.split('\t'); return { use: p[0], h: p[1].split('] ')[1], want: p[3] }; });
const mainMap = new Map();
changes.forEach(c => { if (c.tag === '本体') mainMap.set(c.h, c.neu); });
// 台账期望：Kiki 升级琪琪
const wantOf = r => r.use.includes('Kiki') ? r.want.replace('奇奇', '琪琪') : r.want;
let bad = 0;
ledger.forEach(r => {
  const got = mainMap.get(r.h.replace(/^0+/, '') || '0');
  if (got === undefined) { console.log('★ 台账未复现(未改动): ' + r.h + ' ' + r.use); bad++; return; }
  if (got !== wantOf(r)) { console.log('★ 台账不一致: ' + r.h + ' ' + r.use + ' 期望=' + wantOf(r) + ' 实际=' + got); bad++; }
});
console.log('M1 台账 87 条复现: ' + (bad ? bad + ' 条不一致' : '全部一致（Kiki 已升级琪琪）'));
if (bad) process.exit(1);

// 落盘
fs.mkdirSync(OUT + 'update\\common\\text', { recursive: true });
fs.mkdirSync(OUT + 'update\\TLAD\\common\\text', { recursive: true });
fs.mkdirSync(OUT + 'update\\TBoGT\\common\\text', { recursive: true });
built.forEach(([tag, rel, buf]) => fs.writeFileSync(OUT + rel, buf));

const det = ['tag\tgroup\thash\told\tnew'];
changes.forEach(c => det.push(c.tag + '\t' + c.g + '\t' + c.h + '\t' + c.old + '\t' + c.neu));
fs.writeFileSync(PROJ + '03-补丁构建\\M2改动明细.tsv', '﻿' + det.join('\n'), 'utf8');
console.log('改动明细 ' + changes.length + ' 条 -> M2改动明细.tsv');

// bat
const FILES = built.map(([, rel]) => rel);
const BAK = ['_ORIGINAL_american.gxt', '_ORIGINAL_american_tlad.gxt', '_ORIGINAL_american_tbogt.gxt'];
function bat(install) {
  const L = [];
  L.push('@echo off');
  L.push('setlocal enabledelayedexpansion');
  L.push('');
  L.push('echo ==============================================');
  L.push('echo   M2 name test package  -  person names');
  L.push('echo   needs CHS patch 2024-09-13 already installed');
  L.push('echo ==============================================');
  L.push('');
  L.push('set PKG=%~dp0');
  L.push('cd /d "%PKG%..\\..\\..\\GTAIV"');
  L.push('');
  FILES.forEach((rel, i) => {
    const flat = rel.replace(/\\/g, '_');
    L.push('set REL=' + rel);
    L.push('set BAK=' + BAK[i]);
    L.push('call :' + (install ? 'one' : 'back'));
    L.push('');
  });
  L.push('echo.');
  L.push('echo [DONE] all files ' + (install ? 'installed.' : 'restored.'));
  L.push('pause');
  L.push('exit /b 0');
  L.push('');
  L.push(':one');
  L.push('if not exist "%REL%" echo [ERR] missing %REL% & pause & exit /b 1');
  L.push('if exist "%PKG%%BAK%" goto :one_copy');
  L.push('copy /y "%REL%" "%PKG%%BAK%" >nul && echo [BAK]  %BAK%');
  L.push(':one_copy');
  L.push('copy /y "%PKG%%REL%" "%REL%" >nul && echo [OK]   %REL% || echo [FAIL] %REL%');
  L.push('exit /b 0');
  L.push('');
  L.push(':back');
  L.push('if not exist "%PKG%%BAK%" echo [ERR] no backup %BAK% & pause & exit /b 1');
  L.push('copy /y "%PKG%%BAK%" "%REL%" >nul && echo [OK]   restored %REL% || echo [FAIL] %REL%');
  L.push('exit /b 0');
  return L.join('\r\n') + '\r\n';
}
fs.writeFileSync(OUT + '安装.bat', bat(true));
fs.writeFileSync(OUT + '卸载.bat', bat(false));
console.log('bat 已生成');
console.log('>>> 构建完成');
