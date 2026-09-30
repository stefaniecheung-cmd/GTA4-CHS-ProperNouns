/* build_v7.js - V7 overlay on top of 成品包v6 gxt.
   Merges the Phase-5 production translations (队列A+B, 1797 unique sentences -> Key-level rows in
   07-文本审计/已完成翻译汇总.tsv) as whole-entry hash overwrites.
   Gates: (1) current gxt value === 英文原文 (else report, no blind write);
          (2) control-code multiset equality (only ~n~ additions allowed);
          (3) M4i 3580 charset hard gate.
   Skipped rows: zh starts with 【 (线上挂起/保持原文/红线 markers) and zh===en no-ops.
   Fonts / mapfix.asi / char_table unchanged. Pack metadata fixed later by assemble_v7_pack.js. */
const fs = require('fs');
const { parseGxt, buildGxt } = require('./gxt_io.js');
const PROJ = 'E:/SteamLibrary/steamapps/common/Grand Theft Auto IV/汉化补丁工程/';
const B = PROJ + '03-补丁构建/';
const V6 = B + '成品包v6/';
const V7 = B + '成品包v7/';
const CHAR_TABLE = B + 'M4i字库包/plugins/GTA4.CHS/char_table.dat';
const SUMMARY = PROJ + '07-文本审计/已完成翻译汇总.tsv';
const CHAPS = { '本体': 'update/common/text/american.gxt', 'TLAD': 'update/TLAD/common/text/american.gxt', 'TBoGT': 'update/TBoGT/common/text/american.gxt' };

/* ---- charset gate (M4i 3580) ---- */
const ct = fs.readFileSync(CHAR_TABLE);
const nct = ct.readUInt32LE(0); const allowed = new Set();
for (let i = 0; i < nct; i++) allowed.add(ct.readUInt32LE(4 + i * 4));
const missing = s => [...new Set([...s].filter(ch => ch.codePointAt(0) >= 0x80 && !allowed.has(ch.codePointAt(0))))];
console.log('charset gate: M4i char_table ' + nct + ' codepoints');

/* ---- load key-level summary ---- */
const toks = s => (s.match(/~[^~]+~/g) || []).concat(s.match(/%[sd]|%lu|\{\d+\}/g) || []).sort().join(',');
const L = fs.readFileSync(SUMMARY, 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/).slice(1).filter(x => x.trim());
/* Packaging defect fix: queue key 603ba429 truly ends at "seen?" (verified in gxt), but its WIP
   unique sentence was polluted with the adjacent line's " One love." tail -> drop 愿你平安。
   scan16 couldn't match it (queue en != WIP en) so it is NOT in 已完成翻译汇总 — add manually. */
const MANUAL_EXTRA = [
  { key: '603ba429', chap: '本体', g: 'MF13AUD', en: '~z~Call me soon, Niko. I and I should link up sometime, seen?',
    zh: '~z~尽快打给我，尼克。咱们该找时间聚聚，明白？', pack: 'WIP-04(手工补)' },
];
const OVERRIDE = { '603ba429': MANUAL_EXTRA[0].zh };
const perChap = new Map(); // chap -> Map(hash -> {en, zh})
let skipMarker = 0, skipNoop = 0, applied = 0;
for (const line of L) {
  const c = line.split('\t');
  const [key, chap, g, pack, en, zh] = c.slice(0, 6);
  if (/^【/.test(zh || '')) { skipMarker++; continue; }
  if (!zh || zh === en) { skipNoop++; continue; }
  const finalZh = OVERRIDE[key] || zh;
  const tokEn = toks(en), tokZh = toks(finalZh);
  if (tokEn !== tokZh) {
    const addN = (finalZh.match(/~n~/g) || []).length - (en.match(/~n~/g) || []).length;
    if (!(addN > 0 && toks(en.replace(/~n~/g, '')) === toks(finalZh.replace(/~n~/g, '')))) {
      console.error('控制码不符: ' + key + ' ' + g + ' :: ' + en.slice(0, 50) + ' => ' + finalZh.slice(0, 50));
      process.exit(1);
    }
  }
  const bad = missing(finalZh);
  if (bad.length) { console.error('★ 字库硬闸 ' + key + ' 表外字 ' + bad.join('') + ' :: ' + finalZh.slice(0, 50)); process.exit(1); }
  if (!perChap.has(chap)) perChap.set(chap, new Map());
  const m = perChap.get(chap);
  const h = (parseInt(key, 16) >>> 0).toString(16);
  if (m.has(h)) console.log('注意: 重复 key ' + chap + '/' + h + ' (以最后一条为准)');
  m.set(h, { en, zh: finalZh, g, pack });
  applied++;
}
for (const t of MANUAL_EXTRA) {
  const bad = missing(t.zh);
  if (bad.length) { console.error('★ 字库硬闸(手工补) ' + t.key + ' 表外字 ' + bad.join('')); process.exit(1); }
  if (!perChap.has(t.chap)) perChap.set(t.chap, new Map());
  perChap.get(t.chap).set((parseInt(t.key, 16) >>> 0).toString(16), { en: t.en, zh: t.zh, g: t.g, pack: t.pack });
  applied++;
}
console.log('汇总行 ' + L.length + ' | 待写入 ' + applied + ' | 跳过标记行 ' + skipMarker + ' | 跳过原文保持 ' + skipNoop);

/* ---- stage V7 = copy v6 (载荷/字体/mapfix/bat/说明 均为 v6 态，assemble 再修元数据) ---- */
fs.rmSync(V7, { recursive: true, force: true });
fs.cpSync(V6, V7, { recursive: true });
/* V7i: 字库升级 …… ->M4h(3561, +郭)->M4i(3580, +19 字幕类用字) */
const M4F = B + 'M4i字库包/';
fs.copyFileSync(M4F + 'plugins/GTA4.CHS/char_table.dat', V7 + 'plugins/GTA4.CHS/char_table.dat');
for (const rel of ['update/pc/textures/fonts.wtd', 'update/TLAD/pc/textures/fonts.wtd', 'update/TBoGT/pc/textures/fonts.wtd'])
  fs.copyFileSync(M4F + rel, V7 + rel);
console.log('staged 成品包v7 = 成品包v6 + M4i 字库(3580) + V7 gxt');

/* ---- rewrite gxt ---- */
/* Match gates (汉化组基底常把 ASCII 标点改全角并吞掉空格，或残留 beta 尾巴):
   G1 exact; G2 alphanumeric-only equal (标点/空格形态差异); G3 cur === en + "(BETA)".
   bccd6ce7: base English 是真句但安装覆盖层里存的是字面 "~z~beta"，无法核实内容，永久跳过。 */
const SKIP_ALWAYS = new Set(['bccd6ce7']);
const alnum = s => s.replace(/[^A-Za-z0-9\u4e00-\u9fff]/g, '');
/* V7b 全局译名修正（用户 2026-09-19 拍板）：Lopez 洛佩斯->洛佩兹。
   在哈希合入之后跑，覆盖 M2 时代基底 + V7 批次译文里的所有旧写法；源表 人名译名表.tsv 已同步。 */
const GLOBAL_FIX = [['洛佩斯', '洛佩兹'], ['自由州', '自由城'], ['Joe 乔恩', '乔･乔恩']];
/* ---- V7d 体检修复层（2026-09-19 用户拍板：档1机检的二类真P0+三类整条已译/句内未替） ----
   GLOBAL=全库字面替换（跳过 CREDIT 与 LCPD 前缀组）；HASH=按哈希限定替换（歧义短词只动取证过的条目）。
   依据：07-文本审计 字幕体检报告 + _v7d_probe 取证（英文基底逐条核对）。 */
const V7D_GLOBAL = [
  ['Francis国际机场', '弗朗西斯国际机场'],   // 与区名表定名一致（M2 lookahead 盾当年把正确修法也挡了）
  ['约翰 Hunter', '约翰･亨特'],              // John Hunter 州长候选人全名，无歧义
  ['克里斯 Hunt', '克里斯･亨特'],            // Chris Hunt 动作明星全名
  ['Car 亚博维茨', '卡尔･亚博维茨'],          // 基底自己在 MAIN 电台句已译「卡尔･亚博维茨」，从其先例
  ['卡斯特尔 Gardens', '城堡花园'],          // =Castle Gardens 区名定名
  ['Ancelottis', '安切洛蒂家的'],
  ['金 Young-Guk', '金永国'],                // 韩裔名，汉字名惯例
];
const V7D_HASH = {
  /* 车名句内（车名表定名；只动取证哈希，Zombie 歌名/调试条目、CREDIT 姓氏不受影响） */
  '7aa88aec': [['Banshee', '女妖']], 'eac1728d': [['Cavalcade', '骑兵']],
  '667e16d3': [['Banshee', '女妖']], '743bb24e': [['Cavalcade', '骑兵']],
  'e64c9662': [['Sanchez', '桑切斯']], 'b9ccf9ad': [['Banshee', '女妖']],
  'efead628': [['Cavalcade', '骑兵']], '6fadc511': [['Sanchez', '桑切斯']],
  '4c73bd7a': [['Diabolus', '蒂雅布萝']], 'a1e7c38a': [['Zombie', '鞭尸者']],
  'fd4b7993': [['Hakuchou', '白鸟']], '15b7888d': [['Hellfury', '地狱之怒']],
  '40823f6b': [['Sanchez', '桑切斯']], 'a32440b6': [['Daemon', '恶魔']],
  /* 联系人名句内（v6 只做了整条） */
  '754665ac': [['Brett', '布雷特']], '9bdeb1b2': [['Beth', '贝丝']],
  '996a4c38': [['Cindy', '辛迪']], '1c262a4c': [['Leila', '莱拉']], 'c628a6c8': [['Leon', '莱昂']],
  /* 人名句内 */
  'c5eeee5f': [['Elizabeth', '伊丽莎贝塔']],   // 即 Elizabeta Torres，从基底既有译名
  'cd9cb607': [['Katerina', '卡捷琳娜']],
  '7d8af3b2': [['Vincenzo', '温琴佐']], 'b780405c': [['Vincenzo', '温琴佐']],
  'afab467': [['Mohammed', '穆罕默德']], '492ab0bf': [['Mohammed', '穆罕默德']],
  '5d0ce1e3': [['Philly', '菲利']],
  '1295c550': [['Davey仔', '戴维仔']], 'e8a4d0c5': [['Davey', '戴维']],
  '123e5831': [['McCornish', '麦科尼什']], '3b11450e': [['McCornish', '麦科尼什']], '6112f5dd': [['McCornish', '麦科尼什']],
  '4ab2a8c8': [['McCornish', '麦科尼什']], '68527693': [['埃德 McCornish', '埃德･麦科尼什']],
  'b9fee04a': [['Park的', '朴的']],
  /* 街名/地名句内（街名表/总表定名；站名标签类不动） */
  'b8aeecac': [['林登 Avenue', '林登大道']],
  '4fb502d5': [['弗里敦 Avenue', '弗里敦大道']],
  '2bdc433': [['加尔维斯顿 Avenue', '加尔维斯顿大道']],  '24566559': [['Frankfort大道', '法兰克福大道']], '272b58e7': [['Frankfort大道', '法兰克福大道']],
  'ae38ae48': [['Frankfort大道', '法兰克福大道']], '6d596738': [['Frankfort大道', '法兰克福大道']],
  '82e60fed': [['Savannah大道', '萨凡纳大道']], '2a5a1e16': [['Savannah大道', '萨凡纳大道']],
  'd8ef6aa2': [['Saratoga大道', '萨拉托加大道']], '93acf392': [['Saratoga大道', '萨拉托加大道']],
  '4d06f06d': [['San Quentin大道', '圣昆汀大道']], 'b810bd4a': [['San Quentin大道', '圣昆汀大道']],
  'bd4b3ac3': [['Union高速公路东段', '联合车道东']], '8df2a3b8': [['Union高速公路东段', '联合车道东']],
  'cc2169f4': [['Union高速公路西段', '联合车道西']], 'd6d13bed': [['Union高速公路', '联合车道']],
  '6d5a4af8': [['Hunt Point', '亨特角']], 'c0b483ab': [['Hunt Point', '亨特角']],
  '4fa6fe89': [['North Gardens', '北加登斯']],
  '3cb3a131': [['Franklyn街', '富兰克林街']],
  'f9f7a58f': [['Guernsey城', '根西']], 'bbc36a23': [['Guernsey城', '根西']],
  '84df1569': [['格雷格 Johnson州长公屋', '格雷格･约翰逊州长公屋']], 'ffd9178f': [['格雷格 Johnson州长公屋', '格雷格･约翰逊州长公屋']],
  'c225262': [['Holland', '荷兰']], '19ee6dfa': [['Holland', '荷兰']], 'e046443f': [['Holland', '荷兰']], 'ee67e082': [['Holland', '荷兰']],
  'ccdf54e3': [['Holland医院', '荷兰医院']],
  'a9d4d1fd': [['Richmond', '里士满']], '7ac589e6': [['Frogtown', '蛙镇']],
  '507dee3d': [['草地公园(梅多 Park)', '草地公园']],
  '6829fe0': [['(Beta1)', '']],
  '472e2ac5': [['约翰 Hunter', '约翰･亨特']],   // LCPDFJ 描述字段（非输入字段），哈希限定放行
  /* 2026-09-20 补（V7g 同轮"中文+英文片段"半译扫描所获，共 2 处）：
     ① 基底原文拼写不全 "Meadows Hills"，v6c 的 "Meadows"→梅多 只啃掉前半 → "梅多 Hills"（同族 18 处均作 梅多山）
     ② 基底整句已译但残留英文介词 by（非译名，属笔误级残留） */
  '8c2bd928': [['梅多 Hills', '梅多山']],
  'e1b94b5d': [['减少了by', '减少了']],
};
/* ---- V7e 站名标签层 + 四类拍板落地（2026-09-19 用户拍板：站名全译；圣迈克尔/凯奇/盖塔莱夫/锆石/杰克･豪泽/LibEl 统一） ----
   站名派生自街名表/区名表定名：Manganese St=锰街、Quartz St=石英街、Lynch St=林奇街、Huntington St=亨廷顿街、
   Schottler=舒特勒、Firefly Island=萤火虫岛；Low/High=地下/地上沿基底风格。 */
const V7E_GLOBAL = [
  ['杰克 Howitzer', '杰克･豪泽'],            // 人名与品牌分开口径（品牌 Howitzer 仍留英文）
];
const V7E_HASH = {
  /* 站名标签（地铁/车站） */
  '9d52bde9': [['San Quentin大道站', '圣昆汀大道站']],
  '7934f5ae': [['Frankfort地下站', '法兰克福地下站']],
  'd5ba2eb7': [['Frankfort大道站', '法兰克福大道站']],
  '1558316e': [['Frankfort地上站', '法兰克福地上站']],
  '86e01480': [['Manganese西站', '锰西街站']],
  '89e3995b': [['Manganese东站', '锰东街站']],
  'bbb37e26': [['Quartz西站', '石英西街站']],
  'f6be730f': [['Quartz东站', '石英东街站']],
  '9b483c24': [['下Huntington街站', '下亨廷顿街站']],
  'e653d23e': [['上Huntington街站', '上亨廷顿街站']],
  'c1d2093b': [['Lynch街站', '林奇街站']],
  'acedc560': [['Firefly Station, Broker.', '萤火虫站、布鲁克区。']],
  '5d6dcff2': [['SCHOTTLER车站', '舒特勒车站']],
  'd5bb547f': [['Police Station', '警察局']],
  '5e810bab': [['Huntington街车站', '亨廷顿街车站']],
  /* 四类拍板：圣迈克尔 / 凯奇 / 盖塔莱夫 / 锆石 / LibEl 拼写统一 */
  '5f9812e4': [['St. 迈克尔', '圣迈克尔']],
  'c0598710': [['St. 迈克尔', '圣迈克尔']],
  '85b73591': [['St 迈克尔', '圣迈克尔']],
  'e9195a1c': [['Catch', '凯奇']], '415c21c2': [['Catch', '凯奇']], '5e0aeb88': [['Catch', '凯奇']],
  '7570fcf0': [['Catch', '凯奇']], 'fb1ba446': [['Catch', '凯奇']],
  'e99b3c30': [['GetaLife', '盖塔莱夫']], '798770b5': [['GetaLife', '盖塔莱夫']], '7fbddd15': [['GetaLife', '盖塔莱夫']],
  '46d8c643': [['Zirconium', '锆石']], 'c8848730': [['Zirconium', '锆石']],
  '1d8d5455': [['Libel', 'LibEl']],
  'b287d4cf': [[' (BETA)', ''], ['(BETA)', '']],
  /* TBoGT 赛点标签与赛道名 */
  '664066ae': [['Meadows Park & Ride', '梅多斯公园换乘停车场']],
  '6fb989f0': [['Meadows Park & Ride', '梅多斯公园换乘停车场']],
  'c64b7f26': [['Meadows Park & Ride', '梅多斯公园换乘停车场']],
  '6d4cede6': [['Catch Your Wave', '乘风破浪']],
  'a247efec': [['Catch Your Wave', '乘风破浪']],
  /* Mollis 药名：用户拍板留英文，标签条目从 v5 期"莫利斯"回退（对白 7 处本就是英文，保持一致） */
  'ae63e9cc': [['莫利斯', 'Mollis']],
};
/* ---- V7f 基底译法对齐 + 播报补全（2026-09-20 用户拍板：与无名汉化组既定译法冲突的一律以汉化组为准）
   依据 _v7f_probe9-15 三态取证（EN/基底BAK/V7）。全部哈希限定，命中即替换，未命中即报错。
   A 基底对齐：8 个区名标签 + Firefly Projects + 我方早期自拟条目（星光路口/公爵区林荫大道/大林荫大道/
     Grand大街/自由银行/欢乐之地/Triangle 句内）；B 播报补全：本体 50 条 ~z~~x~ 进区弹窗 + TLAD 34 /
     TBoGT 26 条问答句（基底把前缀译了、地名留英文的同类漏翻）。 */
const V7F_ALIGN = {
  /* 区名标签（gen_zone_table_v7 从本 gxt 取值写 zone_table.h，mapfix 自动跟随） */
  '3aab5d6f': [['市中心', '中心区']],      // 基底对白一贯"中心区"（呃...中心区/市中心泛指保留）
  'c1933590': [['交易所', '证交区']],      // 基底对白"证交区"
  '9046cb6b': [['梅多斯公园', '草地公园']],  // 基底对白"对，草地公园"
  '84caa700': [['星光路口', '星汇广场']],   // 基底对白"星汇广场"
  'e004fbfd': [['中央公园', '中心公园']],   // 基底对白"中心公园"
  'e4e985c6': [['中央公园', '中心公园']],
  'ca6b50be': [['中央公园', '中心公园']],
  '94b9442f': [['利珀斯大桥', '纵身大桥']],  // 基底对白"呃...纵身大桥"
  /* Firefly Projects：基底散文一贯作「(Firefly)公屋社区」（约 20 处），区名表旧值「住宅区」对齐 */
  '8cbf2c37': [['住宅区', '公屋社区']],
  /* 我方早期条目对齐（基底同族用法） */
  '824863b1': [['星光路口', '星汇广场']], '73fdc71c': [['星光路口', '星汇广场']], '329ed1dc': [['星光路口', '星汇广场']],
  'c23bb42d': [['自由银行', '自由城银行'], ['星光路口', '星汇广场']],
  'd5430756': [['星光路口', '星汇广场']],
  'bb297b1': [['中央公园', '中心公园']],
  'ff97f205': [['公爵区林荫大道', '公爵区大街']],
  '3a1ad45f': [['公爵区林荫大道', '公爵区大街']], '28753114': [['公爵区林荫大道', '公爵区大街']], '139e9284': [['公爵区林荫大道', '公爵区大街']],
  '5caccc81': [['大林荫大道', '格兰德大街']],
  '945dc2e3': [['Grand大街', '格兰德大街']],
  /* Triangle 句内（基底留英文；区名表 THTRI=三角区） */
  '2d7a03aa': [['Triangle', '三角区']], '23c93857': [['Triangle', '三角区']],
  '45c73dd1': [['Triangle', '三角区']], 'bb213725': [['Triangle', '三角区']],
  /* Funland：基底对白作「游乐园」（进入游乐园/前往游乐园的另一边） */
  'ec646c17': [['欢乐之地', '游乐园']], '72039538': [['Funland', '游乐园']],
  /* TBoGT 换乘停车场：沿区名表新值 草地公园 */
  '664066ae': [['梅多斯公园', '草地公园']], '6fb989f0': [['梅多斯公园', '草地公园']], 'c64b7f26': [['梅多斯公园', '草地公园']],
};
const V7F_ZH = {
  'Beachgate': '比奇盖特', 'Boulevard': '林荫大道', 'Little Bay': '小湾', 'Northern Gardens': '北方花园',
  'Fortside': '福特赛德', 'South Bohan': '南波汉', 'Chase Point': '追逐角', 'Rotterdam Hill': '鹿特丹山',
  'Steinway': '斯坦威', 'Meadow Hills': '梅多山', 'Cerveza Heights': '塞尔维萨高地', 'Willis': '威利斯',
  'Schottler': '舒特勒', 'Beechwood City': '比奇伍德城', 'East Hook': '东胡克', 'Boabo': '博阿博',
  'South Slopes': '南坡', 'Hove Beach': '霍夫海滩', 'Firefly Island': '萤火虫岛', 'Outlook': '奥特卢克',
  'Anger Bay': '安格尔湾', 'Castle Gardens': '城堡花园', 'Castle Garden City': '城堡花园城',
  'Norfolk': '诺福克', 'Suffolk': '萨福克', 'Lower Easton': '下伊斯顿', 'Easton': '伊斯顿',
  'The Triangle': '三角区', 'The Meat Quarter': '肉类区', 'Presidents City': '总统城', 'Lancet': '兰塞特',
  'Westminster': '威斯敏斯特', 'Purgatory': '炼狱', 'Hatton Gardens': '哈顿花园', 'Lancaster': '兰开斯特',
  'Varsity Heights': '大学高地', 'North Holland': '北荷兰', 'East Holland': '东荷兰',
  'Jefferson Heights': '杰弗逊高地', 'Northwood': '北伍德', 'Westdyke': '韦斯代克', 'Leftwood': '左伍德',
  'Berchem': '伯尔赫姆', 'Normandy': '诺曼底', 'Acter': '阿克特', 'Acter Bay': '阿克特湾', 'Tudor': '都铎',
  'Richmond': '里士满', 'Frogtown': '蛙镇',
};
const V7F_FILL_LIST = {
  '本体': {
    '812071f9': 'Beachgate', '4ad2e5a7': 'Boulevard', '63eba2cc': 'Little Bay', '8b61ca17': 'Northern Gardens',
    '2432eb3c': 'Fortside', '95221e3e': 'South Bohan', '7a529ce3': 'Chase Point', '2da71140': 'Rotterdam Hill',
    'c9fc7237': 'Steinway', 'a02c4b7f': 'Meadow Hills', '81607ec1': 'Cerveza Heights', 'a28de0f7': 'Willis',
    '8e758ab2': 'Schottler', 'b899485c': 'Beechwood City', '2ebf78ce': 'East Hook', 'c5875ace': 'Boabo',
    'a4a7b974': 'South Slopes', 'cc0c05d7': 'Hove Beach', 'b8d5f67f': 'Firefly Island', '76125b1b': 'Outlook',
    '7b9349e9': 'Anger Bay', '5755e7a7': 'Castle Gardens', '659974c0': 'Castle Garden City', 'b98df66d': 'Norfolk',
    'a4412356': 'Suffolk', '4f1100ad': 'Lower Easton', '8a21bf70': 'Easton', 'b8a77020': 'The Triangle',
    '50c1fdb8': 'The Meat Quarter', 'a3e0633a': 'Presidents City', '2b16930b': 'Lancet', 'ed5222d0': 'Westminster',
    '152c6428': 'Purgatory', 'c79101b6': 'Hatton Gardens', '49fd1286': 'Lancaster', '15ec9142': 'Varsity Heights',
    '8e812f8f': 'North Holland', '88e0b396': 'East Holland', '8ee6aad6': 'Jefferson Heights', '4c0298e9': 'Northwood',
    '6dc14e34': 'Westdyke', '243dd18': 'Leftwood', '25c43979': 'Berchem', '972f3243': 'Normandy',
    'c3b439af': 'Acter', '743119a6': 'Acter Bay', '7774a87d': 'Tudor', 'c977f2aa': 'Richmond', 'de99787': 'Frogtown',
    '35414aef': 'Anger Bay',   // 裸条目（区名级；基底在 TLAD 问答已把它当地名处理）
  },
  'TLAD': {
    'ebf73fbe': 'Beachgate', '35e0ded5': 'Boulevard', '96965376': 'South Bohan', '77c40338': 'Chase Point',
    '5acbe819': 'Rotterdam Hill', '96c032b7': 'Meadow Hills', 'b30e3cfc': 'Cerveza Heights', '2b0d828a': 'Beechwood City',
    '357565b1': 'East Hook', 'c76bf981': 'Boabo', '6b3d28a8': 'South Slopes', 'd4e8f919': 'Firefly Island',
    '3ccaa211': 'Anger Bay', '27482c31': 'Castle Gardens', '9cfbe36a': 'Castle Garden City', 'ec2dee0f': 'Norfolk',
    'f8d6889': 'Suffolk', '5835fd3c': 'Easton', '471ca272': 'The Triangle', 'e52ee7eb': 'The Meat Quarter',
    '1c56fd7a': 'Westminster', '46e66724': 'Purgatory', '5e2e1af0': 'Hatton Gardens', '42958f51': 'Lancaster',
    '4f891dba': 'North Holland', '3d56b747': 'East Holland', '236221b7': 'Jefferson Heights', 'd5ac052': 'Northwood',
    '9b5f2316': 'Westdyke', 'e9ea4c0d': 'Berchem', 'b4c5cba7': 'Acter Bay', 'c31d5c32': 'Tudor',
    '9865f339': 'Richmond', 'b7dc4b87': 'Frogtown',
  },
  'TBoGT': {
    'af003c85': 'Little Bay', '74813646': 'Fortside', '22932f85': 'Rotterdam Hill', '3be26edd': 'Schottler',
    '19d229b5': 'Beechwood City', '6d1407f2': 'East Hook', '13ba5e63': 'South Slopes', '758c9fc7': 'Firefly Island',
    'b3c47498': 'Anger Bay', 'ae2beaa1': 'Castle Gardens', '85bbd475': 'Norfolk', '2ba15465': 'Suffolk',
    'b9cc7dd1': 'The Triangle', '311132bd': 'The Meat Quarter', '967ebc66': 'Lancet', '40403c36': 'Westminster',
    '30fb8cbc': 'Hatton Gardens', '65942bf2': 'Lancaster', '46005691': 'North Holland', '3d061a58': 'Jefferson Heights',
    'a13dd3af': 'Northwood', 'a76549b3': 'Westdyke', '6a5ece10': 'Berchem', 'd2b32a09': 'Acter',
    'bad7c9ba': 'Acter Bay', 'f07d4f3a': 'Tudor',
  },
};
const V7F_FILL = {};
for (const [chap, m] of Object.entries(V7F_FILL_LIST)) {
  V7F_FILL[chap] = {};
  for (const [h, name] of Object.entries(m)) {
    if (!V7F_ZH[name]) { console.error('V7F 译名映射缺项: ' + name); process.exit(1); }
    V7F_FILL[chap][h] = [[name, V7F_ZH[name]]];
  }
}
/* ---- V7g 警车电脑（LCPD 警察数据库）地址字段（2026-09-20 用户拍板：只翻罪犯地址即可，前提不影响按名搜索）
   PDB_ADDR_0..29 = 「View Most Wanted / Search Police Records」每条档案的 HANGOUT 地址行（本体独有）。
   其中 PDB_ADDR_0/3（含街名）早先已随街名层译出，值不动；余 28 条本次整条替换，格式沿已译两条（全角逗号）。
   分界：需玩家键入的姓名字段（Bellic/Crane/…）、罪名行、组内描述一律不动。
   PDB_ADDR_9/17 是地标式地址（机场/公寓楼），同样只在本字段出现。裸大区名非 info.zon 键，不影响地图。 */
const V7G_HASH = {
  '6f7f45fd': ['Northern Gardens, Bohan', '北方花园，波汉'],
  'f08c4815': ['South Slopes, Broker', '南坡，布洛克'],
  '94008eff': ['BOABO, Broker', '博阿博，布洛克'],
  'b5c2d283': ['Steinway, Dukes', '斯坦威，公爵区'],
  'd7a49642': ['Steinway, Dukes', '斯坦威，公爵区'],
  'e919b92c': ['Steinway, Dukes', '斯坦威，公爵区'],
  'fad05c99': ['Meadows Park, Dukes', '草地公园，公爵区'],
  'fc9c6031': ['Francis International Airport', '弗朗西斯国际机场'],
  '851edc3c': ['North Holland, Algonquin', '北荷兰，阿尔冈琴'],
  '57408080': ['Middle Park, Algonquin', '中心公园，阿尔冈琴'],
  '3251b69f': ['Purgatory, Algonquin', '炼狱，阿尔冈琴'],
  '23f299e1': ['East Holland, Algonquin', '东荷兰，阿尔冈琴'],
  '4ed56fa6': ['Northwood, Algonquin', '北伍德，阿尔冈琴'],
  '408152fe': ['Fishmarket South, Algonquin', '鱼市南，阿尔冈琴'],
  'db49888c': ['Fishmarket South, Algonquin', '鱼市南，阿尔冈琴'],
  'cd18ec2b': ['Colony Island Apartments', '殖民地岛公寓楼'],
  'f7ff41f7': ['Star Junction, Algonquin', '星汇广场，阿尔冈琴'],
  'e999a52c': ['Castle Garden City, Algonquin', '城堡花园城，阿尔冈琴'],
  'c24e24a': ['Westdyke, Alderney', '韦斯代克，奥尔德尼'],
  'fe6b46d7': ['Leftwood, Alderney', '左伍德，奥尔德尼'],
  '877ed90c': ['Leftwood, Alderney', '左伍德，奥尔德尼'],
  'e0060a19': ['Alderney City, Alderney', '奥尔德尼市，奥尔德尼'],
  '9638f680': ['Alderney City, Alderney', '奥尔德尼市，奥尔德尼'],
  '1247ee9c': ['Normandy, Alderney', '诺曼底，奥尔德尼'],
  '3cb14372': ['Berchem, Alderney', '伯尔赫姆，奥尔德尼'],
  '4b5ce0c9': ['Berchem, Alderney', '伯尔赫姆，奥尔德尼'],
  'eedd27c7': ['Tudor, Alderney', '都铎，奥尔德尼'],
  '391dbc4b': ['Tudor, Alderney', '都铎，奥尔德尼'],
};
const gSeen = new Set(); // V7g 命中自检
/* ---- V7j 收尾两族（2026-09-20 用户拍板"开译"）：
   A. "地标, 区" 地址串 14 条（本体 MAIN；同族 2 条 M11 已译——自由城银行，星汇广场。/都市停车场，星汇广场。→ 补齐消混排）。
   B. LCPD 档案组位置行 12 行（Alderney，Acter / Westdyke / Leftwood —— 基底只改了逗号，名字留英文）。
   全部 hash 限定整条替换；要求当前值 === 英文原文。字段均为显示用，不涉键入姓名与地图 info.zon 键。 */
const V7J_HASH = {
  'c261e9c0': ['Suffolk, Algonquin.', '萨福克，阿尔冈琴。'],
  '62fb22c4': ['Little Italy, Algonquin.', '小意大利，阿尔冈琴。'],
  '5460858f': ['Construction Site, The Exchange.', '建筑工地，证交区。'],
  'b6bf9c3d': ['East Holland, Algonquin.', '东荷兰，阿尔冈琴。'],
  'c8503f5e': ['Northwood, Algonquin.', '北伍德，阿尔冈琴。'],
  '1bb91441': ['Car Park, Little Italy.', '停车场，小意大利。'],
  'a94bafcc': ['Varsity Heights, Algonquin.', '大学高地，阿尔冈琴。'],
  '6f8c8dcc': ['Barium St., Algonquin.', '钡街，阿尔冈琴。'],
  'ed620975': ['Union Drive East, Algonquin.', '联合车道东，阿尔冈琴。'],
  '67ed7d6a': ['Jade Street, Algonquin.', '玉街，阿尔冈琴。'],
  '9a89e2a2': ['Calcium Street, Algonquin.', '钙街，阿尔冈琴。'],
  '6c3c0607': ['Uranium Street, ALgonquin.', '铀街，阿尔冈琴。'],
  'cc9606c1': ['Burger Shot, Alderney.', 'Burger Shot，奥尔德尼。'],
  'a4b5f057': ["Manny's Youth Center, Bohan.", '曼尼青年中心，波汉。'],
  '247c14af': ['Alderney，Acter', '奥尔德尼，阿克特'],
  '28cd2d73': ['Alderney，Acter', '奥尔德尼，阿克特'],
  '44b96413': ['Alderney，Acter', '奥尔德尼，阿克特'],
  'a6dd19a7': ['Alderney，Acter', '奥尔德尼，阿克特'],
  '42a4be38': ['Alderney，Acter', '奥尔德尼，阿克特'],
  '5f9de5b2': ['Alderney，Acter', '奥尔德尼，阿克特'],
  '45821e50': ['Alderney，Acter', '奥尔德尼，阿克特'],
  'e96d4194': ['Alderney，Acter', '奥尔德尼，阿克特'],
  '91ae10e3': ['Alderney，Westdyke', '奥尔德尼，韦斯代克'],
  'eff292f3': ['Alderney，Westdyke', '奥尔德尼，韦斯代克'],
  '4e1732d2': ['Alderney，Westdyke', '奥尔德尼，韦斯代克'],
  'ec4cb33b': ['Alderney，Leftwood', '奥尔德尼，左伍德'],
};
const jSeen = new Set(); // V7j 命中自检
/* ---- V7h 半译人名 + 全名分隔符（2026-09-20 用户拍板 A 方案："遇到英文名，判断是否为人名；
   某一部分在人名表里已有的（无论作为全名/姓氏/名字的一部分）直接对着译；表里没有的按人名常规音译；
   中文全名成分之间的空格统一为 ･"）。规则一律带中文语境锚点，绝不命中纯英文句；CREDIT 组与
   8 个同源盾（Joe "Tuna" DiLeo / Johnny "Spaz" Barbosa / Katt Williams / Ricky Gervais /
   Frankie Boyle / Bluesy St. John / Bobby Konders / Anna Rex）不在规则内。 */
const V7H_RULES = [
  /* A 混排人名：中文名 + 英文部分（或英文部分 + 中文名）→ 接 ･；姓氏单独出现按 先生/议员/船长 语境 */
  [/博比\s+Jefferson/g, '博比･杰斐逊'], [/博迪\s+Jefferson/g, '博迪･杰斐逊'], [/Jefferson(?=[先议])/g, '杰斐逊'],
  [/桑尼\s+Cangelosi/g, '桑尼･坎杰洛西'],
  [/蒂福尔\s+Maxwell-Davies/g, '蒂福尔･麦克斯韦-戴维斯'],
  [/希斯克利夫\s+Waterstreet/g, '希斯克利夫･沃特斯特里特'],
  [/佐尔巴\s+Philippidis/g, '佐尔巴･菲利皮迪斯'], [/Philippidis(?=船长)/g, '菲利皮迪斯'],
  [/特拉维斯\s+Evans/g, '特拉维斯･埃文斯'], [/Evans(?=议员)/g, '埃文斯'],
  [/艾登\s+O'Mally/g, '艾登･奥马利'],
  [/菲尔\s+Kensington/g, '菲尔･肯辛顿'],
  [/玛丽\s+Mayfly/g, '玛丽･梅弗莱'],
  [/莫娜\s+Arthurs/g, '莫娜･阿瑟斯'],
  [/妻子Betania/g, '妻子贝塔尼娅'],
  [/Elisabeth\s+兰开特/g, '伊丽莎白･兰开特'],
  [/Earth-Song\s+鲍登/g, '厄斯桑･鲍登'],
  [/Chuck\s+蒙特雷斯/g, '查克･蒙特雷斯'],
  [/绰号"Ambrosia\(神的食物\)"/g, '绰号"安布罗西亚(神的食物)"'],
  [/路易斯\s+Fertinatta/g, '路易斯･费尔蒂纳塔'],
  [/Vincent\s+卢皮塞拉/g, '文森特･卢皮塞拉'],
  [/西沃恩\s+Phillips/g, '西沃恩･菲利普斯'],
  [/桑德拉\s+McColland/g, '桑德拉･麦科兰'],
  [/尤金\s+Reaper/g, '尤金･里珀'],
  [/Sarah\s+莱文/g, '萨拉･莱文'],
  [/Daisy\s+Cash-Cooze/g, '黛西･卡什-库兹'],
  [/Mark\s+"Loopy"\s+卢皮塞拉/g, '马克･"鲁皮"･卢皮塞拉'], [/"Loopy\(暴躁\)"/g, '"鲁皮(暴躁)"'],
  [/可以让Angela/g, '可以让安吉拉'],
  [/给Katy打个电话/g, '给凯蒂打个电话'],
  [/，Sal，/g, '，萨尔，'], [/，Mark，/g, '，马克，'],
  [/闭嘴，Brain。/g, '闭嘴，布莱恩。'], [/丢下了Brain的团伙/g, '丢下了布莱恩的团伙'],
  [/哟，Jeffy。/g, '哟，杰菲。'],
  [/Katja华尔兹/g, '卡佳华尔兹'],
  /* B 中文全名成分空格 → ･（基底同位置为两个英文单词，已逐条核对；不含呼语/非人名配对） */
  [/帕特里克 麦克雷里/g, '帕特里克･麦克雷里'], [/Mark\s+安东尼 沃尔佩/g, '马克･安东尼･沃尔佩'],
  [/路易斯 费尔南多 洛佩兹/g, '路易斯･费尔南多･洛佩兹'], [/路易斯 费尔南多/g, '路易斯･费尔南多'],
  [/胡里奥 奥乔亚/g, '胡里奥･奥乔亚'], [/塔尔博特 丹尼尔斯/g, '塔尔博特･丹尼尔斯'],
  [/泰迪 贝纳维德/g, '泰迪･贝纳维德'], [/拉里 林纳/g, '拉里･林纳'], [/莱尔 克利索普/g, '莱尔･克利索普'],
  [/乔恩 阿特金森/g, '乔恩･阿特金森'], [/迈克尔 基恩/g, '迈克尔･基恩'], [/曼尼 埃斯库埃/g, '曼尼･埃斯库埃'],
  [/迈克 洛雷蒂/g, '迈克･洛雷蒂'], [/埃文 莫斯/g, '埃文･莫斯'], [/菲尔 罗森堡/g, '菲尔･罗森堡'],
  [/琪琪 詹金斯/g, '琪琪･詹金斯'], [/弗兰基 加罗内/g, '弗兰基･加罗内'], [/格雷丝 安切洛蒂/g, '格雷丝･安切洛蒂'],
  [/杰丰 辛普森/g, '杰丰･辛普森'], [/艾萨克 罗斯/g, '艾萨克･罗斯'], [/玛尼 艾伦/g, '玛尼･艾伦'],
  [/乔瓦尼 安切洛蒂/g, '乔瓦尼･安切洛蒂'], [/雅各布 休斯/g, '雅各布･休斯'], [/安东尼 沃尔佩/g, '安东尼･沃尔佩'],
  [/戈登 萨金特/g, '戈登･萨金特'], [/巴基 斯莱戈/g, '巴基･斯莱戈'], [/汤姆 皮雷尼/g, '汤姆･皮雷尼'],
  [/吉米 卡斯特/g, '吉米･卡斯特'], [/加文 安东尼/g, '加文･安东尼'],
];
/* V7h 泛化尾补：显式规则之后仍残留的英文人名 token（中文语境锚点，纯英文句绝不命中）；
   「中文+空格+英文」在显式规则里已按人名处理，这里只收尾：英文+空格+中文→接 ･；紧贴中文→直连。 */
const V7H_GENERIC = ['Jefferson', 'Philippidis', 'Evans', 'Cangelosi', 'Maxwell-Davies', 'Waterstreet', 'Fitzgerald', 'Kensington', 'Mayfly', 'Arthurs', 'Betania', 'Elisabeth', 'Earth-Song', 'Ambrosia', 'Fertinatta', 'Vincent', 'Phillips', 'McColland', 'Reaper', 'Loopy', 'O\'Mally', 'Angela', 'Sarah', 'Katy', 'Katja', 'Jeffy', 'Mally', 'Cash-Cooze', 'Daisy']
  .map(en => {
    const ZH = { 'Jefferson': '杰斐逊', 'Philippidis': '菲利皮迪斯', 'Evans': '埃文斯', 'Cangelosi': '坎杰洛西', 'Maxwell-Davies': '麦克斯韦-戴维斯', 'Waterstreet': '沃特斯特里特', 'Fitzgerald': '菲茨杰拉德', 'Kensington': '肯辛顿', 'Mayfly': '梅弗莱', 'Arthurs': '阿瑟斯', 'Betania': '贝塔尼娅', 'Elisabeth': '伊丽莎白', 'Earth-Song': '厄斯桑', 'Ambrosia': '安布罗西亚', 'Fertinatta': '费尔蒂纳塔', 'Vincent': '文森特', 'Phillips': '菲利普斯', 'McColland': '麦科兰', 'Reaper': '里珀', 'Loopy': '鲁皮', 'O\'Mally': '奥马利', 'Angela': '安吉拉', 'Sarah': '萨拉', 'Katy': '凯蒂', 'Katja': '卡佳', 'Jeffy': '杰菲', 'Mally': '马利', 'Cash-Cooze': '卡什-库兹', 'Daisy': '黛西' }[en];
    const e = en.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return [
      [new RegExp('\\b' + e + '\\s+([\\u4e00-\\u9fff])', 'g'), ZH + '･$1'],
      [new RegExp('\\b' + e + '(?=[\\u4e00-\\u9fff])', 'g'), ZH],
      [new RegExp('([\\u4e00-\\u9fff])\\s*\\b' + e + '\\b', 'g'), '$1' + ZH],
      [new RegExp('([，。、；：？！「」『』])\\s*\\b' + e + '\\b', 'g'), '$1' + ZH],
    ];
  })
  .flat();
const hSeen = new Set();
const hSeenRule = new Set();
/* ---- V7i 挂起桶·字幕类翻译层（2026-09-20 用户拍板："挂起桶里以字幕形式(~z~)出现的都要翻译，
   人名按 V7h 口径逐词全译"）。数据源 = 07-文本审计/批次工作包/字幕类-WIP-NN.tsv 里已填中文的行。 */
const V7I = new Map();
{
  const dir = PROJ + '07-文本审计/批次工作包/';
  for (const f of fs.readdirSync(dir).filter(x => /^字幕类-WIP-\d+\.tsv$/.test(x)).sort()) {
    const lines = fs.readFileSync(dir + f, 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/).slice(1);
    for (const l of lines) {
      if (!l.trim()) continue;
      const c = l.split('\t');
      if (!c[4] || !c[4].trim()) continue;
      const h = (parseInt(c[0], 16) >>> 0).toString(16);
      if (V7I.has(h)) { console.error('★ V7i 重复哈希 ' + h); process.exit(1); }
      V7I.set(h, { tag: c[1], g: c[2], en: c[3], zh: c[4] });
    }
  }
  console.log('V7i 待写入字幕类译文 ' + V7I.size + ' 条');
}
const iSeen = new Set();
/* ---- V7k 两处地名改名（2026-09-20 用户拍板："证交所改成证券交易所 / 中心公园改成中央公园，
   同步更新出现这些地名的文本，不考虑汉化组的基底"）——全库（含基底自己的 79 处）字面替换。
   单条正则 + 交替（长优先），避免"交易所"把新写的"证券交易所"再吃一遍。 */
const V7K_RULES = [
  [/证交所|证交区|交易所/g, '证券交易所'],
  [/中心公园/g, '中央公园'],
];
const kCount = { 证券交易所: 0, 中央公园: 0 };
const fSeen = new Set(); // V7f 命中自检
const changes = [];
const rowIndex = new Map(); // tag|hash -> changes row (batch+gfix merge into one ledger line)
const stats = { miss: [], mismatch: [], punct: 0, beta: 0, gfix: 0, gfixMerge: 0, v7d: 0, v7dMerge: 0, v7e: 0, v7eMerge: 0, v7f: 0, v7fMerge: 0, v7g: 0, v7gMerge: 0, v7h: 0, v7hMerge: 0, v7i: 0, v7iMerge: 0, v7j: 0, v7jMerge: 0, v7k: 0, v7kMerge: 0 };
for (const [tag, rel] of Object.entries(CHAPS)) {
  const m = perChap.get(tag) || new Map();
  const f = V7 + rel;
  const g = parseGxt(f);
  const hit = new Set();
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    for (const it of r.items) {
      if (it.s == null) continue;
      const hk = (it.hash >>> 0).toString(16);
      const t = m.get(hk);
      if (!t) continue;
      if (SKIP_ALWAYS.has(hk)) { hit.add(hk); continue; }
      if (t.g !== gname) { console.log('组名不符(以gxt为准): ' + hk + ' 汇总=' + t.g + ' gxt=' + gname); }
      if (hit.has(hk)) { console.log('同哈希多条目: ' + tag + '/' + hk); }
      hit.add(hk);
      const orig = it.s;
      if (orig === t.zh) continue; // idempotent re-run
      if (orig === t.en) { /* G1 */ }
      else if (alnum(orig) === alnum(t.en)) { stats.punct++; }
      else if (orig === t.en + '(BETA)') { stats.beta++; }
      else { stats.mismatch.push(tag + '/' + hk + ' [' + gname + '] 当前值≠英文原文 :: ' + orig.slice(0, 60)); continue; }
      const oldBad = new Set(missing(orig));
      const bad = missing(t.zh).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸 [' + tag + '/' + gname + '] ' + hk + ' 新增表外字 ' + bad.join('')); process.exit(1); }
      it.s = t.zh;
      const row = { tag, g: gname, h: hk, old: orig, neu: t.zh, pack: t.pack };
      changes.push(row);
      rowIndex.set(tag + '|' + hk, row);
    }
  }
  /* V7b 全局修正 pass */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    for (const it of r.items) {
      if (it.s == null) continue;
      let s = it.s;
      for (const [a, b] of GLOBAL_FIX) s = s.split(a).join(b);
      if (s === it.s) continue;
      const oldBad = new Set(missing(it.s));
      const bad = missing(s).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(gfix) ' + tag + '/' + gname + ' ' + (it.hash >>> 0).toString(16) + ' ' + bad.join('')); process.exit(1); }
      const hk = (it.hash >>> 0).toString(16);
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = s; row.pack += '+V7b修订'; stats.gfixMerge++; }
      else {
        changes.push({ tag, g: gname, h: hk, old: it.s, neu: s, pack: 'V7b(全局修订)' });
        rowIndex.set(tag + '|' + hk, changes[changes.length - 1]);
      }
      it.s = s;
      stats.gfix++;
    }
  }
  /* V7d 体检修复 pass：HASH=人工取证条目，任何组都可动（含 LCPD 描述字段——非输入字段，安全）；
     GLOBAL=字面替换，跳过 CREDIT 与 LCPD 前缀组（防误伤名单/防卡关字段） */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    const globalOk = !/^CREDIT/.test(gname) && !/^LCPD/.test(gname);
    for (const it of r.items) {
      if (it.s == null) continue;
      const hk = (it.hash >>> 0).toString(16);
      let s = it.s;
      const hops = V7D_HASH[hk];
      if (hops) for (const [a, b] of hops) s = s.split(a).join(b);
      if (globalOk) for (const [a, b] of V7D_GLOBAL) s = s.split(a).join(b);
      if (s === it.s) continue;
      const oldBad = new Set(missing(it.s));
      const bad = missing(s).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(v7d) ' + tag + '/' + gname + ' ' + hk + ' ' + bad.join('')); process.exit(1); }
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = s; row.pack += '+V7d'; stats.v7dMerge++; }
      else {
        const nr = { tag, g: gname, h: hk, old: it.s, neu: s, pack: 'V7d(体检修复)' };
        changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
      }
      it.s = s;
      stats.v7d++;
    }
  }
  /* V7e 站名标签 + 四类拍板 pass */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    const globalOk = !/^CREDIT/.test(gname) && !/^LCPD/.test(gname);
    for (const it of r.items) {
      if (it.s == null) continue;
      const hk = (it.hash >>> 0).toString(16);
      let s = it.s;
      const hops = V7E_HASH[hk];
      if (hops) for (const [a, b] of hops) s = s.split(a).join(b);
      if (globalOk) for (const [a, b] of V7E_GLOBAL) s = s.split(a).join(b);
      if (s === it.s) continue;
      const oldBad = new Set(missing(it.s));
      const bad = missing(s).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(v7e) ' + tag + '/' + gname + ' ' + hk + ' ' + bad.join('')); process.exit(1); }
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = s; row.pack += '+V7e'; stats.v7eMerge++; }
      else {
        const nr = { tag, g: gname, h: hk, old: it.s, neu: s, pack: 'V7e(站名标签)' };
        changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
      }
      it.s = s;
      stats.v7e++;
    }
  }
  /* V7f 基底译法对齐 + 播报补全 pass（hash 限定；依据 _v7f_probe9-15 三态 EN/BAK/V7 取证） */
  for (const [fmap, fpack] of [[V7F_ALIGN, 'V7f(基底对齐)'], [V7F_FILL[tag] || {}, 'V7f(播报补全)']]) {
    for (const r of g.recs) {
      const gname = r.name.replace(/\0+$/, '');
      for (const it of r.items) {
        if (it.s == null) continue;
        const hk = (it.hash >>> 0).toString(16);
        const hops = fmap[hk];
        if (!hops) continue;
        let s = it.s;
        for (const [a, b] of hops) s = s.split(a).join(b);
        if (s === it.s) continue;
        const oldBad = new Set(missing(it.s));
        const bad = missing(s).filter(x => !oldBad.has(x));
        if (bad.length) { console.error('★ 字库硬闸(v7f) ' + tag + '/' + gname + ' ' + hk + ' ' + bad.join('')); process.exit(1); }
        const row = rowIndex.get(tag + '|' + hk);
        if (row) { row.neu = s; row.pack += '+V7f'; stats.v7fMerge++; }
        else {
          const nr = { tag, g: gname, h: hk, old: it.s, neu: s, pack: fpack };
          changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
        }
        it.s = s;
        stats.v7f++;
        fSeen.add(hk);
      }
    }
  }
  /* V7g 警车电脑地址 pass：整条替换，且要求当前值 === 英文原文（未命中/值不符均报错） */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    for (const it of r.items) {
      if (it.s == null) continue;
      const hk = (it.hash >>> 0).toString(16);
      const hop = V7G_HASH[hk];
      if (!hop) continue;
      const [en, zh] = hop;
      if (it.s === zh) { gSeen.add(hk); continue; } // 幂等重跑
      if (it.s !== en) { stats.mismatch.push('v7g ' + tag + '/' + hk + ' [' + gname + '] 当前值≠英文原文 :: ' + it.s.slice(0, 60)); continue; }
      const oldBad = new Set(missing(it.s));
      const bad = missing(zh).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(v7g) ' + tag + '/' + gname + ' ' + hk + ' 新增表外字 ' + bad.join('')); process.exit(1); }
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = zh; row.pack += '+V7g'; stats.v7gMerge++; }
      else {
        const nr = { tag, g: gname, h: hk, old: it.s, neu: zh, pack: 'V7g(警车电脑地址)' };
        changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
      }
      it.s = zh;
      stats.v7g++;
      gSeen.add(hk);
    }
  }
  /* V7h 半译人名/分隔符 pass（正则带中文锚点；CREDIT 组与盾名不涉） */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    if (/^CREDIT/.test(gname)) continue;
    for (const it of r.items) {
      if (it.s == null) continue;
      let s = it.s;
      const hitRule = [];
      for (const [re, rep] of V7H_RULES.concat(V7H_GENERIC)) { const t = s.replace(re, rep); if (t !== s) { s = t; hitRule.push(String(re).slice(1, 44)); } }
      if (s === it.s) continue;
      const oldBad = new Set(missing(it.s));
      const bad = missing(s).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(v7h) ' + tag + '/' + gname + ' ' + (it.hash >>> 0).toString(16) + ' ' + bad.join('')); process.exit(1); }
      const hk = (it.hash >>> 0).toString(16);
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = s; row.pack += '+V7h'; stats.v7hMerge++; }
      else {
        const nr = { tag, g: gname, h: hk, old: it.s, neu: s, pack: 'V7h(半译人名)' };
        changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
      }
      it.s = s;
      stats.v7h++;
      for (const x of hitRule) { hSeen.add(x); hSeenRule.add(x); }
    }
  }
  /* V7i 字幕类整条替换（要求当前值 === 英文原文，允许标点形态差；控制码必须一致） */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    for (const it of r.items) {
      if (it.s == null) continue;
      const hk = (it.hash >>> 0).toString(16);
      const t = V7I.get(hk);
      if (!t) continue;
      if (it.s === t.zh) { iSeen.add(hk); continue; }
      const okExact = it.s === t.en;
      const okAlnum = alnum(it.s) === alnum(t.en);
      if (!okExact && !okAlnum) { stats.mismatch.push('v7i ' + tag + '/' + hk + ' [' + gname + '] 当前值≠英文原文 :: ' + it.s.slice(0, 60)); continue; }
      if (toks(it.s) !== toks(t.zh)) {
        const addN = (t.zh.match(/~n~/g) || []).length - (it.s.match(/~n~/g) || []).length;
        if (!(addN > 0 && toks(it.s.replace(/~n~/g, '')) === toks(t.zh.replace(/~n~/g, '')))) { stats.mismatch.push('v7i 控制码不符 ' + tag + '/' + hk + ' :: ' + it.s.slice(0, 50)); continue; }
      }
      const oldBad = new Set(missing(it.s));
      const bad = missing(t.zh).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(v7i) ' + tag + '/' + gname + ' ' + hk + ' 新增表外字 ' + bad.join('')); process.exit(1); }
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = t.zh; row.pack += '+V7i'; stats.v7iMerge++; }
      else {
        const nr = { tag, g: gname, h: hk, old: it.s, neu: t.zh, pack: 'V7i(字幕类)' };
        changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
      }
      it.s = t.zh;
      stats.v7i++;
      iSeen.add(hk);
    }
  }
  /* V7j 收尾两族 pass（hash 限定整条替换；当前值必须 === 英文原文） */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    for (const it of r.items) {
      if (it.s == null) continue;
      const hk = (it.hash >>> 0).toString(16);
      const hop = V7J_HASH[hk];
      if (!hop) continue;
      const [en, zh] = hop;
      if (it.s === zh) { jSeen.add(hk); continue; }
      if (it.s !== en) { stats.mismatch.push('v7j ' + tag + '/' + hk + ' [' + gname + '] 当前值≠英文原文 :: ' + it.s.slice(0, 60)); continue; }
      const oldBad = new Set(missing(it.s));
      const bad = missing(zh).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(v7j) ' + tag + '/' + gname + ' ' + hk + ' 新增表外字 ' + bad.join('')); process.exit(1); }
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = zh; row.pack += '+V7j'; stats.v7jMerge++; }
      else {
        const nr = { tag, g: gname, h: hk, old: it.s, neu: zh, pack: 'V7j(收尾两族)' };
        changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
      }
      it.s = zh;
      stats.v7j++;
      jSeen.add(hk);
    }
  }
  /* V7k 改名 pass（全库字面替换，跳过 CREDIT；含基底自己的译文） */
  for (const r of g.recs) {
    const gname = r.name.replace(/\0+$/, '');
    if (/^CREDIT/.test(gname)) continue;
    for (const it of r.items) {
      if (it.s == null) continue;
      let s = it.s;
      for (const [re, rep] of V7K_RULES) s = s.replace(re, (m) => { kCount[rep] = (kCount[rep] || 0) + 1; return rep; });
      if (s === it.s) continue;
      const oldBad = new Set(missing(it.s));
      const bad = missing(s).filter(x => !oldBad.has(x));
      if (bad.length) { console.error('★ 字库硬闸(v7k) ' + tag + '/' + gname + ' ' + (it.hash >>> 0).toString(16) + ' 新增表外字 ' + bad.join('')); process.exit(1); }
      const hk = (it.hash >>> 0).toString(16);
      const row = rowIndex.get(tag + '|' + hk);
      if (row) { row.neu = s; row.pack += '+V7k'; stats.v7kMerge++; }
      else {
        const nr = { tag, g: gname, h: hk, old: it.s, neu: s, pack: 'V7k(改名)' };
        changes.push(nr); rowIndex.set(tag + '|' + hk, nr);
      }
      it.s = s;
      stats.v7k++;
    }
  }
  for (const hk of m.keys()) if (!hit.has(hk)) stats.miss.push(tag + '/' + hk);
  fs.writeFileSync(f, buildGxt(g));
  console.log('[' + tag + '] rewritten, hits=' + hit.size + '/' + m.size);
}
const fAll = new Set(Object.keys(V7F_ALIGN));
for (const fm of Object.values(V7F_FILL)) for (const hk of Object.keys(fm)) fAll.add(hk);
const fMiss = [...fAll].filter(hk => !fSeen.has(hk));
if (fMiss.length) { console.error('★ V7f 未命中哈希 ' + fMiss.length + ' 个: ' + fMiss.join(' ')); process.exit(3); }
console.log('V7f 覆盖自检: ' + fSeen.size + '/' + fAll.size + ' 全部命中');
const gMiss = Object.keys(V7G_HASH).filter(hk => !gSeen.has(hk));
if (gMiss.length) { console.error('★ V7g 未命中哈希 ' + gMiss.length + ' 个: ' + gMiss.join(' ')); process.exit(3); }
console.log('V7g 覆盖自检: ' + gSeen.size + '/' + Object.keys(V7G_HASH).length + ' 全部命中');
console.log('V7h 规则命中自检: ' + hSeen.size + '/' + (V7H_RULES.length + V7H_GENERIC.length) + ' 条规则至少各命中一次');
{ const all = V7H_RULES.concat(V7H_GENERIC).map(([re]) => String(re).slice(1, 44)); const miss = all.filter(x => !hSeenRule.has(x)); if (miss.length) console.log('  V7h 未命中规则 ' + miss.length + ' 条（多为兜底/已被显式规则吃掉）: ' + miss.join(' | ')); }
console.log('V7 写入 ' + changes.length + ' 条 (标点归一 ' + stats.punct + ' / BETA尾巴 ' + stats.beta + ' / V7b全局修订 ' + stats.gfix + ' 并入批次行 ' + stats.gfixMerge + ' / V7d体检修复 ' + stats.v7d + ' / V7e站名拍板 ' + stats.v7e + ' / V7f基底对齐+播报补全 ' + stats.v7f + ' / V7g警车电脑地址 ' + stats.v7g + ' / V7h半译人名 ' + stats.v7h + ' / V7i字幕类 ' + stats.v7i + ' / V7j收尾两族 ' + stats.v7j + ' / V7k改名 ' + stats.v7k + ' 并入既有行 ' + (stats.v7dMerge + stats.v7eMerge + stats.v7fMerge + stats.v7gMerge + stats.v7hMerge + stats.v7iMerge + stats.v7jMerge + stats.v7kMerge) + ') | 未命中 ' + stats.miss.length + ' | 值不符 ' + stats.mismatch.length + ' | 永久跳过 ' + SKIP_ALWAYS.size);
const iMiss = [...V7I.keys()].filter(hk => !iSeen.has(hk));
if (iMiss.length) console.error('★ V7i 未命中哈希 ' + iMiss.length + ' 个: ' + iMiss.slice(0, 10).join(' '));
const jMiss = Object.keys(V7J_HASH).filter(hk => !jSeen.has(hk));
if (jMiss.length) { console.error('★ V7j 未命中哈希 ' + jMiss.length + ' 个: ' + jMiss.join(' ')); process.exit(3); }
console.log('V7j 覆盖自检: ' + jSeen.size + '/' + Object.keys(V7J_HASH).length + ' 全部命中');
for (const x of stats.miss) console.log('  MISS ' + x);
for (const x of stats.mismatch.slice(0, 20)) console.log('  MISMATCH ' + x);
if (stats.miss.length || stats.mismatch.length) { console.error('存在未命中/值不符，请核查后再放行'); process.exit(2); }

const det = ['tag\tgroup\thash\t批次\tafter(v6)\tnew(v7)'];
for (const c of changes) det.push([c.tag, c.g, c.h, c.pack, c.old.replace(/[\t\n]/g, ' '), c.neu.replace(/[\t\n]/g, ' ')].join('\t'));
fs.writeFileSync(B + 'V7改动明细.tsv', '\uFEFF' + det.join('\n'), 'utf8');
console.log('改动明细 -> V7改动明细.tsv (' + changes.length + ' 条)');
