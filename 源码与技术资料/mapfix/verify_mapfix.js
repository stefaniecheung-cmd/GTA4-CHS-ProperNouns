/* verify_mapfix.js - offline simulation of mapfix.asi's FixZone matching logic.
   Faithfully replicates the C matcher and runs it over EVERY distinct string captured in
   procdiag.log, plus the 74 real zone names and their -0x20 forms. Proves:
     (1) all garbage zone-label strings match and map to the correct real zone;
     (2) zero false positives on menu / POI / current-zone / objective strings;
     (3) the 74 real names themselves are never matched (recursion-safe). */
const fs = require('fs');
const ROOT = 'E:/SteamLibrary/steamapps/common/Grand Theft Auto IV';
const ENG = ROOT + '/汉化补丁工程';
const MAXREAD = 12;

// ---- zone table (real names) ----
const det = fs.readFileSync(ENG + '/03-补丁构建/M7区名改动明细.tsv','utf8').replace(/^\uFEFF/,'');
const ZONE_REAL = [];
for (const row of det.split(/\r?\n/).slice(1)) { const c=row.split('\t'); if(c.length>=5 && c[4]) ZONE_REAL.push([...c[4]].map(ch=>ch.codePointAt(0))); }
const ZONE_LEN = ZONE_REAL.map(a=>a.length);
const ZONE_COUNT = ZONE_REAL.length;
const u = a => a.map(c=>String.fromCharCode(c)).join('');

// ---- faithful port of FixZone: input = array of u16 codes (the live string, NUL-terminated in game) ----
// 'codes' here is the full string WITHOUT the NUL; we simulate the NUL by its length.
function fixZone(codes){
  const n = codes.length;            // game string length (chars before NUL)
  if (n === 0 || n >= MAXREAD) return null;   // empty or too long / no NUL within MAXREAD -> pass through
  for (let i=0;i<ZONE_COUNT;i++){
    if (ZONE_LEN[i] !== n) continue;
    let match = true;
    for (let k=0;k<n;k++){ const want=(ZONE_REAL[i][k]-0x20)&0xffff; if (codes[k]!==want){match=false;break;} }
    if (match) return i;
  }
  return null;
}

// ---- parse log: collect distinct (string codes, n, x, y) ----
const text = fs.readFileSync((process.env.PLOG || ROOT + '/GTAIV/plugins/procdiag.log'),'latin1');
function f32(h){ const b=Buffer.alloc(4); b.writeUInt32BE(parseInt(h,16)>>>0,0); return b.readFloatBE(0); }
const seen = new Map(); // key=string -> {codes,n,x,y,count}
for (const ln of text.split(/\r?\n/)) {
  const m = ln.match(/r=[0-9a-f]{8} x=([0-9a-f]{8}) y=([0-9a-f]{8}) f=[0-9a-f]{2} t=[0-9a-f]{8} n=(\d+) s=(.*)$/);
  if (!m) continue;
  const x=f32(m[1]), y=f32(m[2]), n=parseInt(m[3],10);
  const hexes=(m[4]||'').trim().split(/\s+/).filter(Boolean);
  const codes=hexes.map(h=>parseInt(h,16));
  const s=u(codes);
  if (!seen.has(s)) seen.set(s,{codes,n,x,y,count:0});
  seen.get(s).count++;
}

// ---- run matcher over every distinct captured string ----
let matched=[], unmatched=[];
for (const [s,info] of seen) {
  // FixZone only sees the live string; the log stored min(n,12) chars. If n>=MAXREAD the game
  // string had no NUL within MAXREAD -> FixZone returns pass-through. Use logged codes when n<12.
  const eff = (info.n >= MAXREAD) ? null : fixZone(info.codes);
  if (eff !== null && eff !== undefined) matched.push({s, idx:eff, ...info});
  else unmatched.push({s, ...info});
}

console.log('=== distinct captured strings:', seen.size, '===');
console.log('MATCHED (will be corrected):', matched.length);
let allGarbage=true, allCorrect=true;
for (const m of matched.sort((a,b)=>b.count-a.count)) {
  const real = u(ZONE_REAL[m.idx]);
  const isGarbagePos = (Math.abs(m.x)<1e-4 && Math.abs(m.y-0.221)<0.002);
  if (!isGarbagePos) allGarbage=false;
  // sanity: matched string + 0x20 must equal the real zone name
  const recovered = u(m.codes.map(c=>(c+0x20)&0xffff));
  if (recovered !== real) allCorrect=false;
  console.log('  ['+String(m.count).padStart(4)+'x] x'+m.x.toFixed(3)+' y'+m.y.toFixed(3)+' "'+m.s+'" -> "'+real+'"'+(isGarbagePos?'':'  <<< NOT at garbage pos!'));
}
console.log('all matched are at garbage pos (x=0,y=0.221):', allGarbage);
console.log('all matched recover to the mapped real zone:', allCorrect);

console.log('\nUNMATCHED (pass through) sample - must include menu/POI/current-zone, total', unmatched.length, ':');
for (const s of unmatched.sort((a,b)=>b.count-a.count).slice(0,25)) console.log('  ['+String(s.count).padStart(4)+'x] x'+s.x.toFixed(3)+' y'+s.y.toFixed(3)+' "'+s.s+'"');

// ---- false-positive audit: any UNMATCHED string that is a readable zone name? (should pass through) ----
const realSet = new Set(ZONE_REAL.map(u));
const zonePassedThrough = unmatched.filter(s=>realSet.has(s.s));
console.log('\nreadable real zone names that passed through unchanged (expected, = path 2):', zonePassedThrough.map(s=>s.s).join(', ') || '(none captured)');

// ---- test 3: the 74 real names must NEVER match (recursion safety) ----
let realMatched=0;
for (let i=0;i<ZONE_COUNT;i++){ if (fixZone(ZONE_REAL[i]) !== null) realMatched++; }
console.log('\nTEST3 real zone names that wrongly match a bad form (must be 0):', realMatched);

// ---- test 4: every bad form (real-0x20) must match its own zone ----
let badOk=0, badBad=[];
for (let i=0;i<ZONE_COUNT;i++){ const bad=ZONE_REAL[i].map(c=>(c-0x20)&0xffff); const r=fixZone(bad); if(r===i) badOk++; else badBad.push(u(ZONE_REAL[i])+'->'+r); }
console.log('TEST4 bad forms matching their own zone (must be '+ZONE_COUNT+'):', badOk, badBad.length?('MISMATCH:'+badBad.join(',')):'');
