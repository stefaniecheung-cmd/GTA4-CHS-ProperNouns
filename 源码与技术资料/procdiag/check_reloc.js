/* check .reloc of GTAIV.exe for an entry covering RVA 0x5222A7 (the GS-cookie operand
   inside ProcessString's 2nd instruction). If present, ASLR relocation rewrites that
   absolute address at runtime -> explains procdiag's disk-byte prologue mismatch. */
const fs = require('fs');
const exe = 'E:/SteamLibrary/steamapps/common/Grand Theft Auto IV/GTAIV/GTAIV.exe';
const buf = fs.readFileSync(exe);

function u16(o){ return buf.readUInt16LE(o); }
function u32(o){ return buf.readUInt32LE(o); }

const peOff = u32(0x3c);
if (buf.toString('ascii', peOff, peOff+4) !== 'PE\0\0') { console.error('not PE'); process.exit(1); }
const numSec = u16(peOff+6);
const optSize = u16(peOff+20);
const secOff = peOff + 24 + optSize;
const imageBase = u32(peOff + 24 + 28); // OptionalHeader.ImageBase (PE32)
console.log('imageBase=0x' + imageBase.toString(16), 'numSections=' + numSec);

let relocRVA = 0, relocSize = 0, relocRaw = 0;
for (let i=0;i<numSec;i++){
  const o = secOff + i*40;
  const name = buf.toString('ascii', o, o+8).replace(/\0.*$/,'');
  const vsize = u32(o+8), va = u32(o+12), rawsize = u32(o+16), raw = u32(o+20);
  if (name === '.reloc'){ relocRVA = va; relocSize = vsize; relocRaw = raw; }
  console.log('sec', name.padEnd(8), 'VA=0x'+va.toString(16), 'vsize=0x'+vsize.toString(16), 'raw=0x'+raw.toString(16));
}
if (!relocRaw){ console.log('NO .reloc section -> no base relocations'); process.exit(0); }

const targets = [0x5222A7, 0x5222A6, 0x5222A0];
let found = {};
let p = relocRaw, end = relocRaw + relocSize, blocks = 0, entries = 0;
while (p + 8 <= end){
  const pageRVA = u32(p), blockSize = u32(p+4);
  if (blockSize === 0) break;
  const n = (blockSize - 8) / 2;
  for (let i=0;i<n;i++){
    const e = u16(p + 8 + i*2);
    const type = e >> 12, off = e & 0x0fff;
    entries++;
    const rva = pageRVA + off;
    for (const t of targets) if (rva === t) found[t] = type;
  }
  blocks++;
  p += blockSize;
}
console.log('.reloc blocks=' + blocks + ' entries=' + entries);
for (const t of targets) console.log('RVA 0x' + t.toString(16) + ' -> ' + (found[t]!==undefined ? ('RELOC type=' + found[t] + (found[t]===3?' (IMAGE_REL_BASED_HIGHLOW)':'')) : 'none'));
