"""
Hiệu chỉnh ngưỡng chuyển điểm GCN (sigmoid ∈ [0,1]) sang mức 0..3.

Cách cũ round(score*3) giả định điểm phân bố đều theo mức; thực tế GCN dồn điểm về giữa thang nên
hầu như mọi cặp rơi vào mức 1-2. Ở đây tìm 3 ngưỡng t1<t2<t3 tối đa hóa kappa trọng số bình phương
trên điểm out-of-fold (data/processed/cv_oof_predictions.csv, sinh bởi `train.py --cv 5`).

Đánh giá trung thực bằng cross-fit: ngưỡng cho mỗi fold được tìm trên các fold còn lại.
Kết quả cuối (khớp toàn bộ điểm out-of-fold) lưu vào models/grade_thresholds.json.

Chạy: python src/evaluation/calibrate_thresholds.py
"""

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, cohen_kappa_score, confusion_matrix, f1_score

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config

OOF_CSV = os.path.join(config.DATA_PROCESSED_DIR, "cv_oof_predictions.csv")
OUT_JSON = os.path.join(config.MODEL_DIR, "grade_thresholds.json")


def apply(scores, th):
    return np.searchsorted(np.asarray(th), scores, side="right")  # <t1→0, [t1,t2)→1, [t2,t3)→2, ≥t3→3


OBJECTIVES = {
    "qwk": lambda g, p: cohen_kappa_score(g, p, weights="quadratic"),
    "macro_f1": lambda g, p: f1_score(g, p, average="macro"),
    "balanced_acc": lambda g, p: balanced_accuracy_score(g, p),
}


def fit_thresholds(scores, grades, objective="macro_f1", iters=6):
    """Khởi tạo bằng cách khớp tỉ lệ từng mức, rồi dò từng ngưỡng (coordinate descent) tối đa hóa `objective`."""
    share = np.cumsum([np.mean(grades == g) for g in range(config.NUM_GRADES)])
    th = list(np.quantile(scores, share))
    grid = np.unique(np.quantile(scores, np.linspace(0.01, 0.99, 300)))
    qwk = lambda t: OBJECTIVES[objective](grades, apply(scores, t))
    best = qwk(th)
    for _ in range(iters):
        moved = False
        for i in range(3):
            lo = th[i - 1] if i else -np.inf
            hi = th[i + 1] if i < 2 else np.inf
            for c in grid[(grid > lo) & (grid < hi)]:
                cand = th.copy(); cand[i] = c
                k = qwk(cand)
                if k > best + 1e-9:
                    best, th, moved = k, cand, True
        if not moved:
            break
    return [float(x) for x in th], best


def report(name, grades, pred):
    print(f"{name:<22} khớp chính xác {np.mean(pred == grades):.1%} | ±1 {np.mean(abs(pred - grades) <= 1):.1%} | "
          f"QWK {cohen_kappa_score(grades, pred, weights='quadratic'):.3f} | "
          f"macro-F1 {f1_score(grades, pred, average='macro'):.3f} | "
          f"nhị phân(>=2) {np.mean((pred >= 2) == (grades >= 2)):.1%}")


if __name__ == "__main__":
    df = pd.read_csv(OOF_CSV)
    s, g = df.gcn_score.values, df.grade.values
    cvs = np.array(sorted(df.cv_id.unique()))
    np.random.default_rng(0).shuffle(cvs)
    fold_of = {c: i % 5 for i, c in enumerate(cvs)}
    fold = df.cv_id.map(fold_of).values

    old = np.clip(np.rint(s * config.NUM_GRADES), 0, config.NUM_GRADES).astype(int)
    cross = np.zeros_like(g)
    for f in range(5):
        th, _ = fit_thresholds(s[fold != f], g[fold != f])
        cross[fold == f] = apply(s[fold == f], th)

    print(f"{len(df)} cặp out-of-fold, {df.cv_id.nunique()} CV\n")
    report("Cách cũ round(s*3)", g, old)
    report("Ngưỡng hiệu chỉnh*", g, cross)
    print("(*) cross-fit: ngưỡng mỗi fold tìm trên 4 fold còn lại\n")
    for name, pred in (("Cách cũ", old), ("Hiệu chỉnh (cross-fit)", cross)):
        print(f"Ma trận nhầm lẫn — {name} (hàng = nhãn thật, cột = dự đoán):")
        print(pd.DataFrame(confusion_matrix(g, pred, labels=range(4)), index=range(4), columns=range(4)), "\n")
    print("Phân bố dự đoán — thật:", np.bincount(g, minlength=4), "| cũ:", np.bincount(old, minlength=4),
          "| hiệu chỉnh:", np.bincount(cross, minlength=4))

    th, k = fit_thresholds(s, g)
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"thresholds": th, "fitted_on": "out-of-fold GCN scores, 5-fold CV theo CV", "objective": "macro_f1",
                   "n_pairs": int(len(df)), "macro_f1_in_sample": round(k, 4),
                   "macro_f1_cross_fit": round(f1_score(g, cross, average="macro"), 4)},
                  f, indent=2)
    print(f"\nNgưỡng cuối (t1,t2,t3): {[round(x, 3) for x in th]} → {OUT_JSON}")
