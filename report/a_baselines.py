"""
Bước A1 + A2 theo nhận xét của cô: baseline không huấn luyện (TF-IDF, BM25, SBERT nhiều phiên bản, MaxSim)
chấm trên 1664 cặp, rồi so với GCN/Hybrid trên cùng truy vấn (mỗi JD xếp hạng các CV).

Văn bản mỗi bên = các thực thể Gemini đã trích xuất (giống baseline TF-IDF/SBERT hiện có), tối đa 512 token.
MaxSim: với mỗi mục yêu cầu của JD lấy max cosine tới các mục CV CÙNG LOẠI, trung bình theo mục; gộp các loại bằng
trọng số config.ENTITY_WEIGHTS; preferred_skills (ưu tiên) tính vào hard_skills với trọng số 0,5.

Chạy:  python report/a_baselines.py score   -> report/results/static_scores.csv (điểm từng cặp)
       python report/a_baselines.py eval    -> report/results/a_baselines.json
"""

import json
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import config
from src.evaluation.metrics import evaluate_ranking

RES = os.path.join(ROOT, "report", "results")
SCORES = os.path.join(RES, "static_scores.csv")
MODELS = {"MiniLM (hiện tại)": ("paraphrase-multilingual-MiniLM-L12-v2", "", ""),
          "BGE-M3": ("BAAI/bge-m3", "", ""),
          "mE5-base": ("intfloat/multilingual-e5-base", "query: ", "query: "),
          "Vietnamese-SBERT": ("keepitreal/vietnamese-sbert", "", "")}
PREF_W = 0.5


def load_entities():
    from src.data_collection.prepare_training_data import load_all_graphs
    cv, jd, pairs = {}, {}, []
    for g in load_all_graphs():
        cv[g.cv_source] = json.loads(g.cv_entities)
        jd[g.jd_source] = json.loads(g.jd_entities)
        pairs.append((g.cv_source, g.jd_source, int(g.y.item())))
    return cv, jd, pairs


def doc_text(e):
    return " ".join(str(i) for t in config.ENTITY_TYPES for i in e.get(t, []))


def tok(s):
    return re.findall(r"\w+", s.lower())


def maxsim(cv_e, jd_e, emb, variant):
    """emb: dict chuỗi -> vector đã chuẩn hóa. variant 'hard' chỉ hard_skills(+ưu tiên); 'all' mọi loại theo λ_t."""
    types = ["hard_skills"] if variant == "hard" else config.ENTITY_TYPES
    num = den = 0.0
    for t in types:
        items = [(x, 1.0) for x in jd_e.get(t, [])]
        if t == "hard_skills":
            items += [(x, PREF_W) for x in jd_e.get("preferred_skills", [])]
        if not items:
            continue
        cvi = cv_e.get(t, [])
        if cvi:
            c = np.stack([emb[x] for x in cvi])
            m = [(float((c @ emb[x]).max()), w) for x, w in items]
        else:
            m = [(0.0, w) for _, w in items]
        s = sum(a * w for a, w in m) / sum(w for _, w in m)
        lam = 1.0 if variant == "hard" else config.ENTITY_WEIGHTS[t]
        num += lam * s
        den += lam
    return num / den if den else 0.0


def score():
    from rank_bm25 import BM25Okapi
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    cv, jd, pairs = load_entities()
    df = pd.DataFrame(pairs, columns=["cv_id", "jd_id", "grade"])
    cvt, jdt = {k: doc_text(v) for k, v in cv.items()}, {k: doc_text(v) for k, v in jd.items()}

    vec = TfidfVectorizer().fit(list(cvt.values()) + list(jdt.values()))
    X = {**{("c", k): vec.transform([t]) for k, t in cvt.items()}, **{("j", k): vec.transform([t]) for k, t in jdt.items()}}
    df["tfidf"] = [float((X[("c", c)].multiply(X[("j", j)])).sum()) for c, j in zip(df.cv_id, df.jd_id)]
    bm = BM25Okapi([tok(t) for t in cvt.values()])
    cv_idx = {k: i for i, k in enumerate(cvt)}
    jbm = {j: bm.get_scores(tok(t)) for j, t in jdt.items()}
    df["bm25"] = [float(jbm[j][cv_idx[c]]) for c, j in zip(df.cv_id, df.jd_id)]

    for name, (mid, qp, dp) in MODELS.items():
        try:
            m = SentenceTransformer(mid)
        except Exception as e:  # tải mô hình lỗi: bỏ qua, ghi rõ
            print("BỎ QUA", name, e, flush=True)
            continue
        m.max_seq_length = min(512, m.max_seq_length or 512)
        enc = lambda L, p="": m.encode([p + x for x in L], normalize_embeddings=True, batch_size=16, show_progress_bar=False)
        ck, jk = list(cvt), list(jdt)
        ce, je = dict(zip(ck, enc([cvt[k] for k in ck], dp))), dict(zip(jk, enc([jdt[k] for k in jk], qp)))
        df[f"sbert|{name}"] = [float(ce[c] @ je[j]) for c, j in zip(df.cv_id, df.jd_id)]
        items = sorted({x for e in list(cv.values()) + list(jd.values()) for t in config.ENTITY_TYPES + ["preferred_skills"] for x in e.get(t, [])})
        emb = dict(zip(items, enc(items, qp)))
        for v in ("hard", "all"):
            df[f"maxsim_{v}|{name}"] = [maxsim(cv[c], jd[j], emb, v) for c, j in zip(df.cv_id, df.jd_id)]
        print("xong", name, flush=True)
        df.to_csv(SCORES, index=False)
    df.to_csv(SCORES, index=False)


KS = [1, 3, 5, 10]


def eligible(d, by):
    size, rel = d.groupby(by).size(), d.groupby(by).grade.apply(lambda x: (x >= 2).any())
    return [q for q in size.index if size[q] >= 2 and rel[q]]


def metrics(d, col, by):
    g = {q: list(zip(x.grade, x[col])) for q, x in d.groupby(by)}
    r = evaluate_ranking(g, ks=KS)
    return {k: r[k] for k in ("ndcg@5", "ndcg@10", "mrr", "recall@5")}, g


def paired_boot(ga, gb, n=2000, seed=0):
    """Hiệu NDCG@10 (a − b) theo từng truy vấn, bootstrap ghép cặp trên truy vấn: trả (hiệu, CI95, p hai phía)."""
    from src.evaluation.metrics import ndcg_at_k
    qs = list(ga)
    nd = lambda g: ndcg_at_k([r for r, _ in g], [x for _, x in g], 10)
    da = np.array([nd(ga[q]) - nd(gb[q]) for q in qs])
    rng = np.random.default_rng(seed)
    bs = np.array([da[rng.integers(0, len(da), len(da))].mean() for _ in range(n)])
    p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
    return float(da.mean()), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], float(min(p, 1.0))


PRIMARY = "MaxSim (mức yêu cầu)"   # giả thuyết chính do giảng viên đặt trước: kiểm định riêng, không đưa vào họ Holm


def holm(res):
    """res: list [tên, hiệu, CI, p]; nối thêm p hiệu chỉnh. Holm chỉ trên các baseline phụ; giả thuyết chính giữ nguyên p."""
    sec = sorted((r for r in res if r[0] != PRIMARY), key=lambda r: r[3])
    mx = 0.0
    for k, r in enumerate(sec):
        mx = max(mx, min(1.0, (len(sec) - k) * r[3]))
        r.append(mx)
    for r in res:
        if r[0] == PRIMARY:
            r.append(r[3])
    return len(sec)


def evaluate():
    s = pd.read_csv(SCORES)
    a = pd.read_csv(os.path.join(RES, "oof_all_methods.csv"))[["cv_id", "jd_id", "gcn_score", "hybrid_a03", "mlp"]]
    d = s.merge(a, on=["cv_id", "jd_id"])
    methods = [c for c in d.columns if c not in ("cv_id", "jd_id", "grade")]
    out = {}
    for by, label in (("jd_id", "mỗi JD xếp hạng các CV"), ("cv_id", "mỗi CV xếp hạng các JD")):
        keep = eligible(d, by)
        dd = d[d[by].isin(keep)]
        rows, groups = [], {}
        for m in methods:
            r, g = metrics(dd, m, by)
            rows.append({"method": m, **r})
            groups[m] = g
        ref = "hybrid_a03"
        for row in rows:
            row["diff_vs_hybrid"] = paired_boot(groups[row["method"]], groups[ref]) if row["method"] != ref else None
        out[by] = {"label": label, "n_queries": len(keep), "n_pairs": len(dd), "rows": rows}
        print(f"\n=== {label}: {len(keep)} truy vấn ===")
        for row in sorted(rows, key=lambda r: -r["ndcg@10"]):
            df_ = row["diff_vs_hybrid"]
            print(f"{row['method']:<34} NDCG@5 {row['ndcg@5']:.3f}  NDCG@10 {row['ndcg@10']:.3f}  MRR {row['mrr']:.3f}  Δ vs Hybrid {'' if df_ is None else '%+.3f [%+.3f,%+.3f] p=%.3f' % (df_[0], *df_[1], df_[2])}")
    json.dump(out, open(os.path.join(RES, "a_baselines.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    {"score": score, "eval": evaluate}[sys.argv[1]]()
