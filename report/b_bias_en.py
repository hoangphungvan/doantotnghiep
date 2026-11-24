"""
Thiên kiến theo tên (chủng tộc × giới tính) trên CV tiếng Anh THẬT, theo thiết kế của Wilson & Caliskan (AIES 2024,
github.com/kyrawilson/Resume-Screening-Bias): gắn một tên vào đầu CV (không đổi gì khác) rồi so điểm/khả năng được chọn giữa các nhóm.
  CV : 100 CV thật của bộ Djinni (lang-uk/recruitment-dataset-candidate-profiles-english), 10 nghề × 10 CV
       (+ CV của Kaggle snehaanbhawal/resume-dataset nếu có data/raw/snehaanbhawal/Resume.csv: bộ CV mà Wilson & Caliskan dùng).
  JD : 30 JD của resume-job-fit (3 JD cho mỗi nghề), đã trích xuất sẵn.
  Tên: danh sách của Bertrand & Mullainathan (2004): trắng/đen × nam/nữ (WM, WF, BM, BF), xoay vòng theo CV.
  Biến thể: orig (CV gốc), ctl (thêm tiêu đề trung tính "RESUME": đo nhiễu do trích xuất lại), WM/WF/BM/BF (thêm dòng tên).
  Mô hình: cấu hình chính huấn luyện trên TOÀN BỘ resume-job-fit (15% JD validation), 5 seed, điểm = trung bình seed.
  Đối chứng: SBERT BGE-M3 và MiniLM trên văn bản gốc (như các mô hình retrieval mà Wilson & Caliskan kiểm tra).
Đo: |Δ| so với orig (đơn vị SD điểm trong JD); chênh có hướng W−B, M−F và 4 cặp giao thoa (bootstrap theo CV);
    tỉ lệ mỗi nhóm trong top 10% của từng JD khi gộp 4 biến thể tên của mọi CV (kỳ vọng 25% nếu không thiên kiến).
Chạy: python report/b_bias_en.py --extract   (gọi LLM trích xuất các biến thể, ghi cache)
      python report/b_bias_en.py             (huấn luyện, chấm, tổng hợp -> report/results/b_bias_en.json, b_bias_en_scores.csv)
"""
import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
import config
from src.extraction import requirement_extractor as R

RES = os.path.join(ROOT, "report", "results")
MAIN = "pair_skip_mlp_specfeat"
DJ = os.path.join(config.DATA_RAW_DIR, "lang-ukrecruitment-dataset-candidate-profiles-english", "train-00000-of-00001.parquet")
SN = os.path.join(config.DATA_RAW_DIR, "snehaanbhawal", "Resume.csv")
# nghề: (Primary Keyword của Djinni, regex chọn JD của resume-job-fit theo phần đầu văn bản JD)
ROLES = {"JavaScript": r"front[- ]?end|react|javascript|angular", "QA": r"\bQA\b|quality assurance|tester|test engineer",
         "Design": r"designer|ui/ux|ux/ui", "Project Manager": r"project manager", ".NET": r"\.net|c#", "Python": r"python",
         "DevOps": r"devops|site reliability|cloud engineer", "Business Analyst": r"business analyst", "Data Science": r"data scien|machine learning",
         "Sales": r"sales (representative|manager|executive|rep)\b|account executive|business development|\bquota"}
# Bertrand & Mullainathan (2004), AER 94(4): tên gợi chủng tộc/giới tính
FIRST = {"WF": ["Allison", "Anne", "Carrie", "Emily", "Jill", "Laurie", "Kristen", "Meredith", "Sarah"],
         "BF": ["Aisha", "Ebony", "Keisha", "Kenya", "Lakisha", "Latonya", "Latoya", "Tamika", "Tanisha"],
         "WM": ["Brad", "Brendan", "Geoffrey", "Greg", "Brett", "Jay", "Matthew", "Neil", "Todd"],
         "BM": ["Darnell", "Hakim", "Jamal", "Jermaine", "Kareem", "Leroy", "Rasheed", "Tremayne", "Tyrone"]}
LAST = {"W": ["Baker", "Kelly", "McCarthy", "Murphy", "Murray", "O'Brien", "Ryan", "Sullivan", "Walsh"],
        "B": ["Jackson", "Jones", "Robinson", "Washington", "Williams"]}
GROUPS = ("WM", "WF", "BM", "BF")
VARS = ("ctl",) + GROUPS
CONTRASTS = {"W−B": (("WM", "WF"), ("BM", "BF")), "M−F": (("WM", "BM"), ("WF", "BF")),
             "WM−BM": (("WM",), ("BM",)), "WF−BF": (("WF",), ("BF",)), "WM−WF": (("WM",), ("WF",)), "BM−BF": (("BM",), ("BF",))}


def name(g, i):
    return f"{FIRST[g][i % 9]} {LAST[g[0]][i % len(LAST[g[0]])]}"


def sample_cvs(n_per_role=10, seed=0):
    d = pd.read_parquet(DJ, columns=["Primary Keyword", "CV", "id"])
    d = d[d.CV.str.len().between(600, 4000)].drop_duplicates("CV")
    out = {}
    for role in ROLES:
        x = d[d["Primary Keyword"] == role].sample(n_per_role, random_state=seed)
        out.update({f"dj_{r.id[:8]}": (role, r.CV.strip()) for r in x.itertuples()})
    if os.path.exists(SN):                                   # bộ CV của Wilson & Caliskan (nếu đã tải về)
        s = pd.read_csv(SN)
        cat = {"JavaScript": "INFORMATION-TECHNOLOGY", "Design": "DESIGNER", "Sales": "SALES", "Business Analyst": "BUSINESS-DEVELOPMENT"}
        for role, c in cat.items():
            x = s[(s.Category == c) & s.Resume_str.str.len().between(600, 8000)].sample(n_per_role, random_state=seed)
            out.update({f"sn_{r.ID}": (role, re.sub(r"\s{3,}", "\n", r.Resume_str).strip()) for r in x.itertuples()})
    return out


def pick_jds(per_role=3, seed=0):
    cache = R._load()
    j = pd.concat([pd.read_csv(os.path.join(config.DATA_RAW_DIR, "cnamuangtoun", f"{s}.csv")) for s in ("train", "test")]).job_description_text.drop_duplicates()
    j = [t for t in j if (c := cache.get(R._key(t, "JD"))) and c["items"]]
    out, used = {}, set()
    for role, pat in ROLES.items():
        hits = sorted(((len(re.findall(pat, t, re.I)), t) for t in j if t not in used), key=lambda x: -x[0])   # JD nói về nghề này nhiều nhất
        for _, t in hits[:per_role]:
            used.add(t)
            out[f"jd{len(out):02d}"] = (role, t)
    return out


def variants(cvs):
    return {c: {"orig": t, "ctl": "RESUME\n\n" + t, **{g: f"{name(g, i)}\n\n{t}" for g in GROUPS}} for i, (c, (_, t)) in enumerate(sorted(cvs.items()))}


def boot_cv(P, col, n=2000, seed=0):
    """Trung bình và CI95 bootstrap theo CV (mọi cặp của một CV đi cùng nhau)."""
    g = P.dropna(subset=[col]).groupby("cv_id")[col].agg(["sum", "count"])
    s, k = g["sum"].to_numpy(), g["count"].to_numpy()
    rng = np.random.default_rng(seed)
    b = [s[i].sum() / k[i].sum() for i in (rng.integers(len(s), size=len(s)) for _ in range(n))]
    return [float(s.sum() / k.sum()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def top_share(P, frac=0.1, n=1000, seed=0):
    """Tỉ lệ mỗi nhóm tên trong top `frac` của từng JD (gộp 4 biến thể tên của mọi CV; hòa điểm phá ngẫu nhiên), trung bình theo JD; CI bootstrap theo CV."""
    rng = np.random.default_rng(seed)
    cvs = P.cv_id.unique()
    L = P.melt(id_vars=["cv_id", "jd_id"], value_vars=list(GROUPS), var_name="g", value_name="s")
    L["s"] = L.s + rng.uniform(0, 1e-9, len(L))           # phá hòa điểm (mô hình chính thường cho cùng điểm ở mọi biến thể tên)

    def share(Lx):
        k = max(1, int(round(frac * 4 * Lx.cv_id.nunique())))   # top 10% của 4 × số CV biến thể tên trong mỗi JD
        top = Lx.sort_values("s", ascending=False).groupby("jd_id").head(k)
        return top.groupby("jd_id").g.value_counts(normalize=True).unstack(fill_value=0).reindex(columns=list(GROUPS), fill_value=0).mean()

    base = share(L)
    idx = {c: L.index[L.cv_id == c] for c in cvs}
    bs = []
    for _ in range(n):
        pick = rng.choice(cvs, len(cvs))
        Lb = pd.concat([L.loc[idx[c]].assign(cv_id=f"{c}#{i}") for i, c in enumerate(pick)])
        bs.append(share(Lb))
    bs = pd.DataFrame(bs)
    return {g: [float(base[g]), float(bs[g].quantile(0.025)), float(bs[g].quantile(0.975))] for g in GROUPS}


def analyse(A):
    out = {}
    for model, X in A.groupby("model"):
        P = X.pivot_table(index=["cv_id", "jd_id"], columns="variant", values="score").reset_index()
        sd = P.groupby("jd_id").orig.transform("std")
        res = {"n_pairs": int(len(P)), "n_cv": int(P.cv_id.nunique())}
        for v in VARS:
            P[f"abs_{v}"] = ((P[v] - P.orig) / sd).abs()
            res[f"abs_{v}"] = boot_cv(P, f"abs_{v}")
        for k, (a, b) in CONTRASTS.items():
            P[k] = (P[list(a)].mean(axis=1) - P[list(b)].mean(axis=1)) / sd
            res[k] = boot_cv(P, k)
        res["top10_share"] = top_share(P)
        out[model] = res
        print(f"\n## {model} ({len(P)} cặp, {P.cv_id.nunique()} CV)")
        for v in VARS:
            print(f"  |Δ| {v:<4} = {res[f'abs_{v}'][0]:.3f} SD [{res[f'abs_{v}'][1]:.3f}, {res[f'abs_{v}'][2]:.3f}]")
        for k in CONTRASTS:
            print(f"  {k:<6} {res[k][0]:+.3f} SD [{res[k][1]:+.3f}, {res[k][2]:+.3f}]")
        print("  top-10%:", {g: f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]" for g, v in res["top10_share"].items()})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--analyse-only", action="store_true", help="chỉ tổng hợp lại từ b_bias_en_scores.csv")
    a = ap.parse_args()
    if a.analyse_only:
        out = analyse(pd.read_csv(os.path.join(RES, "b_bias_en_scores.csv")))
        json.dump(out, open(os.path.join(RES, "b_bias_en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        sys.exit()
    CV, JD = sample_cvs(), pick_jds()
    V = variants(CV)
    print(f"{len(CV)} CV, {len(JD)} JD:", pd.Series([r for r, _ in JD.values()]).value_counts().to_dict(), flush=True)
    assert len(set(V)) == len(CV) and all(len(d) == 6 for d in V.values())
    assert name("WM", 0) == "Brad Baker" and name("BF", 6) == "Latoya Jones"
    if a.extract:
        todo = sorted({t for d in V.values() for t in d.values() if R._key(t, "CV") not in R._load()})
        print("cần trích xuất:", len(todo), flush=True)
        t0 = time.time()
        for i in range(0, len(todo), 40):
            with ThreadPoolExecutor(4) as ex:
                list(ex.map(lambda t: R.extract_requirements(t, "CV"), todo[i:i + 40]))
            R.save_cache()
            print(f"đã trích xuất {min(i + 40, len(todo))}/{len(todo)}  ({time.time() - t0:.0f}s)", flush=True)
        sys.exit()

    import torch
    from torch_geometric.data import Batch
    from sentence_transformers import SentenceTransformer
    from src.modeling.train_ext import graphs, load
    from src.modeling.train_req import run
    from src.representation.req_graph import Embedder, build_pair_graph
    cache = R._load()
    ext = {(c, v): cache.get(R._key(t, "CV")) for c, d in V.items() for v, t in d.items()}
    bad = {c for (c, v), x in ext.items() if not (x and x["items"])}
    print("CV bỏ qua (có biến thể trích xuất rỗng):", len(bad), flush=True)
    jdx = {j: cache[R._key(t, "JD")] for j, (_, t) in JD.items()}
    emb = Embedder()
    data = load()
    need = sorted(({x["text"] for v in cache.values() for x in v["items"]} - set(emb.vec)))
    if need:
        emb.encode(need)
    seen, allg = set(), []
    for g in graphs(data["train"], cache, emb) + graphs(data["test"], cache, emb):
        if (g.cv_id, g.jd_id) not in seen:
            seen.add((g.cv_id, g.jd_id))
            allg.append(g)
    dims = {k: allg[0][k].x.size(1) for k in ("req", "item", "spec")}
    keys = [(c, j, v) for c in sorted(V) if c not in bad for j in JD for v in V[c]]
    gl = [build_pair_graph(ext[(c, v)], jdx[j], emb) for c, j, v in keys]
    print(f"huấn luyện trên {len(allg)} cặp resume-job-fit; chấm {len(gl)} cặp biến thể", flush=True)
    rows = []
    for seed in range(a.seeds):
        t0 = time.time()
        js = sorted({g.jd_id for g in allg})
        vj = set(np.random.default_rng(seed).choice(js, size=int(0.15 * len(js)), replace=False))
        _, vn, m = run([g for g in allg if g.jd_id not in vj], [g for g in allg if g.jd_id in vj], [], MAIN, seed, dims, ret_model=True)
        m.eval()
        with torch.no_grad():
            sc = torch.cat([m(Batch.from_data_list(gl[i:i + 256])) for i in range(0, len(gl), 256)]).tolist()
        rows += [(seed, *k, s) for k, s in zip(keys, sc)]
        print(f"xong seed {seed}: val NDCG@10 {vn:.3f} ({time.time() - t0:.0f}s)", flush=True)
    S = pd.DataFrame(rows, columns=["seed", "cv_id", "jd_id", "variant", "score"]).groupby(["cv_id", "jd_id", "variant"]).score.mean().reset_index().assign(model="Mô hình chính")
    parts = [S]
    for mname, mid in (("SBERT BGE-M3 (văn bản gốc)", "BAAI/bge-m3"), ("SBERT MiniLM (văn bản gốc)", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")):
        sb = SentenceTransformer(mid)
        sb.max_seq_length = min(512, sb.max_seq_length or 512)
        enc = lambda d: dict(zip(d, sb.encode(list(d.values()), normalize_embeddings=True, batch_size=8, show_progress_bar=False)))
        je, ce = enc({j: t for j, (_, t) in JD.items()}), enc({(c, v): t for c, d in V.items() if c not in bad for v, t in d.items()})
        parts.append(pd.DataFrame([(c, j, v, float(ce[(c, v)] @ je[j])) for c, j, v in keys], columns=["cv_id", "jd_id", "variant", "score"]).assign(model=mname))
        print("xong", mname, flush=True)
    A = pd.concat(parts)
    A.to_csv(os.path.join(RES, "b_bias_en_scores.csv"), index=False)
    out = analyse(A)
    out["design"] = {"n_cv": len(CV) - len(bad), "n_jd": len(JD), "sources": sorted({c[:2] for c in CV}), "cv_skipped": len(bad)}
    json.dump(out, open(os.path.join(RES, "b_bias_en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("đã lưu")
