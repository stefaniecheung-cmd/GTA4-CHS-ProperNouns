const fs = require('fs');
const G = 'E:\\SteamLibrary\\steamapps\\common\\Grand Theft Auto IV\\GTAIV\\';

function parseGxt(file) {
  const d = fs.readFileSync(file);
  const tabSize = d.readUInt32LE(8);
  const recs = [];
  for (let i = 0; i * 12 < tabSize; i++) {
    const p = 12 + i * 12;
    const rawName = d.slice(p, p + 8);
    const off = d.readUInt32LE(p + 8);
    const tkeyAt = d.slice(off, off + 4).toString('latin1') === 'TKEY' ? off : off + 8;
    const hasName = tkeyAt === off + 8;
    const tkeySize = d.readUInt32LE(tkeyAt + 4);
    const es = tkeyAt + 8;
    const tdatAt = es + tkeySize;
    const tdatSize = d.readUInt32LE(tdatAt + 4);
    const payload = tdatAt + 8;
    const items = [];
    for (let k = 0; k * 8 < tkeySize; k++) {
      const to = d.readUInt32LE(es + k * 8);
      const hash = d.readUInt32LE(es + k * 8 + 4);
      let s = '';
      for (let q = payload + to; q + 1 < d.length; q += 2) { const c = d.readUInt16LE(q); if (!c) break; s += String.fromCharCode(c); }
      items.push({ hash, s });
    }
    recs.push({ rawName, name: rawName.toString('latin1'), hasName, items });
  }
  // 推断该文件的填充规则
  let padded = 0, tight = 0;
  for (let k = 0; k + 1 < recs.length; k++) {
    const r = recs[k];
    const off = d.readUInt32LE(12 + k * 12 + 8);
    const tkeyAt = d.slice(off, off + 4).toString('latin1') === 'TKEY' ? off : off + 8;
    const tdatAt = tkeyAt + 8 + d.readUInt32LE(tkeyAt + 4);
    const end = tdatAt + 8 + d.readUInt32LE(tdatAt + 4);
    const nextOff = d.readUInt32LE(12 + (k + 1) * 12 + 8);
    if (nextOff > end) padded++; else tight++;
  }
  const padMode = padded > 0 ? 'align4' : 'none';
  return { recs, u16a: d.readUInt16LE(0), u16b: d.readUInt16LE(2), len: d.length, padMode, padded, tight, raw: d };
}

function buildGxt(g) {
  const n = g.recs.length;
  const tabSize = n * 12;
  const header = Buffer.alloc(12);
  header.writeUInt16LE(g.u16a, 0);
  header.writeUInt16LE(g.u16b, 2);
  header.write('TABL', 4, 'latin1');
  header.writeUInt32LE(tabSize, 8);
  const table = Buffer.alloc(tabSize);
  const blocks = [];
  let cur = 12 + tabSize;
  g.recs.forEach((r, i) => {
    const parts = [];
    let pos = 0;
    const offs = r.items.map(it => {
      const o = pos;
      const buf = Buffer.from(it.s, 'utf16le');
      parts.push(buf); parts.push(Buffer.alloc(2));
      pos += buf.length + 2;
      return o;
    });
    const tdat = Buffer.concat(parts);
    const tkey = Buffer.alloc(r.items.length * 8);
    r.items.forEach((it, k) => { tkey.writeUInt32LE(offs[k], k * 8); tkey.writeUInt32LE(it.hash >>> 0, k * 8 + 4); });
    const chunks = [];
    if (r.hasName) chunks.push(r.rawName);
    const th = Buffer.alloc(8); th.write('TKEY', 0, 'latin1'); th.writeUInt32LE(tkey.length, 4);
    const dh = Buffer.alloc(8); dh.write('TDAT', 0, 'latin1'); dh.writeUInt32LE(tdat.length, 4);
    chunks.push(th, tkey, dh, tdat);
    const block = Buffer.concat(chunks);
    table.set(r.rawName, i * 12);
    table.writeUInt32LE(cur, i * 12 + 8);
    blocks.push(block);
    cur += block.length;
    if (g.padMode === 'align4' && i < n - 1) {
      const pad = (4 - (cur % 4)) % 4;
      if (pad) { blocks.push(Buffer.alloc(pad)); cur += pad; }
    }
  });
  return Buffer.concat([header, table, ...blocks]);
}

if (require.main === module) {
  const targets = [
    ['本体-base', 'common/text/american.gxt'],
    ['本体-override', 'update/common/text/american.gxt'],
    ['TLAD-base', 'TLAD/common/text/american.gxt'],
    ['TLAD-override', 'update/TLAD/common/text/american.gxt'],
    ['TBoGT-base', 'TBoGT/common/text/american.gxt'],
    ['TBoGT-override', 'update/TBoGT/common/text/american.gxt'],
  ];
  let allOk = true;
  for (const [tag, rel] of targets) {
    const src = G + rel;
    if (!fs.existsSync(src)) { console.log(tag + ': 文件不存在'); continue; }
    const g = parseGxt(src);
    const out = buildGxt(g);
    const identical = out.equals(g.raw);
    if (!identical) allOk = false;
    let extra = '';
    if (!identical) {
      let fd = -1;
      for (let i = 0; i < Math.min(out.length, g.raw.length); i++) if (out[i] !== g.raw[i]) { fd = i; break; }
      let blk = -1;
      for (let k = 0; k < g.recs.length; k++) {
        const off = g.raw.readUInt32LE(12 + k * 12 + 8);
        if (off <= fd) blk = k; else break;
      }
      extra = '  首个差异在偏移 ' + fd + '（第 ' + blk + ' 块内，块内偏移 +' + (fd - g.raw.readUInt32LE(12 + blk * 12 + 8)) + '；原字节 ' + g.raw[fd] + ' vs 重建 ' + out[fd] + '）';
    }
    console.log(tag + ': 填充规则=' + g.padMode + '（补 ' + g.padded + ' / 紧 ' + g.tight + '）  原 ' + g.len + ' B -> 重建 ' + out.length + ' B  字节级完全相同 = ' + identical + extra);
  }
  console.log('');
  console.log(allOk ? '全部 6 个文件都能字节级还原 —— GXT 读写器可以放心用。' : '仍有文件还原不一致，需要继续查。');
}

module.exports = { parseGxt, buildGxt };
