# -*- coding: utf-8 -*-
import io, json, hashlib, os, datetime

base = r"C:\Game\gta4-chs"
p = os.path.join(base, "data", "review", "润色线-断点.json")
d = json.load(io.open(p, encoding="utf-8-sig"))

def sha16(path):
    h = hashlib.sha256(io.open(path, "rb").read()).hexdigest().upper()
    return h[:16]

def sha_full(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

d["updated"] = now
d["p1"] = {"total": 7950, "offset_done": 7950, "remaining": 0, "next_from": 7951,
           "note": "P1 队列 1-7950 全批走完（6366 起分段推进到 7950）"}
d["p3"] = {"total": 18725, "offset_done": 18725, "remaining": 0, "next_from": 18726}
d["p4"] = {"total": 30369, "offset_done": 30369, "remaining": 0, "next_from": 30370}
d["p2"] = {"total": 1113, "offset_done": 0, "remaining": 1113, "next_from": 7951,
           "note": "未动。TBoGT|MAIN 的 Email/短信长句"}

d["passed_offset"] = 57044
d["remaining"] = 1113
d["next_from"] = 7951

# counts
zg = os.path.join(base, "data", "zh_global.tsv")
log = os.path.join(base, "data", "review", "上游润色_审读日志.tsv")
rows_zg = sum(1 for _ in io.open(zg, encoding="utf-8")) - 1
rows_log = sum(1 for _ in io.open(log, encoding="utf-8-sig")) - 1
d["counts"] = {"zh_global_rows": rows_zg, "review_log_rows": rows_log,
               "qa": "合计：检查 14040 条，错误 0，警告 17"}

d["artifacts_sha256"] = {
    "zh_global": sha_full(zg),
    "review_log": sha_full(log),
    "zchs_gxt": sha16(os.path.join(base, "build", "zchs_base_tr.gxt")),
}

d["build"] = {
    "src_regenerated": False,
    "gxt_base_tr": {"bytes": os.path.getsize(os.path.join(base, "build", "zchs_base_tr.gxt")),
                    "sha256_16": sha16(os.path.join(base, "build", "zchs_base_tr.gxt"))},
    "gxt_TLAD_tr": {"bytes": os.path.getsize(os.path.join(base, "build", "zchs_TLAD_tr.gxt")),
                    "sha256_16": sha16(os.path.join(base, "build", "zchs_TLAD_tr.gxt"))},
    "gxt_TBoGT_tr": {"bytes": os.path.getsize(os.path.join(base, "build", "zchs_TBoGT_tr.gxt")),
                     "sha256_16": sha16(os.path.join(base, "build", "zchs_TBoGT_tr.gxt"))},
    "applied": {"base": 9661, "TLAD": 2486, "TBoGT": 2816},
    "deployed": False,
    "deployed_batch": "p49725（游戏侧仍为 P4 收尾版 2,669,910）",
}

d.setdefault("notes_log", []).append({
    "at": now, "offset": 7950,
    "note": "P1 队列全部走完（6366→7950 共 34 批）；base 生效 9,661 条，zchs_base_tr.gxt 2,670,200 字节，qa 检查 14,040 条 0 错误 / 17 警告；尚未部署到游戏侧",
})

io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=2))
print("updated:", now, "zh_global_rows", rows_zg, "log_rows", rows_log)
