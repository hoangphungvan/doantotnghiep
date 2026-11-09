"""
Kiểm tra NGOÀI trên bộ Vanetik–Kogan (Information 14(8):468, 2023): 30 CV, mỗi CV được 2 người xếp hạng 5 vacancy (hạng 1 = phù hợp nhất).
Chiều truy vấn: MỖI CV XẾP HẠNG 5 VACANCY. Bộ chỉ dùng để kiểm tra (không huấn luyện trên nó).

Mô hình mức yêu cầu huấn luyện trên cnamuangtoun/resume-job-description-fit (train + test), loss xếp hạng NHÓM THEO CV
(cùng chiều với bộ kiểm tra); 15% CV làm validation (dừng sớm + chọn cấu hình). Nhiều seed.
Nhãn Vanetik–Kogan: phần tử thứ i của mảng = hạng của vacancy thứ i (thứ tự dòng trong 5_vacancies.csv); trung bình hạng của 2 người
làm ground truth, đúng như bài gốc (lấy trung bình mảng hạng).

Chạy: python src/modeling/train_vk.py [--seeds 5] [--configs pair,pair_skip]
Ra:   report/results/vk_scores.csv (điểm mọi phương pháp cho 150 cặp), vk_val.csv, vk_ranks.csv (hạng của 2 người)
"""
import argparse
import ast
import os
import re
import sys

import docx
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import config
from src.extraction import requirement_extractor as R
from src.modeling.train_ext import load as load_cna, graphs as cna_graphs
from src.modeling.train_req import maxsim_req, run
from src.representation.req_graph import Embedder, build_pair_graph

RES = os.path.join(ROOT, "report", "results")
os.makedirs(RES, exist_ok=True)  # report/ không nằm trong repo
VK = os.path.join(config.DATA_RAW_DIR, "vacancy-resume-matching-dataset-main", "vacancy-resume-matching-dataset-main")
N_CV = 30


def docx_text(path):
    """Mọi đoạn văn trong file, kể cả nằm trong bảng/text box (CV 11, 12 đặt nội dung trong bảng)."""
    from docx.oxml.ns import qn
    ps = ("".join(t.text or "" for t in p.iter(qn("w:t"))) for p in docx.Document(path).element.body.iter(qn("w:p")))
    return "\n".join(x for x in ps if x.strip())


def load_vk():
    cv = {f"vk{i}": docx_text(os.path.join(VK, "CV", f"{i}.docx")) for i in range(1, N_CV + 1)}
    vac = pd.read_csv(os.path.join(VK, "5_vacancies.csv"))
    jd = {f"vac{k + 1}": f"{r.job_title}\n{r.job_description}" for k, r in enumerate(vac.itertuples())}
    txt = open(os.path.join(VK, "annotations-for-the-first-30-vacancies.txt"), encoding="utf-8").read()
    ranks = []
    for name in ("ANNOTATOR_1_RANKINGS", "ANNOTATOR_2_RANKINGS"):
        body = re.search(name + r"\s*=\s*(\[.*?\]\])", txt, re.S).group(1)
        arr = ast.literal_eval(re.sub(r"#[^\n]*", "", body))
        assert len(arr) == N_CV and all(len(x) == 5 for x in arr), name
        ranks.append(arr)
    rk = pd.DataFrame([(f"vk{c + 1}", f"vac{v + 1}", ranks[0][c][v], ranks[1][c][v]) for c in range(N_CV) for v in range(5)],
                      columns=["cv_id", "jd_id", "rank_a1", "rank_a2"])
    rk["rank_avg"] = (rk.rank_a1 + rk.rank_a2) / 2
    return cv, jd, rk


def static_scores(cv, jd, cvx, jdx, pairs):
    from rank_bm25 import BM25Okapi
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    df = pairs[["cv_id", "jd_id"]].copy()
    it = lambda e: " ".join(x["text"] for x in e["items"])
    ci, ji = {k: it(v) for k, v in cvx.items()}, {k: it(v) for k, v in jdx.items()}
    tok = lambda s: re.findall(r"\w+", s.lower())
    vec = TfidfVectorizer().fit(list(ci.values()) + list(ji.values()))
    df["tfidf"] = [float(vec.transform([ci[c]]).multiply(vec.transform([ji[j]])).sum()) for c, j in zip(df.cv_id, df.jd_id)]
    jk = list(ji)
    bm = BM25Okapi([tok(ji[k]) for k in jk])                 # truy vấn = CV, tài liệu = vacancy (đúng chiều xếp hạng)
    cb = {c: dict(zip(jk, bm.get_scores(tok(t)))) for c, t in ci.items()}
    df["bm25"] = [float(cb[c][j]) for c, j in zip(df.cv_id, df.jd_id)]
    for name, mid, a, b in (("MiniLM_items", "paraphrase-multilingual-MiniLM-L12-v2", ci, ji), ("BGE-M3_items", "BAAI/bge-m3", ci, ji),
                            ("MiniLM_raw", "paraphrase-multilingual-MiniLM-L12-v2", cv, jd), ("BGE-M3_raw", "BAAI/bge-m3", cv, jd)):
        m = SentenceTransformer(mid)
        m.max_seq_length = min(512, m.max_seq_length or 512)
        enc = lambda dct: dict(zip(dct, m.encode(list(dct.values()), normalize_embeddings=True, batch_size=8, show_progress_bar=False)))
        ce, je = enc(a), enc(b)
        df[f"sbert|{name}"] = [float(ce[c] @ je[j]) for c, j in zip(df.cv_id, df.jd_id)]
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--configs", default="pair,pair_skip")
    a = ap.parse_args()
    cv, jd, rk = load_vk()
    rk.to_csv(os.path.join(RES, "vk_ranks.csv"), index=False)
    cvx = {k: R.extract_requirements(t, "CV") for k, t in cv.items()}
    jdx = {k: R.extract_requirements(t, "JD") for k, t in jd.items()}
    R.save_cache()
    miss = [k for k, v in {**cvx, **jdx}.items() if not v["items"]]
    assert not miss, f"trích xuất rỗng (chạy lại để thử tiếp): {miss}"
    emb = Embedder()
    emb.encode(sorted({x["text"] for v in {**cvx, **jdx}.values() for x in v["items"]}))  # mã hóa một lần
    vk = []
    for r in rk.itertuples():
        g = build_pair_graph(cvx[r.cv_id], jdx[r.jd_id], emb)
        g.cv_id, g.jd_id, g.grade = r.cv_id, r.jd_id, 0
        vk.append(g)
    df = static_scores(cv, jd, cvx, jdx, rk)
    df["maxsim_req"] = [maxsim_req(g) for g in vk]
    print("xong baseline", flush=True)

    data, cache = load_cna(), R._load()
    tr = cna_graphs(pd.concat([data["train"], data["test"]]), cache, emb)
    dims = {k: tr[0][k].x.size(1) for k in ("req", "item", "spec")}
    cvs = sorted({g.cv_id for g in tr})
    vrows = []
    for name in a.configs.split(","):
        sc = []
        for seed in range(a.seeds):
            vc = set(np.random.default_rng(seed).choice(cvs, size=int(0.15 * len(cvs)), replace=False))
            out, vn = run([g for g in tr if g.cv_id not in vc], [g for g in tr if g.cv_id in vc], vk, name, seed, dims, key="cv_id")
            s = {(c, j): x for c, j, x in out}
            df[f"req|{name}|s{seed}"] = [s[(c, j)] for c, j in zip(df.cv_id, df.jd_id)]
            vrows.append((name, seed, vn))
            print("xong", name, "seed", seed, "val NDCG@10 theo CV = %.4f" % vn, flush=True)
            df.to_csv(os.path.join(RES, "vk_scores.csv"), index=False)
            pd.DataFrame(vrows, columns=["config", "seed", "val_ndcg10"]).to_csv(os.path.join(RES, "vk_val.csv"), index=False)
    print("đã lưu")
