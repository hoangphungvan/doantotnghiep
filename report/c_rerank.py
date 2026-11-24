"""
Baseline cross-encoder (nhận xét của cô): BAAI/bge-reranker-v2-m3 (đa ngữ) chấm trực tiếp từng cặp (JD, CV) trên văn bản gốc, không huấn luyện.
Chạy: python report/c_rerank.py [own|ext]
      ext: chỉ chấm cặp thuộc JD đủ điều kiện đánh giá, còn lại để trống
Ra:   thêm cột 'ce|bge-reranker-v2-m3' vào report/results/static_scores.csv (own) hoặc ext_cna_static.csv (ext)
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
RES = os.path.join(ROOT, "report", "results")
COL, MID = "ce|bge-reranker-v2-m3", "BAAI/bge-reranker-v2-m3"

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "own"
    if which == "own":
        from src.data_collection.extract_requirements_all import load_texts
        cvt, jdt = load_texts()
        out = os.path.join(RES, "static_scores.csv")
    else:
        from src.modeling.train_ext import load, sid
        d = load()
        df = pd.concat([d["train"], d["test"]])
        cvt, jdt = {sid(t): t for t in df.resume_text.unique()}, {sid(t): t for t in df.job_description_text.unique()}
        out = os.path.join(RES, "ext_cna_static.csv")
    S = pd.read_csv(out)
    from sentence_transformers import CrossEncoder
    m = CrossEncoder(MID, max_length=1024)              # JD + CV cắt còn 1024 token (CPU)
    todo = S.index
    if which == "ext":                                  # chỉ JD đủ điều kiện đánh giá (>=2 cặp, >=1 Good Fit); chỉ số chỉ tính trên các truy vấn này
        ok = [j for j, x in S.groupby("jd_id") if len(x) >= 2 and (x.grade >= 2).any()]
        todo = S.index[S.jd_id.isin(ok)]
    pairs = list(zip(S.jd_id[todo], S.cv_id[todo]))
    sc = []
    for i in range(0, len(pairs), 64):                  # in tiến độ, vì chạy CPU lâu
        sc += m.predict([(jdt[j], cvt[c]) for j, c in pairs[i:i + 64]], batch_size=8, show_progress_bar=False).tolist()
        print(f"{min(i + 64, len(pairs))}/{len(pairs)}", flush=True)
    S[COL] = np.nan
    S.loc[todo, COL] = sc
    S.to_csv(out, index=False)
    print("đã lưu", out)
