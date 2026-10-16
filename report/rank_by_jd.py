"""
Đánh giá theo góc nhìn nhà tuyển dụng: với MỖI JD, xếp hạng các CV theo điểm giảm dần.
Dùng lại điểm out-of-fold đã có (oof_all_methods.csv, oof_ablation.csv); chỉ đổi cách nhóm (theo jd_id thay vì cv_id).
Chỉ xét JD có >= 2 CV và có ít nhất một CV phù hợp (mức >= 2) để NDCG, Recall, MRR cùng một tập truy vấn.

Chạy: python report/rank_by_jd.py   ->  report/results/by_jd.json
"""

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.evaluation.metrics import evaluate_ranking

RES = os.path.join(ROOT, "report", "results")
d = pd.read_csv(os.path.join(RES, "oof_all_methods.csv"))
ab = pd.read_csv(os.path.join(RES, "oof_ablation.csv"))
d = d.merge(ab.drop(columns=["grade"]), on=["cv_id", "jd_id"])

size = d.groupby("jd_id").size()
rel = d.groupby("jd_id").grade.apply(lambda x: (x >= 2).any())
keep = [j for j in size.index if size[j] >= 2 and rel[j]]
d = d[d.jd_id.isin(keep)]
print("JD đủ điều kiện:", len(keep), "/", len(size), "| số cặp:", len(d), "| CV trung bình mỗi JD: %.1f" % size[keep].mean())

methods = {"TF-IDF + cosine": "tfidf", "SBERT + cosine": "sbert", "MLP (SBERT)": "mlp", "GCN": "gcn_score",
           "Hybrid tuyến tính (GCN + SBERT)": "hybrid", "Mô hình đề xuất (GCN + LLM + GBM)": "stack_score"}
for c in ab.columns[3:]:
    methods[c] = c
KS = [1, 3, 5, 10]


def groups(col):
    return {j: list(zip(g.grade, g[col])) for j, g in d.groupby("jd_id")}


rng = np.random.default_rng(0)
out = {"n_jd": len(keep), "n_pairs": int(len(d)), "mean_cv_per_jd": float(size[keep].mean()), "rows": []}
for name, col in methods.items():
    g = groups(col)
    r = evaluate_ranking(g, ks=KS)
    ids = list(g)
    boots = {k: [] for k in ("ndcg@5", "ndcg@10", "mrr")}
    for _ in range(500):
        pick = rng.integers(0, len(ids), len(ids))
        rb = evaluate_ranking({i: g[ids[p]] for i, p in enumerate(pick)}, ks=KS)
        for k in boots:
            if rb[k] is not None:
                boots[k].append(rb[k])
    row = {"method": name, **{k: r[k] for k in ["ndcg@1", "ndcg@3", "ndcg@5", "ndcg@10", "recall@5", "recall@10", "mrr"]}}
    for k in boots:
        row[k + "_ci"] = [float(np.percentile(boots[k], 2.5)), float(np.percentile(boots[k], 97.5))]
    out["rows"].append(row)
    print(name, {k: round(v, 3) for k, v in row.items() if isinstance(v, float)}, flush=True)
json.dump(out, open(os.path.join(RES, "by_jd.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
