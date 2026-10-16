"""
Thực nghiệm bổ sung cho báo cáo (Chương 2, mục 2.6): baseline MLP, độ đo phân loại cho mọi phương pháp,
khoảng tin cậy bootstrap theo CV.

Tất cả dùng CHUNG cách chia: 5-fold theo CV (seed 42, giống src/modeling/train.py::cross_validate).
Điểm GCN lấy từ data/processed/cv_oof_predictions.csv, điểm mô hình đề xuất (lồng nhau) từ stack_oof_predictions.csv.

Chạy từ thư mục gốc dự án:  python report/experiments.py
Kết quả ghi vào report/results/ (JSON + CSV).
"""

import json
import os
import sys
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from torch.optim import Adam

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.data_collection.prepare_training_data import load_all_graphs
from src.evaluation.baselines import tfidf_cosine_scores
from src.evaluation.hybrid import compute_semantic_scores
from src.evaluation.metrics import evaluate_ranking
from src.modeling.train import get_query_id, split_by_query

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)
SEED, K = 42, 5


def folds_of(graphs):
    """Danh sách K tập CV test, đúng cách chia của cross_validate."""
    qids = np.array(sorted({get_query_id(g) for g in graphs}))
    np.random.default_rng(SEED).shuffle(qids)
    return [set(x) for x in np.array_split(qids, K)]


# ---------------------------------------------------------------------------
# Baseline MLP trên embedding SBERT của CV và JD
# ---------------------------------------------------------------------------

class PairMLP(nn.Module):
    """MLP học sâu đơn giản: [u; v; |u-v|; u*v] (u, v là vector SBERT 384 chiều của CV và JD) -> logit."""

    def __init__(self, d=384, h=256, drop=0.3):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(4 * d, h), nn.ReLU(), nn.Dropout(drop), nn.Linear(h, 64), nn.ReLU(), nn.Linear(64, 1))

    def forward(self, u, v):
        return self.net(torch.cat([u, v, (u - v).abs(), u * v], dim=-1)).squeeze(-1)


def vecs(gl):
    d = gl[0].x.shape[1] // 3
    return (torch.stack([g.x[0, :d] for g in gl]).float(), torch.stack([g.x[1, :d] for g in gl]).float(),
            torch.tensor([g.y.item() for g in gl]) / config.NUM_GRADES)


def train_mlp(tr, va, epochs=100, patience=20, batch=32, lr=config.LEARNING_RATE):
    torch.manual_seed(SEED)
    m, loss_fn = PairMLP(), nn.BCEWithLogitsLoss()
    opt = Adam(m.parameters(), lr=lr, weight_decay=config.WEIGHT_DECAY)
    (ut, vt, yt), (uv, vv, yv) = vecs(tr), vecs(va)
    best, best_state, bad = 1e9, None, 0
    for _ in range(epochs):
        m.train()
        for idx in torch.randperm(len(yt)).split(batch):
            opt.zero_grad()
            loss_fn(m(ut[idx], vt[idx]), yt[idx]).backward()
            opt.step()
        m.eval()
        with torch.no_grad():
            vl = loss_fn(m(uv, vv), yv).item()
        if vl < best - 1e-5:
            best, best_state, bad = vl, {k: x.clone() for k, x in m.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= patience:
                break
    m.load_state_dict(best_state)
    return m.eval()


def mlp_oof(graphs, folds):
    out = {}
    for te in folds:
        test = [g for g in graphs if get_query_id(g) in te]
        rest = [g for g in graphs if get_query_id(g) not in te]
        tr, va = split_by_query(rest, val_ratio=0.15)
        m = train_mlp(tr, va)
        u, v, _ = vecs(test)
        with torch.no_grad():
            s = torch.sigmoid(m(u, v)).numpy()
        for g, x in zip(test, s):
            out[(g.cv_source, g.jd_source)] = float(x)
    return out


# ---------------------------------------------------------------------------
# Độ đo
# ---------------------------------------------------------------------------

def ranking_metrics(df, col):
    groups = {c: list(zip(g.grade, g[col])) for c, g in df.groupby("cv_id")}
    return evaluate_ranking(groups, ks=[1, 3, 5, 10])


def bootstrap_ci(df, col, keys, n=500, seed=0):
    rng = np.random.default_rng(seed)
    groups = {c: list(zip(g.grade, g[col])) for c, g in df.groupby("cv_id")}
    ids = list(groups)
    res = {k: [] for k in keys}
    for _ in range(n):
        pick = rng.integers(0, len(ids), len(ids))
        r = evaluate_ranking({j: groups[ids[p]] for j, p in enumerate(pick)}, ks=[1, 3, 5, 10])
        for k in keys:
            if r[k] is not None:
                res[k].append(r[k])
    return {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in res.items()}


def best_f1_threshold(s, y):
    cand = np.unique(np.quantile(s, np.linspace(0.02, 0.98, 97)))
    f = [f1_score(y, s >= t) for t in cand]
    return cand[int(np.argmax(f))]


def classification_metrics(df, col, fold):
    """Phân loại nhị phân 'phù hợp' = grade >= 2. Ngưỡng của mỗi fold chọn trên 4 fold còn lại (cross-fit) để tối đa F1."""
    y, s = (df.grade.values >= config.RELEVANT_GRADE).astype(int), df[col].values
    pred = np.zeros_like(y)
    for f in range(K):
        t = best_f1_threshold(s[fold != f], y[fold != f])
        pred[fold == f] = (s[fold == f] >= t).astype(int)
    return {"accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred), "recall": recall_score(y, pred),
            "f1": f1_score(y, pred), "auc_roc": roc_auc_score(y, s)}


def main():
    t0 = time.time()
    graphs = load_all_graphs()
    folds = folds_of(graphs)
    gdf = pd.DataFrame({"cv_id": [g.cv_source for g in graphs], "jd_id": [g.jd_source for g in graphs],
                        "grade": [int(g.y.item()) for g in graphs],
                        "tfidf": tfidf_cosine_scores(graphs), "sbert": compute_semantic_scores(graphs)})
    oof = pd.read_csv(os.path.join(config.DATA_PROCESSED_DIR, "cv_oof_predictions.csv"))
    stack = pd.read_csv(os.path.join(config.DATA_PROCESSED_DIR, "stack_oof_predictions.csv"))
    df = gdf.merge(oof[["cv_id", "jd_id", "gcn_score"]], on=["cv_id", "jd_id"]) \
            .merge(stack[["cv_id", "jd_id", "stack_score"]], on=["cv_id", "jd_id"])

    print("MLP baseline (5-fold)...", flush=True)
    mlp = mlp_oof(graphs, folds)
    df["mlp"] = [mlp[(c, j)] for c, j in zip(df.cv_id, df.jd_id)]

    fold_of_cv = {c: i for i, te in enumerate(folds) for c in te}
    df["fold"] = df.cv_id.map(fold_of_cv)
    fold = df.fold.values

    # Hybrid tuyến tính alpha*GCN + (1-alpha)*SBERT_chuẩn_hóa; alpha chọn trên 4 fold còn lại, tối đa NDCG@10
    hyb = np.zeros(len(df))
    alphas = []
    for f in range(K):
        trm, tem = fold != f, fold == f
        lo, hi = df.sbert[trm].min(), df.sbert[trm].max()
        norm = lambda x: np.clip((x - lo) / (hi - lo + 1e-9), 0, 1)
        best, ba = -1, 0.5
        for a in np.linspace(0, 1, 21):
            tmp = df[trm].assign(h=a * df.gcn_score[trm] + (1 - a) * norm(df.sbert[trm]))
            v = ranking_metrics(tmp, "h")["ndcg@10"]
            if v > best:
                best, ba = v, a
        alphas.append(float(ba))
        hyb[tem] = ba * df.gcn_score[tem] + (1 - ba) * norm(df.sbert[tem])
    df["hybrid"] = hyb

    methods = {"TF-IDF + cosine": "tfidf", "SBERT + cosine": "sbert", "MLP (SBERT)": "mlp", "GCN": "gcn_score",
               "Hybrid tuyến tính (GCN + SBERT)": "hybrid", "Mô hình đề xuất (GCN + LLM + GBM)": "stack_score"}
    rows = []
    for name, col in methods.items():
        r = ranking_metrics(df, col)
        ci = bootstrap_ci(df, col, ["ndcg@5", "ndcg@10", "mrr"])
        cm = classification_metrics(df, col, fold)
        rows.append({"method": name, **{k: r[k] for k in ["ndcg@1", "ndcg@3", "ndcg@5", "ndcg@10", "recall@5", "recall@10", "mrr"]},
                     "ndcg@5_ci": ci["ndcg@5"], "ndcg@10_ci": ci["ndcg@10"], "mrr_ci": ci["mrr"], **cm})
        print(name, {k: round(v, 3) for k, v in rows[-1].items() if isinstance(v, float)}, flush=True)
    json.dump({"rows": rows, "alphas": alphas, "n_pairs": len(df), "n_cv": int(df.cv_id.nunique())},
              open(os.path.join(OUT, "main_results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    df.to_csv(os.path.join(OUT, "oof_all_methods.csv"), index=False)
    print("xong trong %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
