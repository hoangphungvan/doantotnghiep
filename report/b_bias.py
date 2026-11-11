"""
Thiên kiến và độ bền (nhận xét của cô): sửa CV mà GIỮ NGUYÊN năng lực, trích xuất lại bằng LLM, chấm lại bằng cấu hình chính rồi đo thay đổi.
Biến thể của mỗi CV (104 CV tổng hợp, vốn đã ẩn danh):
  ctl    : thêm dòng tiêu đề trung tính "HỒ SƠ ỨNG VIÊN" (đo nhiễu do trích xuất lại, làm mốc so sánh)
  nam/nu : thêm "Họ và tên" + "Giới tính" (cặp tên cùng họ, khác giới; xoay vòng 4 cặp tên)
  uniA/uniB: thay cụm trường ẩn danh có sẵn ("một trường đại học công lập...") bằng trường tốp đầu / trường địa phương (chỉ CV có ghi)
  typo   : lỗi chính tả ở ~5% số từ (bỏ dấu, đảo/xóa ký tự)
  fmt    : đổi định dạng (gạch đầu dòng -> câu nối bằng dấu chấm phẩy, tiêu đề chữ hoa -> chữ thường có dấu hai chấm)
Mô hình: pair_skip_mlp_specfeat, chia theo JD (mỗi cặp chấm bằng mô hình của fold mà JD nằm ở tập kiểm tra), 5 seed.
Đối chứng: SBERT BGE-M3 trên văn bản gốc (không qua trích xuất).
Chạy: python report/b_bias.py --extract   (chỉ gọi LLM trích xuất các biến thể, ghi cache)
      python report/b_bias.py             (chấm và tổng hợp)
Ra:   report/results/b_bias_scores.csv, report/results/b_bias.json
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Batch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from src.data_collection.extract_requirements_all import load_texts
from src.extraction import requirement_extractor as R
from src.modeling.train_req import build_all, run, splits

RES = os.path.join(ROOT, "report", "results")
MAIN = "pair_skip_mlp_specfeat"
NAMES = [("Nguyễn Văn Hùng", "Nguyễn Thị Hương"), ("Trần Minh Tuấn", "Trần Thị Thu Trang"), ("Lê Đức Anh", "Lê Thị Ngọc Anh"), ("Phạm Quốc Bảo", "Phạm Thị Bảo Ngọc")]
UNI = ("Trường Đại học Bách khoa Hà Nội", "Trường Đại học Quảng Bình")
VARS = ("ctl", "nam", "nu", "uniA", "uniB", "typo", "fmt")


def strip_one(ch):
    return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", ch) if unicodedata.category(c) != "Mn")).replace("đ", "d").replace("Đ", "D")


def typo(t, rng, rate=0.05):
    def f(m):
        w = m.group()
        if len(w) < 3 or rng.random() > rate:
            return w
        i, op = int(rng.integers(len(w) - 1)), rng.integers(3)
        if op == 0:                                   # bỏ dấu một ký tự
            return w[:i] + strip_one(w[i]) + w[i + 1:]
        if op == 1:                                   # đảo hai ký tự kề nhau
            return w[:i] + w[i + 1] + w[i] + w[i + 2:]
        return w[:i] + w[i + 1:]                      # xóa một ký tự
    return re.sub(r"\w+", f, t)


def fmt(t):
    out, buf = [], []
    for line in t.splitlines() + [""]:
        if line.startswith("- "):
            buf.append(line[2:].rstrip(". "))
            continue
        if buf:
            out.append("; ".join(buf) + ".")
            buf = []
        s = line.strip()
        out.append(s[0] + s[1:].lower() + ":" if len(s) >= 5 and s.isupper() else line)
    return "\n".join(out).strip()


UNI_RE = re.compile(r"(một |trường: )?(trường )?đại học (công lập|tư thục|dân lập|kỹ thuật)[^.,;\n]*", re.I)


def add_uni(t, u):
    """Thay cụm trường ẩn danh có sẵn bằng tên trường; None nếu CV không ghi trường đại học (không tự thêm bằng cấp)."""
    return UNI_RE.sub(u, t) if UNI_RE.search(t) else None


def variants(cvs):
    out = {}
    for i, (c, t) in enumerate(sorted(cvs.items())):
        m, f = NAMES[i % len(NAMES)]
        out[c] = {"ctl": "HỒ SƠ ỨNG VIÊN\n\n" + t, "nam": f"Họ và tên: {m}\nGiới tính: Nam\n\n" + t, "nu": f"Họ và tên: {f}\nGiới tính: Nữ\n\n" + t,
                  "uniA": add_uni(t, UNI[0]), "uniB": add_uni(t, UNI[1]), "typo": typo(t, np.random.default_rng(i)), "fmt": fmt(t)}
        out[c] = {v: x for v, x in out[c].items() if x is not None}
    return out


def rank(P, col):
    """Thứ hạng (0 = cao nhất) của CV khi điểm là P[col], so với điểm GỐC của các CV khác trong cùng JD."""
    r = pd.Series(np.nan, index=P.index)
    for _, d in P.groupby("jd_id"):
        o = d.orig.to_numpy()
        for i, (idx, s) in enumerate(d[col].items()):
            if not np.isnan(s):
                r[idx] = (np.delete(o, i) > s).sum()
    return r


def cluster_boot(df, col, n=2000, seed=0):
    """Trung bình col và CI95 bootstrap theo CV (các cặp cùng CV không độc lập)."""
    df = df.dropna(subset=[col])
    g = df.groupby("cv_id")[col].agg(["sum", "count"])
    s, k = g["sum"].to_numpy(), g["count"].to_numpy()
    rng = np.random.default_rng(seed)
    b = [s[i].sum() / k[i].sum() for i in (rng.integers(len(s), size=len(s)) for _ in range(n))]
    return float(s.sum() / k.sum()), [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    cvt, jdt = load_texts()
    V = variants(cvt)
    if a.extract:
        todo = [t for d in V.values() for t in d.values() if R._key(t, "CV") not in R._load()]
        print("cần trích xuất:", len(todo), flush=True)
        for i in range(0, len(todo), 40):             # ghi cache từng đợt để mất mạng không mất kết quả
            with ThreadPoolExecutor(4) as ex:
                list(ex.map(lambda t: R.extract_requirements(t, "CV"), todo[i:i + 40]))
            R.save_cache()
            print("đã trích xuất", min(i + 40, len(todo)), "/", len(todo), flush=True)
        sys.exit()

    from sentence_transformers import SentenceTransformer
    from src.representation.req_graph import Embedder, build_pair_graph
    cache = R._load()
    ext = {(c, v): cache.get(R._key(t, "CV")) for c, d in V.items() for v, t in d.items()}
    miss = {k for k, x in ext.items() if not (x and x["items"])} | {(c, v) for c in V for v in VARS if v not in V[c]}
    print("biến thể bỏ qua (trích xuất lỗi hoặc CV không ghi trường):", len(miss), flush=True)
    docs = {}
    gs = build_all(docs)
    emb = Embedder()
    emb.encode(sorted({x["text"] for e in ext.values() if e for x in e["items"]}))
    dims = {k: gs[0][k].x.size(1) for k in ("req", "item", "spec")}
    folds, _ = splits(gs, "jd")
    rows = []
    for seed in range(a.seeds):
        for f, pool, test in folds:
            js = sorted({g.jd_id for g in pool})
            vj = set(np.random.default_rng(seed).choice(js, size=max(1, int(0.15 * len(js))), replace=False))
            _, _, m = run([g for g in pool if g.jd_id not in vj], [g for g in pool if g.jd_id in vj], [], MAIN, seed, dims, ret_model=True)
            keys, gl = [], []
            for g in test:
                jd = docs["jd"][g.jd_id]
                keys.append((g.cv_id, g.jd_id, "orig")), gl.append(build_pair_graph(docs["cv"][g.cv_id], jd, emb))   # dựng lại như các biến thể (không nhãn)
                for v in VARS:
                    if (g.cv_id, v) not in miss:
                        keys.append((g.cv_id, g.jd_id, v)), gl.append(build_pair_graph(ext[(g.cv_id, v)], jd, emb))
            with torch.no_grad():
                sc = torch.cat([m(Batch.from_data_list(gl[i:i + 256])) for i in range(0, len(gl), 256)]).tolist()
            rows += [(seed, *k, s) for k, s in zip(keys, sc)]
        print("xong seed", seed, flush=True)
    S = pd.DataFrame(rows, columns=["seed", "cv_id", "jd_id", "variant", "score"]).groupby(["cv_id", "jd_id", "variant"]).score.mean().reset_index()
    S["model"] = "Mô hình chính"
    # đối chứng SBERT trên văn bản gốc
    sb = SentenceTransformer("BAAI/bge-m3")
    sb.max_seq_length = 512
    enc = lambda d: dict(zip(d, sb.encode(list(d.values()), normalize_embeddings=True, batch_size=8, show_progress_bar=False)))
    je = enc(jdt)
    ce = enc({(c, v): t for c, d in V.items() for v, t in [("orig", cvt[c]), *d.items()]})
    pairs = S[["cv_id", "jd_id"]].drop_duplicates()
    T = pd.DataFrame([(c, j, v, float(ce[(c, v)] @ je[j])) for c, j in pairs.itertuples(index=False) for v in ("orig", *V[c])],
                     columns=["cv_id", "jd_id", "variant", "score"]).assign(model="SBERT BGE-M3 (văn bản gốc)")
    A = pd.concat([S, T])
    A.to_csv(os.path.join(RES, "b_bias_scores.csv"), index=False)

    out = {}
    for model, X in A.groupby("model"):
        P = X.pivot_table(index=["cv_id", "jd_id"], columns="variant", values="score").reset_index()
        sd = P.groupby("jd_id").orig.transform("std")             # quy về đơn vị độ lệch chuẩn điểm trong cùng JD để so được giữa hai mô hình
        r0 = rank(P, "orig")
        res = {}
        for v in VARS:
            P[f"d_{v}"] = (P[v] - P.orig) / sd
            P[f"abs_{v}"] = P[f"d_{v}"].abs()
            P[f"rk_{v}"] = (rank(P, v) - r0).abs()                     # số bậc thay đổi thứ hạng của CV trong JD (so với các CV gốc khác)
            res[v] = {"mean_abs_delta_sd": cluster_boot(P.dropna(subset=[v]), f"abs_{v}"), "mean_rank_shift": float(P[f"rk_{v}"].dropna().mean())}
        for x, y in (("nam", "nu"), ("uniA", "uniB")):
            P[f"{x}-{y}"] = (P[x] - P[y]) / sd
            res[f"{x}-{y}"] = cluster_boot(P.dropna(subset=[x, y]), f"{x}-{y}")
        out[model] = res
        print(f"\n## {model}  ({len(P)} cặp)")
        for v in VARS:
            (m_, ci), rs = res[v]["mean_abs_delta_sd"], res[v]["mean_rank_shift"]
            print(f"  {v:<6} |Δ| = {m_:.3f} SD  [{ci[0]:.3f}, {ci[1]:.3f}]   dịch hạng TB = {rs:.2f} bậc")
        for k in ("nam-nu", "uniA-uniB"):
            print(f"  {k:<10} Δ = {res[k][0]:+.3f} SD  CI95 [{res[k][1][0]:+.3f}, {res[k][1][1]:+.3f}]")
    out["n_skipped_variants"] = len(miss)
    json.dump(out, open(os.path.join(RES, "b_bias.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("đã lưu")
