# -*- coding: utf-8 -*-
import io, json, os, hashlib, shutil

P = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\review\润色线-断点.json"
d = json.loads(io.open(P, encoding="utf-8").read())

def sz(p):
    return os.path.getsize(p)
def sha16(p):
    h = hashlib.sha256(open(p, "rb").read()).hexdigest().upper()
    return h[:16]

b = r"C:\Game\Grand Theft Auto IV\gta4-chs\build"
zg = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\zh_global.tsv"
lg = r"C:\Game\Grand Theft Auto IV\gta4-chs\data\review\上游润色_审读日志.tsv"

d["updated"] = "2026-11-09 23:40:00"
d["p2"] = {"total": 1113, "offset_done": 1113, "remaining": 0, "next_from": 1114,
           "note": "P2 队列 7951-9063 全批走完（每批 100 条，末批 113 条）"}
d["passed_offset"] = 58157
d["remaining"] = 0
d["next_from"] = 1114
d["counts"] = {
    "zh_global_rows": sum(1 for _ in io.open(zg, encoding="utf-8")) - 1,
    "review_log_rows": sum(1 for _ in io.open(lg, encoding="utf-8-sig")) - 1,
    "qa": "合计：检查 14109 条，错误 0，警告 17",
}
d["build"]["gxt_base_tr"] = {"bytes": sz(os.path.join(b, "zchs_base_tr.gxt")), "sha256_16": sha16(os.path.join(b, "zchs_base_tr.gxt"))}
d["build"]["gxt_TLAD_tr"] = {"bytes": sz(os.path.join(b, "zchs_TLAD_tr.gxt")), "sha256_16": sha16(os.path.join(b, "zchs_TLAD_tr.gxt"))}
d["build"]["gxt_TBoGT_tr"] = {"bytes": sz(os.path.join(b, "zchs_TBoGT_tr.gxt")), "sha256_16": sha16(os.path.join(b, "zchs_TBoGT_tr.gxt"))}
d["build"]["applied"] = {"base": 9709, "TLAD": 2497, "TBoGT": 2826}
d["build"]["deployed"] = False
d["build"]["deployed_batch"] = "p49725（游戏侧仍为 P4 收尾版 2,669,910）"
d["artifacts_sha256"] = {
    "zh_global": hashlib.sha256(open(zg, "rb").read()).hexdigest(),
    "review_log": hashlib.sha256(open(lg, "rb").read()).hexdigest(),
    "zchs_gxt": d["build"]["gxt_base_tr"]["sha256_16"],
}
d["notes_log"].append({
    "at": "2026-11-09 23:40:00",
    "offset": 1113,
    "note": "P2 队列全部走完（7951→1113 共 12 批）；base 生效 9,709 条，zchs_base_tr.gxt 2,670,198 字节，qa 检查 14,109 条 0 错误 / 17 警告；尚未部署到游戏侧",
})

shutil.copy2(P, P + ".bak_before_p2end")
io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=2))
print("p2 done; zh_global_rows", d["counts"]["zh_global_rows"], "log_rows", d["counts"]["review_log_rows"])
print("gxt", d["build"]["gxt_base_tr"]["bytes"], d["build"]["gxt_TLAD_tr"]["bytes"], d["build"]["gxt_TBoGT_tr"]["bytes"])
