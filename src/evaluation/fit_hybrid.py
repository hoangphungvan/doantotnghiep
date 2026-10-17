"""
Fit Hybrid Score (điểm cuối của hệ thống):  S = α · điểm_GCN + (1 − α) · điểm_SBERT_chuẩn_hóa

α tối đa hóa NDCG@10 theo danh sách của từng JD (nhà tuyển dụng xếp hạng CV cho mỗi JD) trên điểm GCN out-of-fold
(data/processed/cv_oof_predictions.csv, sinh bởi `train.py --cv 5`); min/max chuẩn hóa điểm SBERT lấy trên toàn bộ cặp.
Ghi models/hybrid.json, rồi hiệu chỉnh 3 ngưỡng quy điểm Hybrid ra mức 0-3 (tối đa macro-F1) ghi models/grade_thresholds.json.

    python src/evaluation/fit_hybrid.py              # α chọn theo NDCG@10
    python src/evaluation/fit_hybrid.py --alpha 0.5  # đặt α cố định (vẫn tính lại min/max và ngưỡng)
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.data_collection.prepare_training_data import load_all_graphs
from src.evaluation.calibrate_thresholds import OUT_JSON, apply, fit_thresholds
from src.evaluation.hybrid import HYBRID_FILE, _minmax_fit, compute_semantic_scores
from src.evaluation.metrics import evaluate_ranking

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--alpha", type=float, default=None, help="α cố định thay vì chọn theo NDCG@10")
    args = ap.parse_args()
    graphs = load_all_graphs()
    oof = pd.read_csv(os.path.join(config.DATA_PROCESSED_DIR, "cv_oof_predictions.csv")).set_index(["cv_id", "jd_id"]).gcn_score
    keys = [(g.cv_source, g.jd_source) for g in graphs]
    gs = np.array([oof[k] for k in keys])
    ss = compute_semantic_scores(graphs)
    y = np.array([int(g.y.item()) for g in graphs])
    jd = np.array([k[1] for k in keys])
    cv = np.array([k[0] for k in keys])
    norm = _minmax_fit(ss)(ss)

    def ndcg10(alpha):
        groups = {}
        for j, grade, s in zip(jd, y, alpha * gs + (1 - alpha) * norm):
            groups.setdefault(j, []).append((grade, float(s)))
        return evaluate_ranking(groups, ks=config.RANKING_KS)["ndcg@10"]

    alpha = args.alpha if args.alpha is not None else max(np.linspace(0, 1, 21), key=ndcg10)
    params = {"alpha": float(alpha), "sem_min": float(ss.min()), "sem_max": float(ss.max()), "n_pairs": len(graphs),
              "fitted_on": "điểm GCN out-of-fold, " + ("α đặt tay" if args.alpha is not None else "tối đa NDCG@10 theo danh sách của từng JD")}
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    with open(HYBRID_FILE, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2, ensure_ascii=False)

    h = alpha * gs + (1 - alpha) * norm
    cvs = np.array(sorted(set(cv)))
    np.random.default_rng(0).shuffle(cvs)
    fold = np.array([{c: i % 5 for i, c in enumerate(cvs)}[c] for c in cv])
    cross = np.zeros_like(y)
    for k in range(5):
        th, _ = fit_thresholds(h[fold != k], y[fold != k])
        cross[fold == k] = apply(h[fold == k], th)
    th, best = fit_thresholds(h, y)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"thresholds": th, "fitted_on": "điểm Hybrid, 5-fold CV theo CV", "objective": "macro_f1", "n_pairs": len(graphs),
                   "macro_f1_in_sample": round(best, 4), "macro_f1_cross_fit": round(f1_score(y, cross, average="macro"), 4)}, f, indent=2, ensure_ascii=False)
    print(f"α = {alpha:.2f}, NDCG@10 theo JD = {ndcg10(alpha):.3f} -> {HYBRID_FILE}")
    print(f"Ngưỡng mức 0-3: {[round(t, 3) for t in th]}; khớp chính xác cross-fit {np.mean(cross == y):.1%} -> {OUT_JSON}")
