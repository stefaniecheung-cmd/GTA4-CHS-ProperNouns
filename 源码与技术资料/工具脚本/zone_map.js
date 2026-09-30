const fs = require('fs');
const G = 'E:\\SteamLibrary\\steamapps\\common\\Grand Theft Auto IV\\GTAIV\\';
const { parseGxt } = require('./gxt_io.js');

const U32 = x => x >>> 0;
function gtaHash(s) {
  let h = 0;
  for (const c of s.toLowerCase()) { h = U32(h + c.charCodeAt(0)); h = U32(h + (h << 10)); h = U32(h ^ (h >>> 6)); }
  h = U32(h + (h << 3)); h = U32(h ^ (h >>> 11)); h = U32(h + (h << 15));
  return h;
}

const base = parseGxt(G + 'common\\text\\american.gxt');
const over = parseGxt(G + 'update\\common\\text\\american.gxt');
const bH = new Map(), oH = new Map();
base.recs.forEach(r => r.items.forEach(it => { if (!bH.has(it.hash)) bH.set(it.hash, { s: it.s, blk: r.name.replace(/\0/g, '').trim() }); }));
over.recs.forEach(r => r.items.forEach(it => { if (!oH.has(it.hash)) oH.set(it.hash, { s: it.s, blk: r.name.replace(/\0/g, '').trim() }); }));

const EDITED = new Set(['3c3b5b90','119526ae','95865bd0','3fa20554','d699b0b8','2e3db764','4d6da0eb','7653ef56','80d6b2a5','514f289e','1dc13e42','2fd4e4a9','30d39268','b144e898','459790fe','e64e5984','1903b1cc','fdc103e2','be9ca760','c65b0b5c','76947467','756ac6f6','42d337b3','7c3cfe89','f1cc8a1a','846b05f5','7464688c','95256cea','2b1955f7','6d0d4db','ec9382fc','db8913fc','f61cc088','97c7b06d','1e3590e9','b788efef','33f3bc65','347469c8','890c676d','4226852c','57b084b6','5f00bee0','8a16f37f','fccc3d5','8261e524','6610acb3','290c5654','8cc27fb3','57cb7889','9dba526f','5ebec3a','1b59b643','22133f34','cd4479e5','d5154e63','bfe4e5f7','e614951d','e1d1c334','b903ed17','2b26f456','e76a3064','170f2c1e','b64fcd48','7c21fc06','5de92201','125c6dac','afe3f6c2','1416888f','6178bbf','70435b93','46d94e66','df7e64b0','e14e408c','e9d95a48','38aff7f4','d7f9338','9129f0cb','18f3794a','2d9271e1','48487d09','57d9c673','643334e2','2cc3f6c9','5c9bb920','4a0251ce','7a483259','ce734eda','36134c9b','adca25ae']);

const zon = fs.readFileSync(G + 'common\\data\\info.zon', 'latin1').split(/\r?\n/);
const keys = new Map();
for (const line of zon) {
  const t = line.trim(); if (!t || t === 'zone' || t === 'end') continue;
  const p = t.split(',').map(s => s.trim());
  const lvl = p[p.length - 2], k = p[p.length - 1];
  if (!/^[A-Za-z0-9_]+$/.test(k)) continue;
  if (!keys.has(k)) keys.set(k, { lvl, n: 0 });
  keys.get(k).n++;
}

console.log('=== info.zon 全部区名键 -> GXT 条目 ===');
console.log('键名     层级 出现次数  哈希       英文原文                 汉化补丁现译              我们改过?');
let hit = 0, edited = 0;
const rows = [];
for (const [k, v] of keys) {
  const h = gtaHash(k);
  const b = bH.get(h), o = oH.get(h);
  const isEd = EDITED.has(h.toString(16));
  if (b) hit++;
  if (isEd) edited++;
  rows.push([k, v.lvl, v.n, h.toString(16).padStart(8, '0'), b ? b.s : '(GXT无此键)', o ? o.s : '(无)', isEd ? '★改了' : '']);
}
rows.sort((a, b) => a[1] - b[1] || a[0].localeCompare(b[0]));
for (const r of rows) console.log('  ' + r[0].padEnd(8) + r[1].padEnd(5) + String(r[2]).padEnd(9) + r[3].padEnd(10) + r[4].slice(0, 24).padEnd(26) + r[5].slice(0, 24).padEnd(26) + r[6]);
console.log('');
console.log('键总数 ' + keys.size + '，能在 GXT 里找到对应条目 ' + hit + ' 个，其中被本次测试包改过 ' + edited + ' 个');

console.log('');
console.log('=== 我们改的那 28 条区名条目，到底被谁用？ ===');
const NAMES = ['Broker', 'Algonquin', 'Bohan', 'Dukes', 'Alderney'];
for (const nm of NAMES) {
  const hs = (base.recs.flatMap(r => r.items.filter(it => it.s === nm).map(it => ({ h: it.hash, blk: r.name.replace(/\0/g, '').trim() }))));
  console.log('  英文文本恰好是 "' + nm + '" 的条目共 ' + hs.length + ' 个:');
  for (const x of hs) {
    const zonKey = [...keys.entries()].find(([k]) => gtaHash(k) === x.h);
    console.log('    hash=' + x.h.toString(16).padStart(8, '0') + ' @' + x.blk.padEnd(9) + ' 被 info.zon 引用: ' + (zonKey ? '是（键 ' + zonKey[0] + '）' : '否'));
  }
}
