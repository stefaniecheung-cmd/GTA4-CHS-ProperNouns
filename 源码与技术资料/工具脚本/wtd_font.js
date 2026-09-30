/* fonts.wtd 字库贴图读写模块
   结构（本项目实测）：
     文件 = 'RSC\x05' + u32 flags + u32 sizes + zlib deflate 流（从偏移 12 开始）
     解压后 = [虚拟段 0x1000 B][数据段 ...]，虚拟段基址 0x50000000，数据段基址 0x60000000
     贴图结构体 80 B，+0x00 vtable 0xb6f0ee97，+0x14 名字指针，+0x1C width|height，
       +0x20 fourCC，+0x48 像素数据指针
     font_chs 是 4096x4096 DXT5(BC3)，格 64x66，64 列 x 62 行 = 3968 格，格号 == char_table 索引
   BC3 块 = [alpha 块 8 B][颜色块 8 B]，4x4 像素
   颜色平面惯例（实测）：alpha>0 的像素 100% 是纯白，alpha=0 的多数是纯黑
*/
const fs = require('fs');
const zlib = require('zlib');

const CW = 64, CH = 66, COLS = 64, ROWS = 62;
const VTABLE = 0xb6f0ee97;

/* ---------- 打开 / 关闭 ---------- */
function openWtd(file) {
  const raw = fs.readFileSync(file);
  if (raw.slice(0, 4).toString('latin1') !== 'RSC\x05') throw new Error('不是 RSC5: ' + file);
  const flags = raw.readUInt32LE(4);
  const sizes = raw.readUInt32LE(8);
  if (raw[12] !== 0x78) throw new Error('偏移 12 不是 zlib 头 (0x' + raw[12].toString(16) + '): ' + file);
  const data = zlib.inflateSync(raw.slice(12));
  const texs = parseTextures(data);
  return { file, raw, flags, sizes, data, texs };
}

function parseTextures(d) {
  const out = [];
  for (let o = 0; o + 0x50 <= 0x1000; o += 4) {
    if (d.readUInt32LE(o) !== VTABLE) continue;
    const namePtr = d.readUInt32LE(o + 0x14);
    const wh = d.readUInt32LE(o + 0x1c);
    const fourcc = d.slice(o + 0x20, o + 0x24).toString('latin1');
    const dataPtr = d.readUInt32LE(o + 0x48);
    let name = '';
    if (namePtr >= 0x50000000 && namePtr - 0x50000000 < 0x1000) {
      const no = namePtr - 0x50000000;
      let e = no; while (e < 0x1000 && d[e] !== 0) e++;
      name = d.slice(no, e).toString('latin1');
    }
    if (dataPtr < 0x60000000) continue;
    out.push({
      at: o, name, w: wh & 0xffff, h: (wh >> 16) & 0xffff, fourcc, dataPtr,
      off: dataPtr - 0x60000000 + 0x1000
    });
  }
  return out;
}

function repack(w, level) {
  const body = zlib.deflateSync(w.data, { level: level === undefined ? 9 : level });
  const out = Buffer.alloc(12 + body.length);
  out.write('RSC\x05', 0, 'latin1');
  out.writeUInt32LE(w.flags, 4);
  out.writeUInt32LE(w.sizes, 8);
  body.copy(out, 12);
  return out;
}

/* ---------- BC3 alpha ---------- */
function alphaPalette(a0, a1) {
  const p = new Uint8Array(8);
  p[0] = a0; p[1] = a1;
  if (a0 > a1) {
    for (let k = 1; k <= 6; k++) p[1 + k] = Math.floor(((7 - k) * a0 + k * a1) / 7);
  } else {
    for (let k = 1; k <= 4; k++) p[1 + k] = Math.floor(((5 - k) * a0 + k * a1) / 5);
    p[6] = 0; p[7] = 255;
  }
  return p;
}

function decodeAlphaRegion(data, atlasOff, W, H, x0, y0, x1, y1) {
  const BW = W / 4, BH = H / 4;
  const bw = x1 - x0, bh = y1 - y0;
  const out = new Uint8Array(bw * bh);
  for (let by = Math.floor(y0 / 4); by <= Math.floor((y1 - 1) / 4); by++) {
    for (let bx = Math.floor(x0 / 4); bx <= Math.floor((x1 - 1) / 4); bx++) {
      const o = atlasOff + (by * BW + bx) * 16;
      const a0 = data[o], a1 = data[o + 1];
      const pal = alphaPalette(a0, a1);
      let bits = 0n;
      for (let k = 0; k < 6; k++) bits |= BigInt(data[o + 2 + k]) << BigInt(8 * k);
      for (let p = 0; p < 16; p++) {
        const px = bx * 4 + (p & 3), py = by * 4 + (p >> 2);
        if (px < x0 || px >= x1 || py < y0 || py >= y1) continue;
        out[(py - y0) * bw + (px - x0)] = pal[Number((bits >> BigInt(3 * p)) & 7n)];
      }
    }
  }
  return out;
}

/* 4x4 alpha 块编码：候选端点取块内出现过的值加 0/255，两种模式全试，取 SSE 最小 */
function encodeAlphaBlock(vals) {
  let mn = 255, mx = 0;
  for (const v of vals) { if (v < mn) mn = v; if (v > mx) mx = v; }
  const out = Buffer.alloc(8);
  if (mn === mx) { out[0] = mx; out[1] = mx; return out; }   // 索引全 0 -> a0

  const cand = [...new Set([...vals, 0, 255])].sort((a, b) => a - b);
  const keep = cand.length <= 14 ? cand : (() => {
    const pick = new Set([cand[0], cand[cand.length - 1]]);
    for (let i = 0; i < 12; i++) pick.add(cand[Math.round(i * (cand.length - 1) / 11)]);
    return [...pick].sort((a, b) => a - b);
  })();

  let best = null;
  for (const a0 of keep) {
    for (const a1 of keep) {
      const pal = alphaPalette(a0, a1);
      let sse = 0;
      const idx = new Uint8Array(16);
      for (let p = 0; p < 16; p++) {
        let bd = 1e9, bi = 0;
        for (let k = 0; k < 8; k++) { const dd = Math.abs(pal[k] - vals[p]); if (dd < bd) { bd = dd; bi = k; } }
        idx[p] = bi; sse += bd * bd;
      }
      if (!best || sse < best.sse) best = { sse, a0, a1, idx };
    }
  }
  out[0] = best.a0; out[1] = best.a1;
  let bits = 0n;
  for (let p = 0; p < 16; p++) bits |= BigInt(best.idx[p]) << BigInt(3 * p);
  for (let k = 0; k < 6; k++) out[2 + k] = Number((bits >> BigInt(8 * k)) & 0xffn);
  return out;
}

/* 颜色块：alpha>0 -> 白，alpha==0 -> 黑（照抄原字库惯例） */
function encodeColorBlock(alphas) {
  const out = Buffer.alloc(8);
  let anyOn = false, anyOff = false;
  for (const a of alphas) { if (a > 0) anyOn = true; else anyOff = true; }
  if (!anyOn) return out;                                   // 全透明：8 字节全 0
  if (!anyOff) { out.writeUInt16LE(0xffff, 0); out.writeUInt16LE(0xffff, 2); return out; }  // 全白
  out.writeUInt16LE(0xffff, 0);                             // c0=白 c1=黑，c0>c1 走四色模式
  out.writeUInt16LE(0x0000, 2);
  let idx = 0;
  for (let p = 0; p < 16; p++) if (alphas[p] === 0) idx |= (1 << (2 * p));   // 索引 1 = 黑
  out.writeUInt32LE(idx >>> 0, 4);
  return out;
}

/* ---------- 格级读写 ---------- */
function cellRect(i, W, H) {
  const cols = Math.floor(W / CW);
  const col = i % cols, row = Math.floor(i / cols);
  const x0 = col * CW, y0 = row * CH;
  return { x0, y0, x1: Math.min(W, x0 + CW), y1: Math.min(H, y0 + CH), col, row, cols };
}

function readCell(data, atlasOff, W, H, i) {
  const r = cellRect(i, W, H);
  return { rect: r, alpha: decodeAlphaRegion(data, atlasOff, W, H, r.x0, r.y0, r.x1, r.y1) };
}

/* glyph: Uint8Array(CW*CH)；只重写与本格相交的块，块内本格以外的像素保持原值 */
function writeCell(data, atlasOff, W, H, i, glyph) {
  const r = cellRect(i, W, H);
  const bw = r.x1 - r.x0, bh = r.y1 - r.y0;
  // 覆盖范围向外扩到块边界
  const bx0 = Math.floor(r.x0 / 4), bx1 = Math.floor((r.x1 - 1) / 4);
  const by0 = Math.floor(r.y0 / 4), by1 = Math.floor((r.y1 - 1) / 4);
  const px0 = bx0 * 4, py0 = by0 * 4, px1 = (bx1 + 1) * 4, py1 = (by1 + 1) * 4;
  const cur = decodeAlphaRegion(data, atlasOff, W, H, px0, py0, Math.min(W, px1), Math.min(H, py1));
  const rw = Math.min(W, px1) - px0;
  for (let y = 0; y < bh; y++) {
    for (let x = 0; x < bw; x++) {
      cur[(r.y0 + y - py0) * rw + (r.x0 + x - px0)] = glyph[y * CW + x];
    }
  }
  const BW = W / 4;
  let maxErr = 0;
  for (let by = by0; by <= by1; by++) {
    for (let bx = bx0; bx <= bx1; bx++) {
      const vals = new Uint8Array(16);
      for (let p = 0; p < 16; p++) {
        const lx = bx * 4 + (p & 3) - px0, ly = by * 4 + (p >> 2) - py0;
        vals[p] = (lx >= 0 && ly >= 0 && lx < rw && ly < cur.length / rw) ? cur[ly * rw + lx] : 0;
      }
      const o = atlasOff + (by * BW + bx) * 16;
      encodeAlphaBlock(vals).copy(data, o);
      encodeColorBlock(vals).copy(data, o + 8);
      // 回读校验
      const pal = alphaPalette(data[o], data[o + 1]);
      let bits = 0n;
      for (let k = 0; k < 6; k++) bits |= BigInt(data[o + 2 + k]) << BigInt(8 * k);
      for (let p = 0; p < 16; p++) {
        const got = pal[Number((bits >> BigInt(3 * p)) & 7n)];
        const e = Math.abs(got - vals[p]);
        if (e > maxErr) maxErr = e;
      }
    }
  }
  return { blocks: (bx1 - bx0 + 1) * (by1 - by0 + 1), maxErr };
}

/* ---------- char_table.dat ---------- */
function readCharTable(file) {
  const b = fs.readFileSync(file);
  const n = b.readUInt32LE(0);
  const cps = [];
  for (let i = 0; i < n; i++) cps.push(b.readUInt32LE(4 + i * 4));
  return cps;
}
function buildCharTable(cps) {
  const b = Buffer.alloc(4 + cps.length * 4);
  b.writeUInt32LE(cps.length, 0);
  cps.forEach((c, i) => b.writeUInt32LE(c, 4 + i * 4));
  return b;
}

module.exports = { CW, CH, COLS, ROWS, openWtd, repack, parseTextures, alphaPalette,
  decodeAlphaRegion, encodeAlphaBlock, encodeColorBlock, cellRect, readCell, writeCell,
  readCharTable, buildCharTable };
