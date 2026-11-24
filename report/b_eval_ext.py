"""
Đánh giá trên bộ cnamuangtoun/resume-job-description-fit (test gốc, truy vấn = JD, nhãn 0/1/2, phù hợp = Good Fit).
Cấu hình chính chọn chỉ bằng NDCG@10 trên VALIDATION. Kiểm định: paired bootstrap trên truy vấn + Holm.
Chạy: python report/b_eval_ext.py [--main pair,pair_skip]
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
from src.evaluation.metrics import evaluate_ranking

ap = argparse.ArgumentParser()
ap.add_argument("--main", default="pair,pair_skip")
ap.add_argument("--tag", default="")
a = ap.parse_args()
L = pd.read_csv(os.path.join(RES, f"ext_cna_req{a.tag}.csv"))
V = pd.read_csv(os.path.join(RES, f"ext_cna_req{a.tag}_val.csv"))
S = pd.read_csv(os.path.join(RES, "ext_cna_static.csv"))
M = pd.read_csv(os.path.join(RES, "ext_cna_maxsim.csv"))
base = L[["cv_id", "jd_id"]].drop_duplicates().merge(S, on=["cv_id", "jd_id"]).merge(M, on=["cv_id", "jd_id"])
base["qid"] = base.jd_id
BASE = {"maxsim_req": "MaxSim (mức yêu cầu)", "sbert|MiniLM_items": "SBERT MiniLM (mục trích xuất)", "sbert|BGE-M3_items": "SBERT BGE-M3 (mục trích xuất)",
        "sbert|MiniLM_raw": "SBERT MiniLM (văn bản gốc)", "ce|bge-reranker-v2-m3": "Cross-encoder bge-reranker-v2-m3", "llm|gemini-3.5-flash-lite": "LLM chấm điểm (Gemini 3.5 Flash-Lite, nhiệt độ 0)", "bm25": "BM25", "tfidf": "TF-IDF"}
SEEDED = {}                                # baseline có huấn luyện (nhiều seed): cột = điểm trung bình các seed, bảng in ± độ lệch chuẩn
for k, (f, nme) in {"confit": ("confit_ext.csv", "ConFit (bi-encoder MNRL)"), "bilstm": ("bilstm_ext.csv", "BiLSTM (siamese, PJFNN rút gọn)")}.items():
    f = os.path.join(RES, f)
    if os.path.exists(f):
        x = pd.read_csv(f)
        n = x.groupby("seed").size()
        x = x[x.seed.isin(n[n == n.max()].index)]          # bỏ seed chạy dở (chưa đủ mọi fold)
        print(nme, ": dùng seed", sorted(x.seed.unique()))
        base = base.merge(x.groupby(["cv_id", "jd_id"]).score.mean().rename(k).reset_index(), on=["cv_id", "jd_id"])
        BASE[k], SEEDED[k] = nme, x
BASE = {k: v for k, v in BASE.items() if k in base.columns}

vs = V.groupby("config").val_ndcg10.agg(["mean", "std"])
main = max(a.main.split(","), key=lambda c: vs.loc[c, "mean"])
print("NDCG@10 validation:\n", vs.round(4).to_string(), "\n=> cấu hình chính (chọn trên validation):", main)
ELIG = [q for q, x in base.groupby("qid") if len(x) >= 2 and (x.grade >= 2).any()]
print(f"{len(ELIG)} truy vấn đủ điều kiện / {base.qid.nunique()} JD; {len(base)} cặp test")
QW = np.cumsum(np.bincount(base.grade, minlength=3) / len(base))[:2]


def groups(df, col):
    return {q: list(zip(x.grade, x[col])) for q, x in df[df.qid.isin(ELIG)].groupby("qid")}


def allm(df, col):
    gr = groups(df, col)
    r = evaluate_ranking(gr, ks=[5, 10])
    ap_, rho, yt, yp = [], [], [], []
    for q, x in gr.items():
        y, s = np.array([t[0] for t in x]), np.array([t[1] for t in x])
        rel = (y[np.argsort(-s)] >= 2)
        if rel.any():
            ap_.append(float((np.cumsum(rel) / (np.arange(len(rel)) + 1))[rel].mean()))
        if len(set(y)) > 1 and len(set(s)) > 1:
            rho.append(spearmanr(s, y).correlation)
        yt += list(y)
        yp += list(np.searchsorted(QW, (np.argsort(np.argsort(s)) + 0.5) / len(s)))
    return {"ndcg@5": r["ndcg@5"], "ndcg@10": r["ndcg@10"], "map": float(np.mean(ap_)), "mrr": r["mrr"], "recall@5": r["recall@5"],
            "spearman": float(np.mean(rho)), "qwk": float(cohen_kappa_score(yt, yp, weights="quadratic"))}


K = ["ndcg@5", "ndcg@10", "map", "mrr", "recall@5", "spearman", "qwk"]
rows, out = [], {"main": main, "val": vs.round(4).to_dict(), "n_queries": len(ELIG), "methods": {}}
for cfg in sorted(set(L.config)):
    mm = pd.DataFrame([allm(base.merge(x[["cv_id", "jd_id", "score"]], on=["cv_id", "jd_id"]), "score") for _, x in L[L.config == cfg].groupby("seed")])
    rows.append((f"req-GNN [{cfg}]" + (" *" if cfg == main else ""), mm.mean().to_dict(), mm.std().to_dict()))
for k, nme in BASE.items():
    if k in SEEDED:
        mm = pd.DataFrame([allm(base.drop(columns=k).merge(x[["cv_id", "jd_id", "score"]], on=["cv_id", "jd_id"]), "score") for _, x in SEEDED[k].groupby("seed")])
        rows.append((nme, mm.mean().to_dict(), mm.std().to_dict() if len(mm) > 1 else None))
    else:
        rows.append((nme, allm(base, k), None))
print(f"\n{'Phương pháp':<34}" + "".join(f"{m:>16}" for m in K))
for nme, m, sd in rows:
    print(f"{nme:<34}" + "".join(f"{m[k]:>9.3f}" + (f"±{sd[k]:.3f}" if sd else "      ") for k in K))
    out["methods"][nme] = {"mean": m, "std": sd}

avg = L[L.config == main].groupby(["cv_id", "jd_id"]).score.mean().rename("req_main").reset_index()
dfm = base.merge(avg, on=["cv_id", "jd_id"])
gm = groups(dfm, "req_main")
res = [[nme, *paired_boot(gm, groups(dfm, k))] for k, nme in BASE.items()]
m_ = holm(res)
print(f"\nNDCG@10: req-GNN [{main}] − baseline  (paired bootstrap trên truy vấn; MaxSim = giả thuyết chính, p không hiệu chỉnh; Holm trên {m_} baseline phụ)")
for nme, d, ci, p, ph in res:
    print(f"{nme:<34} diff={d:+.3f}  CI95=[{ci[0]:+.3f},{ci[1]:+.3f}]  p={p:.3f}  p_Holm={ph:.3f}")
out["tests"] = [{"vs": r[0], "diff": r[1], "ci": r[2], "p": r[3], "p_holm": r[4]} for r in res]
json.dump(out, open(os.path.join(RES, f"b_eval_ext{a.tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
