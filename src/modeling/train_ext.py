"""
Thực nghiệm trên bộ ngoài cnamuangtoun/resume-job-description-fit (tiếng Anh, nhãn 3 mức) với chia train/test GỐC của bộ.
Nhãn: No Fit = 0, Potential Fit = 1, Good Fit = 2 ("phù hợp" = Good Fit, tức nhãn >= 2). Truy vấn = JD xếp hạng các CV.
Mô hình: 15% JD của train làm validation (dừng sớm + chọn cấu hình), tập test chấm một lần. Nhiều seed.
Baseline không huấn luyện: TF-IDF/BM25/SBERT (MiniLM, BGE-M3) trên văn bản các mục đã trích xuất, SBERT MiniLM trên văn bản gốc, MaxSim mức yêu cầu.

Chạy: python src/modeling/train_ext.py [--seeds 5] [--configs pair,pair_skip] [--baselines]
Ra:   report/results/ext_cna_req.csv, ext_cna_req_val.csv, ext_cna_static.csv
"""
import argparse
import hashlib
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import config
from src.extraction import requirement_extractor as R
from src.modeling.train_req import CONFIGS, maxsim_req, run, splits
from src.representation.req_graph import DEFAULT_GRAPH, Embedder, build_pair_graph

RES = os.path.join(ROOT, "report", "results")
os.makedirs(RES, exist_ok=True)  # report/ không nằm trong repo
D = os.path.join(config.DATA_RAW_DIR, "cnamuangtoun")
LAB = {"No Fit": 0, "Potential Fit": 1, "Good Fit": 2}
sid = lambda t: hashlib.md5(t.encode("utf-8")).hexdigest()[:10]


def load():
    out = {}
    for s in ("train", "test"):
        d = pd.read_csv(os.path.join(D, f"{s}.csv"))
        d["cv_id"], d["jd_id"], d["grade"] = d.resume_text.map(sid), d.job_description_text.map(sid), d.label.map(LAB)
        out[s] = d
    return out


def graphs(df, cache, emb):
    gs = []
    for r in df.itertuples():
        c, j = cache.get(R._key(r.resume_text, "CV")), cache.get(R._key(r.job_description_text, "JD"))
        if c and j and c["items"] and j["items"]:
            g = build_pair_graph(c, j, emb, r.grade)
            g.cv_id, g.jd_id, g.grade = r.cv_id, r.jd_id, int(r.grade)
            gs.append(g)
    return gs


def static_scores(data, cache):
    """Baseline không huấn luyện cho mọi cặp train+test."""
    from rank_bm25 import BM25Okapi
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    df = pd.concat([data["train"], data["test"]]).drop_duplicates(["cv_id", "jd_id"])[["cv_id", "jd_id", "grade", "resume_text", "job_description_text"]]
    items = lambda t, k: " ".join(x["text"] for x in cache[R._key(t, k)]["items"]) if R._key(t, k) in cache else ""
    cvt = {sid(t): items(t, "CV") for t in df.resume_text.unique()}
    jdt = {sid(t): items(t, "JD") for t in df.job_description_text.unique()}
    cvr = {sid(t): t for t in df.resume_text.unique()}
    jdr = {sid(t): t for t in df.job_description_text.unique()}
    tok = lambda s: re.findall(r"\w+", s.lower())
    vec = TfidfVectorizer().fit(list(cvt.values()) + list(jdt.values()))
    X = {("c", k): vec.transform([t]) for k, t in cvt.items()} | {("j", k): vec.transform([t]) for k, t in jdt.items()}
    df["tfidf"] = [float(X[("c", c)].multiply(X[("j", j)]).sum()) for c, j in zip(df.cv_id, df.jd_id)]
    bm = BM25Okapi([tok(t) for t in cvt.values()])
    ci = {k: i for i, k in enumerate(cvt)}
    jb = {j: bm.get_scores(tok(t)) for j, t in jdt.items()}
    df["bm25"] = [float(jb[j][ci[c]]) for c, j in zip(df.cv_id, df.jd_id)]
    for name, mid, a, b, ml in (("MiniLM_items", "paraphrase-multilingual-MiniLM-L12-v2", cvt, jdt, 512), ("BGE-M3_items", "BAAI/bge-m3", cvt, jdt, 512),
                                ("MiniLM_raw", "paraphrase-multilingual-MiniLM-L12-v2", cvr, jdr, 512)):
        m = SentenceTransformer(mid)
        m.max_seq_length = min(ml, m.max_seq_length or ml)
        enc = lambda dct: dict(zip(dct, m.encode(list(dct.values()), normalize_embeddings=True, batch_size=16, show_progress_bar=False)))
        ce, je = enc(a), enc(b)
        df[f"sbert|{name}"] = [float(ce[c] @ je[j]) for c, j in zip(df.cv_id, df.jd_id)]
        print("xong", name, flush=True)
    return df.drop(columns=["resume_text", "job_description_text"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--configs", default="pair,pair_skip")
    ap.add_argument("--baselines", action="store_true", help="chỉ tính baseline không huấn luyện")
    ap.add_argument("--protocol", choices=["official", "jd"], default="official",
                    help="official: train/test gốc; jd: gộp train+test, 5 fold chia theo nhóm JD (nhiều truy vấn kiểm tra hơn)")
    ap.add_argument("--tag", default="")
    ap.add_argument("--seed0", type=int, default=0, help="seed đầu tiên (để chạy thêm seed mà không lặp lại)")
    a = ap.parse_args()
    data, cache = load(), R._load()
    if a.baselines:
        static_scores(data, cache).to_csv(os.path.join(RES, "ext_cna_static.csv"), index=False)
        sys.exit()
    emb = Embedder()
    texts = sorted({x["text"] for v in cache.values() for x in v["items"]} - set(emb.vec))
    print("mục cần mã hóa:", len(texts), flush=True)
    if texts:
        emb.encode(texts)                                     # mã hóa một lần, tránh ghi cache lặp lại cho từng cặp
    tr, te = graphs(data["train"], cache, emb), graphs(data["test"], cache, emb)
    print(f"train {len(tr)} cặp, test {len(te)} cặp", flush=True)
    # biến thể đồ thị (top-m/embedding/ESCO) ghi MaxSim riêng theo tag, không ghi đè baseline MaxSim chính
    pd.DataFrame([(g.cv_id, g.jd_id, maxsim_req(g)) for g in tr + te], columns=["cv_id", "jd_id", "maxsim_req"]).drop_duplicates(["cv_id", "jd_id"]).to_csv(
        os.path.join(RES, "ext_cna_maxsim.csv" if DEFAULT_GRAPH else f"ext_cna_maxsim{a.tag}.csv"), index=False)
    dims = {k: tr[0][k].x.size(1) for k in ("req", "item", "spec")}
    if a.protocol == "official":
        folds = [(0, tr, te)]
    else:
        seen, allg = set(), []
        for g in tr + te:                                     # cặp trùng giữa train và test gốc chỉ giữ một
            if (g.cv_id, g.jd_id) not in seen:
                seen.add((g.cv_id, g.jd_id))
                allg.append(g)
        folds = splits(allg, "jd")[0]
    rows, vrows = [], []
    for name in a.configs.split(","):
        for seed in range(a.seed0, a.seed0 + a.seeds):
            for f, pool, test in folds:
                js = sorted({g.jd_id for g in pool})
                vj = set(np.random.default_rng(seed).choice(js, size=int(0.15 * len(js)), replace=False))
                out, vn = run([g for g in pool if g.jd_id not in vj], [g for g in pool if g.jd_id in vj], test, name, seed, dims)
                vrows.append((name, seed, f, vn))
                rows += [(c, j, j, name, seed, s) for c, j, s in out]
            print("xong", name, "seed", seed, flush=True)
            pd.DataFrame(rows, columns=["cv_id", "jd_id", "qid", "config", "seed", "score"]).to_csv(os.path.join(RES, f"ext_cna_req{a.tag}.csv"), index=False)
            pd.DataFrame(vrows, columns=["config", "seed", "fold", "val_ndcg10"]).to_csv(os.path.join(RES, f"ext_cna_req{a.tag}_val.csv"), index=False)
    print("đã lưu")
