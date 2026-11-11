"""
Đánh giá mô hình mức yêu cầu theo giao thức của cô, từ các file do src/modeling/train_req.py tạo ra.
  python report/b_eval2.py <jd|double> [--main pair,pair_skip] [--tag ""]

 - Cấu hình chính được CHỌN chỉ bằng NDCG@10 trung bình trên VALIDATION (req_<p>_val.csv); tập kiểm tra không tham gia chọn.
 - Mỗi phương pháp: trung bình ± độ lệch chuẩn qua các seed (baseline không huấn luyện chỉ có một giá trị).
 - Độ đo: NDCG@5/10, MAP (phù hợp = nhãn >= 2), MRR, Recall@5, Spearman theo từng truy vấn (trung bình), QWK
   (điểm -> mức 0-3 bằng phân vị TRONG TỪNG TRUY VẤN theo tỉ lệ nhãn của toàn bộ dữ liệu, vì điểm xếp hạng không so được giữa các truy vấn).
 - Kiểm định: paired bootstrap trên truy vấn (NDCG@10, điểm trung bình các seed của mô hình) so với từng baseline, hiệu chỉnh Holm.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a_baselines import RES, holm, paired_boot
from src.evaluation.metrics import evaluate_ranking, ndcg_at_k

ap = argparse.ArgumentParser()
ap.add_argument("protocol", choices=["jd", "double"])
ap.add_argument("--main", default="pair,pair_skip")
ap.add_argument("--tag", default="")
ap.add_argument("--confit", default="", help="hậu tố file confit_<protocol><hậu tố>.csv (nếu có)")
a = ap.parse_args()
P = a.protocol

L = pd.read_csv(os.path.join(RES, f"req_{P}{a.tag}.csv"))
V = pd.read_csv(os.path.join(RES, f"req_{P}{a.tag}_val.csv"))
# chỉ giữ cặp có điểm ở MỌI cấu hình/seed (các lượt chạy khác nhau có thể bỏ vài cặp do văn bản rỗng) để so sánh cùng truy vấn
full = L.groupby(["cv_id", "jd_id"]).size()
full = full[full == full.max()].reset_index()[["cv_id", "jd_id"]]
L = L.merge(full, on=["cv_id", "jd_id"])
meta = L[["cv_id", "jd_id", "qid"]].drop_duplicates()
lab = pd.read_csv(os.path.join(RES, "static_scores.csv"))
base = meta.merge(lab, on=["cv_id", "jd_id"]).merge(pd.read_csv(os.path.join(RES, "maxsim_req.csv")), on=["cv_id", "jd_id"])
old = pd.read_csv(os.path.join(RES, "oof_jd_split.csv" if P == "jd" else "oof_double_split.csv"))
if P == "jd":
    base = base.merge(old[["cv_id", "jd_id", "GCN", "Hybrid_(α_theo_JD)", "mlp"]].rename(columns={"GCN": "gcn_old", "Hybrid_(α_theo_JD)": "hybrid_old", "mlp": "mlp_old"}), on=["cv_id", "jd_id"])
else:
    base = base.merge(old[["cv_id", "jd_id", "gcn"]].rename(columns={"gcn": "gcn_old"}), on=["cv_id", "jd_id"])
BASE = {"maxsim_req": "MaxSim (mức yêu cầu)", "maxsim_hard|BGE-M3": "MaxSim hard_skills BGE-M3", "sbert|MiniLM (hiện tại)": "SBERT MiniLM",
        "sbert|BGE-M3": "SBERT BGE-M3", "sbert|mE5-base": "SBERT mE5-base", "sbert|Vietnamese-SBERT": "SBERT Vietnamese",
        "ce|bge-reranker-v2-m3": "Cross-encoder bge-reranker-v2-m3", "llm|gemini-3.5-flash-lite": "LLM chấm điểm (Gemini 3.5 Flash-Lite, nhiệt độ 0)", "bm25": "BM25", "tfidf": "TF-IDF", "gcn_old": "GCN 14 nút (cũ)", "hybrid_old": "Hybrid cũ", "mlp_old": "MLP"}
CF = os.path.join(RES, f"confit_{P}{a.confit}.csv")
if os.path.exists(CF):                      # baseline có huấn luyện (nhiều seed): cột = điểm trung bình các seed, bảng in ± độ lệch chuẩn
    CF = pd.read_csv(CF)
    n = CF.groupby("seed").size()
    CF = CF[CF.seed.isin(n[n == n.max()].index)]          # bỏ seed chạy dở (chưa đủ mọi fold)
    print("ConFit: dùng seed", sorted(CF.seed.unique()))
    base = base.merge(CF.groupby(["cv_id", "jd_id"]).score.mean().rename("confit").reset_index(), on=["cv_id", "jd_id"])
    BASE["confit"] = "ConFit (bi-encoder MNRL)"
BASE = {k: v for k, v in BASE.items() if k in base.columns}

# --- chọn cấu hình chính trên validation ---
vs = V.groupby("config").val_ndcg10.agg(["mean", "std"])
main = max(a.main.split(","), key=lambda c: vs.loc[c, "mean"])
print("NDCG@10 validation theo cấu hình:\n", vs.round(4).to_string(), "\n=> cấu hình chính (chọn trên validation):", main)

# --- truy vấn đủ điều kiện ---
g = base.groupby("qid")
ELIG = [q for q, x in g if len(x) >= 2 and (x.grade >= 2).any()]
print(f"{len(ELIG)} truy vấn đủ điều kiện, giao thức {P}")
QW = np.cumsum(np.bincount(base.grade, minlength=4) / len(base))[:3]


def groups(df, col):
    return {q: list(zip(x.grade, x[col])) for q, x in df[df.qid.isin(ELIG)].groupby("qid")}


def allm(df, col):
    gr = groups(df, col)
    r = evaluate_ranking(gr, ks=[5, 10])
    ap_, rho, yt, yp = [], [], [], []
    for q, x in gr.items():
        y, s = np.array([t[0] for t in x]), np.array([t[1] for t in x])
        o = np.argsort(-s)
        rel = (y[o] >= 2)
        if rel.any():
            ap_.append(float((np.cumsum(rel) / (np.arange(len(rel)) + 1))[rel].mean()))
        if len(set(y)) > 1 and len(set(s)) > 1:
            rho.append(spearmanr(s, y).correlation)
        pct = (np.argsort(np.argsort(s)) + 0.5) / len(s)           # phân vị trong truy vấn
        yt += list(y)
        yp += list(np.searchsorted(QW, pct))
    return {"ndcg@5": r["ndcg@5"], "ndcg@10": r["ndcg@10"], "map": float(np.mean(ap_)), "mrr": r["mrr"], "recall@5": r["recall@5"],
            "spearman": float(np.mean(rho)), "qwk": float(cohen_kappa_score(yt, yp, weights="quadratic"))}


rows, out = [], {"protocol": P, "main": main, "val": vs.round(4).to_dict(), "n_queries": len(ELIG), "methods": {}}
# mô hình (nhiều seed)
for cfg in sorted(set(L.config)):
    ms = []
    for sd, x in L[L.config == cfg].groupby("seed"):
        ms.append(allm(base.merge(x[["cv_id", "jd_id", "score"]], on=["cv_id", "jd_id"]), "score"))
    mm = pd.DataFrame(ms)
    rows.append((f"req-GNN [{cfg}]" + (" *" if cfg == main else ""), mm.mean().to_dict(), mm.std().to_dict()))
for k, nme in BASE.items():
    if k == "confit":
        mm = pd.DataFrame([allm(base.drop(columns="confit").merge(x[["cv_id", "jd_id", "score"]], on=["cv_id", "jd_id"]), "score") for _, x in CF.groupby("seed")])
        rows.append((nme, mm.mean().to_dict(), mm.std().to_dict() if len(mm) > 1 else None))
    else:
        rows.append((nme, allm(base, k), None))
print(f"\n{'Phương pháp':<34}" + "".join(f"{m:>16}" for m in ["ndcg@5", "ndcg@10", "map", "mrr", "recall@5", "spearman", "qwk"]))
for nme, m, sd in rows:
    print(f"{nme:<34}" + "".join(f"{m[k]:>9.3f}" + (f"±{sd[k]:.3f}" if sd else "      ") for k in ["ndcg@5", "ndcg@10", "map", "mrr", "recall@5", "spearman", "qwk"]))
    out["methods"][nme] = {"mean": m, "std": sd}

# --- kiểm định: cấu hình chính (điểm trung bình các seed) vs từng baseline, Holm ---
avg = L[L.config == main].groupby(["cv_id", "jd_id"]).score.mean().rename("req_main").reset_index()
dfm = base.merge(avg, on=["cv_id", "jd_id"])
gm = groups(dfm, "req_main")
res = []
for k, nme in BASE.items():
    d, ci, p = paired_boot(gm, groups(dfm, k))
    res.append([nme, d, ci, p])
m_ = holm(res)
print(f"\nNDCG@10: req-GNN [{main}] − baseline  (paired bootstrap trên truy vấn; MaxSim = giả thuyết chính, p không hiệu chỉnh; Holm trên {m_} baseline phụ)")
for nme, d, ci, p, ph in res:
    print(f"{nme:<34} Δ={d:+.3f}  CI95=[{ci[0]:+.3f},{ci[1]:+.3f}]  p={p:.3f}  p_Holm={ph:.3f}")
out["tests"] = [{"vs": r[0], "diff": r[1], "ci": r[2], "p": r[3], "p_holm": r[4]} for r in res]
json.dump(out, open(os.path.join(RES, f"b_eval2_{P}{a.tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
