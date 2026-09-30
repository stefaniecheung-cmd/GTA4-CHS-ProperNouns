/* build_m10_gxt.js - M10 vehicle + street + bridge names, whole-entry overwrite by GXT hash,
   on top of 成品包v3 gxt (which already has M2 person names + M5 in-text places + M7 74 zones).
   Hard gate = M4c char_table (3544). Safety: only overwrite an item when its current value
   === the expected english (en==zh untranslated label); otherwise skip + warn (collision / already
   touched by M2/M5/M7). Writes 3 gxt into M10测试包 + ledger M10改动明细.tsv. */
const fs = require('fs');
const path = require('path');
const { parseGxt, buildGxt } = require('./gxt_io.js');

const PROJ = 'E:/SteamLibrary/steamapps/common/Grand Theft Auto IV/汉化补丁工程/';
const ALIGN = PROJ + '02-英中对齐表/';
const V3 = PROJ + '03-补丁构建/成品包v3/';
const PKG = PROJ + '03-补丁构建/M10测试包/';

/* ---- charset gate (M4c 3544) ---- */
const ct = fs.readFileSync(PROJ + '03-补丁构建/M4c字库包/plugins/GTA4.CHS/char_table.dat');
const allowed = new Set();
const n = ct.readUInt32LE(0);
for (let i = 0; i < n; i++) allowed.add(ct.readUInt32LE(4 + i * 4));
console.log('M4c char_table codepoints:', allowed.size);
function missing(s) { const o = []; for (const ch of s) { const c = ch.codePointAt(0); if (c >= 0x80 && !allowed.has(c)) o.push(ch); } return [...new Set(o)]; }

/* ---- load tables ---- */
function readTsv(p) { return fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/).filter(l => l.trim()).map(l => l.split('\t')); }
const entries = []; // {hashU32, en, zh, type}
const veh = readTsv(ALIGN + '车名译名表.tsv').slice(1);
for (const c of veh) {
  const [en, zh, hashes] = c;
  if (!en || !zh || !hashes) continue;
  for (const h of hashes.split(',')) if (h.trim()) entries.push({ hashU32: parseInt(h, 16) >>> 0, en, zh, type: 'vehicle' });
}
const st = readTsv(ALIGN + '街名译名表.tsv').slice(1);
for (const c of st) {
  const [en, zh, hash, src, bucket] = c;
  if (!en || !zh || !hash) continue;
  entries.push({ hashU32: parseInt(hash, 16) >>> 0, en, zh, type: bucket === 'BRIDGE' ? 'bridge' : 'street' });
}
console.log('table entries: ' + entries.length + ' (vehicle ' + entries.filter(e => e.type === 'vehicle').length +
  ', street ' + entries.filter(e => e.type === 'street').length + ', bridge ' + entries.filter(e => e.type === 'bridge').length + ')');

/* ---- gate all zh ---- */
let gateFail = 0;
for (const e of entries) { const m = missing(e.zh); if (m.length) { console.error('  ★ GATE ' + e.type + ' "' + e.en + '" -> "' + e.zh + '" missing ' + m.join('')); gateFail++; } }
if (gateFail) { console.error('★ ' + gateFail + ' entries fail charset gate; abort'); process.exit(1); }
console.log('charset gate: all ' + entries.length + ' zh strings clean vs M4c table');

/* ---- per chapter ---- */
const CHAPS = [
  ['本体', 'update/common/text/american.gxt'],
  ['TLAD', 'update/TLAD/common/text/american.gxt'],
  ['TBoGT', 'update/TBoGT/common/text/american.gxt'],
];
const byHash = new Map();
for (const e of entries) { if (!byHash.has(e.hashU32)) byHash.set(e.hashU32, []); byHash.get(e.hashU32).push(e); }

/* ---- TEST-ONLY probe: repurpose the M4b sample SMS (df7e64b0, 本体 MAIN) to show all 16
   new glyphs + sample names in one place. The PRODUCT build sets ADD_PROBE=false to revert. ---- */
const ADD_PROBE = false;
const PROBE_HASH = 0xdf7e64b0 >>> 0;
const PROBE_TEXT = 'M10缺字样张：俾廷潘琼禄笋翠翡苣茨钙钡铀锰镍镐、翡翠街、锰街、铀街、哈拔尼禄、亨廷顿街、琼斯敦大道，完';
if (ADD_PROBE) { const m = missing(PROBE_TEXT); if (m.length) { console.error('★ probe text missing chars ' + m.join('')); process.exit(1); } }

const ledger = ['\uFEFF' + ['chapter', 'hash', 'type', 'en', 'old', 'new', 'status'].join('\t')];
const appliedPerType = { vehicle: 0, street: 0, bridge: 0 };
const notFound = [];
const mismatch = [];
const foundHashes = new Set();

for (const [tag, rel] of CHAPS) {
  const baseFile = V3 + rel;
  const g = parseGxt(baseFile);
  let changed = 0;
  for (const r of g.recs) {
    for (const it of r.items) {
      const h = it.hash >>> 0;
      const ents = byHash.get(h);
      if (!ents) continue;
      for (const e of ents) {
        if (it.s === e.zh) { ledger.push([tag, h.toString(16), e.type, e.en, it.s, e.zh, 'already'].join('\t')); foundHashes.add(h); continue; }
        if (it.s !== e.en) {
          mismatch.push([tag, h.toString(16), e.type, e.en, it.s]);
          ledger.push([tag, h.toString(16), e.type, e.en, it.s, e.zh, 'SKIP-mismatch'].join('\t'));
          continue;
        }
        const old = it.s;
        it.s = e.zh;
        changed++; appliedPerType[e.type]++; foundHashes.add(h);
        ledger.push([tag, h.toString(16), e.type, e.en, old, e.zh, 'changed'].join('\t'));
      }
    }
  }
  if (ADD_PROBE && tag === '本体') {
    let done = false;
    for (const r of g.recs) for (const it of r.items) if ((it.hash >>> 0) === PROBE_HASH) {
      const old = it.s; it.s = PROBE_TEXT; done = true;
      ledger.push([tag, PROBE_HASH.toString(16), 'probe', '(SMS sample)', old, PROBE_TEXT, 'probe'].join('\t'));
    }
    if (!done) { console.error('★ probe hash df7e64b0 not found in 本体'); process.exit(1); }
    console.log('[本体] probe SMS df7e64b0 set (test-only, product reverts)');
  }
  const out = buildGxt(g);
  const outPath = PKG + rel;
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, out);
  console.log('[' + tag + '] changed ' + changed + ' entries; ' + g.raw.length + ' B -> ' + out.length + ' B; wrote ' + rel);
}

/* ---- coverage report ---- */
const allHashes = [...byHash.keys()];
for (const h of allHashes) if (!foundHashes.has(h)) { const e = byHash.get(h)[0]; notFound.push([h.toString(16), e.type, e.en, e.zh]); }
console.log('');
console.log('=== coverage ===');
console.log('applied: vehicle ' + appliedPerType.vehicle + ', street ' + appliedPerType.street + ', bridge ' + appliedPerType.bridge);
console.log('distinct hashes in tables: ' + allHashes.length + ' | found in some chapter: ' + foundHashes.size + ' | NOT FOUND: ' + notFound.length);
if (notFound.length) { console.log('--- NOT FOUND (hash absent from all 3 gxt) ---'); for (const x of notFound) console.log('  ' + x.join('\t')); }
if (mismatch.length) { console.log('--- MISMATCH (current value != expected en, skipped) ---'); for (const x of mismatch) console.log('  ' + x.join('\t')); }

fs.writeFileSync(PROJ + '03-补丁构建/M10改动明细.tsv', ledger.join('\r\n'), 'utf8');
console.log('');
console.log('wrote M10改动明细.tsv (' + (ledger.length - 1) + ' rows)');
if (notFound.length) { console.error('★ some table hashes not found in any gxt - investigate'); }
