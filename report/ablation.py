"""
Ablation cho mô hình đề xuất: bỏ từng thành phần, cùng cách chia 5-fold theo CV (seed 42) với experiments.py.

  - GBM chỉ đặc trưng LLM (6)            : không GCN, không cosine
  - GBM đặc trưng LLM + cosine (7)       : không GCN
  - GBM cosine + điểm GCN                : không đặc trưng LLM (dùng điểm GCN out-of-fold 5-fold; rò rỉ nhẹ, xem ghi chú báo cáo)
Hai biến thể đầu không dùng điểm GCN nên không có rò rỉ.

Chạy sau experiments.py:  python report/ablation.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "report"))
import config
from experiments import K, bootstrap_ci, classification_metrics, folds_of, ranking_metrics
from src.data_collection.prepare_training_data import load_all_graphs
from src.modeling.stacker import make_stacker, topic_features
from src.modeling.train import attach_pair_features, get_query_id

graphs = load_all_graphs()
attach_pair_features(graphs)
folds = folds_of(graphs)
pf = torch.cat([g.g_feat for g in graphs]).numpy()
cos = topic_features(graphs)
y = np.array([g.y.item() for g in graphs])
cv = np.array([g.cv_source for g in graphs])
jd = np.array([g.jd_source for g in graphs])
oof = pd.read_csv(os.path.join(config.DATA_PROCESSED_DIR, "cv_oof_predictions.csv")).set_index(["cv_id", "jd_id"]).gcn_score
gcn = np.array([oof[(c, j)] for c, j in zip(cv, jd)])
fold = np.array([next(i for i, te in enumerate(folds) if c in te) for c in cv])

variants = {"GBM: chỉ đặc trưng LLM": pf, "GBM: đặc trưng LLM + cosine (không GCN)": np.hstack([pf, cos]),
            "GBM: cosine + điểm GCN (không đặc trưng LLM)": np.hstack([cos, gcn[:, None]])}
rows = []
scores = pd.DataFrame({"cv_id": cv, "jd_id": jd, "grade": y.astype(int)})
for name, X in variants.items():
    s = np.zeros(len(y))
    for f in range(K):
        m = fold == f
        s[m] = make_stacker().fit(X[~m], y[~m]).predict(X[m])
    scores[name] = s
    df = pd.DataFrame({"cv_id": cv, "jd_id": jd, "grade": y.astype(int), "s": s})
    r = ranking_metrics(df, "s")
    ci = bootstrap_ci(df, "s", ["ndcg@5", "ndcg@10", "mrr"])
    cm = classification_metrics(df, "s", fold)
    pred = np.clip(np.rint(s), 0, 3)
    rows.append({"method": name, **{k: r[k] for k in ["ndcg@1", "ndcg@3", "ndcg@5", "ndcg@10", "recall@5", "recall@10", "mrr"]},
                 "ndcg@5_ci": ci["ndcg@5"], "ndcg@10_ci": ci["ndcg@10"], "mrr_ci": ci["mrr"], **cm,
                 "exact": float((pred == y).mean()), "within1": float((abs(pred - y) <= 1).mean())})
    print(name, {k: round(v, 3) for k, v in rows[-1].items() if isinstance(v, float)}, flush=True)
json.dump(rows, open(os.path.join(ROOT, "report", "results", "ablation.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
scores.to_csv(os.path.join(ROOT, "report", "results", "oof_ablation.csv"), index=False)
