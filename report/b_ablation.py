"""
Bảng ablation quanh CẤU HÌNH CHÍNH pair_skip_mlp_specfeat (chọn trên validation), 5 seed.
Mỗi biến thể chỉ thay MỘT thành phần; so với cấu hình chính bằng paired bootstrap trên truy vấn (điểm = TB các seed), Holm.
Chạy: python report/b_ablation.py
Ra:   report/results/b_ablation.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a_baselines import RES, paired_boot
from src.evaluation.metrics import ndcg_at_k

MAIN = "pair_skip_mlp_specfeat"
NAME = {"abl_nospec": "Bỏ cấp độ/số năm (đặc trưng + phạt)", "abl_nopen": "Bỏ phạt đơn điệu cấp độ/số năm",
        "abl_noreq": "Bỏ phân biệt bắt buộc/ưu tiên", "abl_mean": "max → mean", "abl_noattn": "attention → trọng số đều",
        "abl_bce": "loss pairwise → BCE", "abl_noskip": "Bỏ đường tắt cosine", "abl_L1": "+1 lớp GATv2", "abl_L2": "+2 lớp GATv2",
        "abl_L3": "+3 lớp GATv2", "m1": "top-m = 1", "m5": "top-m = 5", "me5": "Embedding mE5-base thay BGE-M3",
        "esco": "Chuẩn hóa kỹ năng ESCO (ngưỡng 0,85)"}
VAR = ("m1", "m5", "me5", "esco")


def load(setting):
    """Trả về (bảng điểm đã gộp, bảng nhãn). Biến thể top-m/embedding đổi tên config thành m1/m5/me5."""
    if setting == "ext":
        fs = [("ext_cna_req_jd_mlpsf.csv", None), ("ext_cna_req_jd_abl2a.csv", None), ("ext_cna_req_jd_abl2b.csv", None)] + \
             [(f"ext_cna_req_jd_abl2_{v}.csv", v) for v in VAR]
        lab = "ext_cna_static.csv"
    else:
        fs = [(f"req_{setting}_abl2.csv", None)] + [(f"req_{setting}_abl2_{v}.csv", v) for v in VAR]
        lab = "static_scores.csv"
    parts = []
    for f, v in fs:
        p = os.path.join(RES, f)
        if os.path.exists(p):
            x = pd.read_csv(p)
            if v:
                x["config"] = v
            parts.append(x)
    return pd.concat(parts), pd.read_csv(os.path.join(RES, lab))[["cv_id", "jd_id", "grade"]]


out = {}
for setting, title in (("jd", "Bộ đề tài — chia theo JD"), ("double", "Bộ đề tài — loại trừ hai chiều"), ("ext", "resume-job-fit — chia theo JD")):
    L, lab = load(setting)
    n = L.groupby(["cv_id", "jd_id", "config"]).size().unstack()
    keep = n.dropna().index                           # chỉ cặp mà mọi biến thể đều chấm
    L = L.set_index(["cv_id", "jd_id"]).loc[keep].reset_index()
    meta = L[["cv_id", "jd_id", "qid"]].drop_duplicates().merge(lab, on=["cv_id", "jd_id"])
    el = set(q for q, x in meta.groupby("qid") if len(x) >= 2 and (x.grade >= 2).any())

    def grp(df):
        a = df.merge(meta, on=["cv_id", "jd_id", "qid"])
        return {q: list(zip(x.grade, x.score)) for q, x in a[a.qid.isin(el)].groupby("qid")}

    cfgs = [MAIN] + [c for c in NAME if c in set(L.config)]
    per = {c: [np.mean([ndcg_at_k([g for g, _ in x], [s for _, s in x], 10) for x in grp(y).values()]) for _, y in L[L.config == c].groupby("seed")] for c in cfgs}
    avg = {c: grp(L[L.config == c].groupby(["cv_id", "jd_id", "qid"]).score.mean().reset_index()) for c in cfgs}
    res = [[c, *paired_boot(avg[c], avg[MAIN])] for c in cfgs[1:]]
    mx = 0.0
    for rank, i in enumerate(np.argsort([r[3] for r in res])):
        mx = max(mx, min(1.0, (len(res) - rank) * res[i][3]))
        res[i].append(mx)
    print(f"\n## {title}: {len(el)} truy vấn, {len(keep)} cặp; Holm {len(res)} so sánh")
    print(f"{'Biến thể':<40}{'NDCG@10':>16}{'Δ so với chính':>16}   CI95              p_Holm")
    print(f"{'Cấu hình chính (MLP + cấp độ/số năm)':<40}{np.mean(per[MAIN]):>9.3f}±{np.std(per[MAIN]):.3f}")
    out[setting] = {"n_queries": len(el), "main": {"mean": float(np.mean(per[MAIN])), "std": float(np.std(per[MAIN]))}, "ablations": []}
    for c, d, ci, p, ph in res:
        print(f"{NAME[c]:<40}{np.mean(per[c]):>9.3f}±{np.std(per[c]):.3f}{d:>+13.3f}   [{ci[0]:+.3f},{ci[1]:+.3f}]   {ph:.3f}")
        out[setting]["ablations"].append({"config": c, "name": NAME[c], "mean": float(np.mean(per[c])), "std": float(np.std(per[c])),
                                          "seeds": len(per[c]), "diff": d, "ci": ci, "p": p, "p_holm": ph})
json.dump(out, open(os.path.join(RES, "b_ablation.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
