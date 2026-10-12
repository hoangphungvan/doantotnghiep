"""
Kiểm tra ngưỡng SEMANTIC_MATCH_THRESHOLD (khớp ngữ nghĩa trong diễn giải) trên tập nhãn tay.

data/processed/semantic_match_labels.csv: 178 cặp (mục CV, mục JD) không trùng chuỗi, cosine >= 0.5, lấy mẫu
phân tầng theo cosine từ 600 cặp CV-JD; label = 1 nếu mục CV thực sự đáp ứng mục JD (đồng nghĩa, dịch,
viết tắt, hoặc cụ thể hơn rõ ràng). `weight` đưa mẫu phân tầng về phân bố thật của các ứng viên khớp.
Một người gán nhãn (Claude), không nhìn cosine khi gán.

Chạy: python src/evaluation/calibrate_semantic_threshold.py
"""

import os
import sys

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config

df = pd.read_csv(os.path.join(config.DATA_PROCESSED_DIR, "semantic_match_labels.csv"))
y, w = df.label.values == 1, df.weight.values


def prf(mask, t):
    p = (df.cos.values >= t) & mask
    tp, fp, fn = w[p & y].sum(), w[p & ~y].sum(), w[mask & ~p & y].sum()
    pr, rc = tp / (tp + fp) if tp + fp else 0, tp / (tp + fn) if tp + fn else 0
    return pr, rc, (1.25 * pr * rc / (0.25 * pr + rc) if pr + rc else 0)  # F0.5: ưu tiên precision


print(f"{len(df)} cặp có nhãn; ngưỡng hiện tại = {config.SEMANTIC_MATCH_THRESHOLD}")
print("ngưỡng | precision | recall | F0.5")
for t in np.arange(0.6, 0.91, 0.05):
    print("%.2f   | %.2f      | %.2f   | %.2f" % ((t,) + prf(np.ones(len(df), bool), t)))

rng, best = np.random.default_rng(0), []
ts = np.arange(0.6, 0.9, 0.025)
for _ in range(500):
    idx = rng.integers(0, len(df), len(df))
    d, yy, ww = df.cos.values[idx], y[idx], w[idx]
    f = []
    for t in ts:
        p = d >= t
        tp, fp, fn = ww[p & yy].sum(), ww[p & ~yy].sum(), ww[~p & yy].sum()
        pr, rc = tp / (tp + fp) if tp + fp else 0, tp / (tp + fn) if tp + fn else 0
        f.append(1.25 * pr * rc / (0.25 * pr + rc) if pr + rc else 0)
    best.append(ts[int(np.argmax(f))])
print("Ngưỡng tối ưu F0.5 (bootstrap): trung vị %.3f, khoảng 90%% [%.3f, %.3f]" % (np.median(best), *np.percentile(best, [5, 95])))
