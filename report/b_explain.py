"""
Đánh giá diễn giải sinh từ đồ thị (nhận xét của cô, mục 'Diễn giải'), cấu hình chính pair_skip_mlp_specfeat, chia theo JD, 5 seed.
Lời giải thích lấy từ chính mô hình: mỗi yêu cầu JD có trọng số attention w, độ phủ σ(c) (max trên các cạnh khớp) và mục CV
làm bằng chứng (cạnh khớp có điểm cao nhất). 'Đã đáp ứng' = σ(c) >= 0.5.
Kiểm tra 'xóa' (mỗi cặp kiểm tra, mỗi seed; dựng lại đồ thị rồi chấm lại bằng đúng mô hình đó):
  A. bỏ khỏi JD yêu cầu đã đáp ứng có đóng góp w·σ lớn nhất -> điểm phải giảm
     đối chứng: một yêu cầu đã đáp ứng ngẫu nhiên; và từng yêu cầu đã đáp ứng
  B. bỏ khỏi CV mục bằng chứng của yêu cầu đó -> điểm phải giảm; đối chứng: một mục CV ngẫu nhiên
  C. bỏ khỏi JD yêu cầu chưa đáp ứng quan trọng nhất (w·(1-σ) lớn nhất) -> điểm phải tăng
Chạy: python report/b_explain.py [--seeds 5]
Ra:   report/results/b_explain.json, report/annotation/explanations_100.xlsx (100 lời giải thích cho 3 người chấm)
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Batch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from src.data_collection.extract_requirements_all import load_texts
from src.modeling.train_req import build_all, run, splits
from src.representation.req_graph import Embedder, build_pair_graph

RES = os.path.join(ROOT, "report", "results")
MAIN = "pair_skip_mlp_specfeat"
EPS = 1e-6
LV = {None: "không nêu", "intern": "thực tập", "fresher": "fresher", "junior": "junior", "middle": "middle", "senior": "senior",
      "lead": "trưởng nhóm", "manager": "quản lý"}


def score(m, gl):
    with torch.no_grad():
        return m(Batch.from_data_list(gl)).tolist()


def inspect(m, g):
    """Điểm gốc và bảng theo yêu cầu: w, σ(c), chỉ số mục CV bằng chứng (-1 nếu không có mục cùng loại)."""
    with torch.no_grad():
        s0 = m(Batch.from_data_list([g])).item()
        w, c, s = m.last
    ei = g["req", "match", "item"].edge_index
    ev = []
    for r in range(len(w)):
        k = (ei[0] == r).nonzero().flatten()
        ev.append(int(ei[1, k[s[k].argmax()]]) if len(k) else -1)
    return s0, w.numpy(), torch.sigmoid(c).numpy(), ev


def drop(doc, i):
    return {**doc, "items": [x for j, x in enumerate(doc["items"]) if j != i]}


def explain(cv, jd, w, cov, ev, gap_lv, gap_y):
    """Lời giải thích dạng văn bản, chỉ dùng các đại lượng của mô hình (không có LLM)."""
    rq = lambda x: "Bắt buộc" if x["required"] else "Ưu tiên"
    o = np.argsort(-w)
    K = o[: min(10, int(np.searchsorted(np.cumsum(w[o]), 0.9)) + 1)]   # yêu cầu chiếm 90% tổng trọng số attention (tối đa 10)
    ok, no = [r for r in K if cov[r] >= 0.5], [r for r in K if cov[r] < 0.5]
    n_ok = int((cov >= 0.5).sum())
    L = [f"Mức đáp ứng có trọng số: {100 * float((w * cov).sum()):.0f}%  ({n_ok}/{len(w)} yêu cầu đã đáp ứng)",
         f"Mô hình dựa chủ yếu vào {len(K)} yêu cầu (chiếm {100 * float(w[K].sum()):.0f}% trọng số):", "Đã đáp ứng:"]
    L += [f"  • [{rq(jd['items'][r])}] {jd['items'][r]['text']}  ←  CV: “{cv['items'][ev[r]]['text']}” (độ phủ {cov[r]:.2f}, trọng số {100 * w[r]:.0f}%)" for r in ok] or ["  (không có)"]
    L.append("Chưa đáp ứng:")
    L += [f"  • [{rq(jd['items'][r])}] {jd['items'][r]['text']} (trọng số {100 * w[r]:.0f}%)  —  " +
          (f"mục gần nhất trong CV: “{cv['items'][ev[r]]['text']}” (độ phủ {cov[r]:.2f})" if ev[r] >= 0 else "CV không có mục cùng loại") for r in no] or ["  (không có)"]
    if len(w) > len(K):
        L.append(f"{len(w) - len(K)} yêu cầu còn lại có trọng số không đáng kể (tổng {100 * float(1 - w[K].sum()):.0f}%), trong đó {n_ok - len(ok)} đã đáp ứng.")
    ys = lambda v: "không nêu" if v is None else f"{v:g} năm"
    L.append(f"Cấp độ: JD {LV.get(jd['level'], jd['level'])}, CV {LV.get(cv['level'], cv['level'])}" + (" → CV thấp hơn yêu cầu" if gap_lv > 0 else "") +
             f".  Kinh nghiệm: JD {ys(jd['total_years'])}, CV {ys(cv['total_years'])}" + (" → CV thiếu kinh nghiệm" if gap_y > 0 else "") + ".")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--xlsx-only", action="store_true", help="chỉ sinh lại 100 lời giải thích (seed 0), không chạy kiểm tra xóa")
    a = ap.parse_args()
    a.seeds = 1 if a.xlsx_only else a.seeds
    docs = {}
    gs = build_all(docs)
    emb = Embedder()
    dims = {k: gs[0][k].x.size(1) for k in ("req", "item", "spec")}
    folds, _ = splits(gs, "jd")
    rec, expl = [], []
    for seed in range(a.seeds):
        rng = np.random.default_rng(1000 + seed)
        for f, pool, test in folds:
            js = sorted({g.jd_id for g in pool})
            vj = set(np.random.default_rng(seed).choice(js, size=max(1, int(0.15 * len(js))), replace=False))
            _, _, m = run([g for g in pool if g.jd_id not in vj], [g for g in pool if g.jd_id in vj], [], MAIN, seed, dims, ret_model=True)
            for g in test:
                cv, jd = docs["cv"][g.cv_id], docs["jd"][g.jd_id]
                s0, w, cov, ev = inspect(m, g)
                ok, no = np.where(cov >= 0.5)[0], np.where(cov < 0.5)[0]
                variants = {}                                     # tên -> đồ thị sau khi xóa
                if len(ok) and len(w) >= 2 and not a.xlsx_only:
                    top = ok[np.argmax((w * cov)[ok])]
                    variants["A_top"] = build_pair_graph(cv, drop(jd, top), emb)
                    variants["A_rand"] = build_pair_graph(cv, drop(jd, rng.choice(ok)), emb)
                    for r in ok:
                        variants[f"A_all{r}"] = build_pair_graph(cv, drop(jd, r), emb)
                    if len(cv["items"]) >= 2:
                        variants["B_top"] = build_pair_graph(drop(cv, ev[top]), jd, emb)
                        variants["B_rand"] = build_pair_graph(drop(cv, rng.integers(len(cv["items"]))), jd, emb)
                if len(no) and len(w) >= 2 and not a.xlsx_only:
                    variants["C_top"] = build_pair_graph(cv, drop(jd, no[np.argmax((w * (1 - cov))[no])]), emb)
                if variants:
                    for k, s in zip(variants, score(m, list(variants.values()))):
                        rec.append((seed, g.cv_id, g.jd_id, k[:5] if k.startswith("A_all") else k, s - s0))
                if seed == 0:
                    gap = g["spec", "cmp", "spec"].edge_attr[:, 1].tolist()
                    expl.append((g.cv_id, g.jd_id, g.grade, s0, explain(cv, jd, w, cov, ev, *gap)))
        print("xong seed", seed, flush=True)

    if not a.xlsx_only:
        R = pd.DataFrame(rec, columns=["seed", "cv_id", "jd_id", "test", "delta"])
        R.to_csv(os.path.join(RES, "b_explain_deltas.csv"), index=False)
        want = {"A_top": -1, "A_rand": -1, "A_all": -1, "B_top": -1, "B_rand": -1, "C_top": +1}
        out = {}
        print(f"\n{'Kiểm tra':<10}{'kỳ vọng':>9}{'số cặp':>8}{'tỉ lệ đúng chiều':>20}{'không ngược chiều':>20}{'Δ trung vị':>12}{'Δ TB':>9}")
        for t, sign in want.items():
            x = R[R.test == t]
            per = x.groupby("seed").delta.apply(lambda d: ((sign * d) > EPS).mean())
            nonneg = x.groupby("seed").delta.apply(lambda d: ((sign * d) >= -EPS).mean())
            out[t] = {"expect": "giảm" if sign < 0 else "tăng", "n_per_seed": int(len(x) / a.seeds), "share_correct": float(per.mean()), "share_correct_std": float(per.std(ddof=0)),
                      "share_not_wrong": float(nonneg.mean()), "median_delta": float(x.delta.median()), "mean_delta": float(x.delta.mean())}
            print(f"{t:<10}{out[t]['expect']:>9}{out[t]['n_per_seed']:>8}{per.mean():>14.3f}±{per.std(ddof=0):.3f}{nonneg.mean():>20.3f}{x.delta.median():>12.3f}{x.delta.mean():>9.3f}")
        # bằng chứng của yêu cầu quan trọng nhất có làm giảm điểm nhiều hơn một mục ngẫu nhiên không (ghép theo cặp, mọi seed)
        p = R[R.test.isin(["B_top", "B_rand", "A_top", "A_rand"])].pivot_table(index=["seed", "cv_id", "jd_id"], columns="test", values="delta")
        for x, y in (("B_top", "B_rand"), ("A_top", "A_rand")):
            q = p[[x, y]].dropna()
            out[f"{x}<{y}"] = float((q[x] < q[y] - EPS).mean())
            print(f"{x} giảm nhiều hơn {y}: {out[f'{x}<{y}']:.3f} số cặp")
        json.dump(out, open(os.path.join(RES, "b_explain.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 100 lời giải thích (seed 0) chia đều theo nhãn, cho 3 người chấm; nhãn và điểm để ở sheet riêng để người chấm không bị ảnh hưởng
    cvt, jdt = load_texts()
    A = pd.DataFrame(expl, columns=["cv_id", "jd_id", "grade", "score", "giai_thich"])
    idx = [i for _, d in A.groupby("grade") for i in d.sample(min(len(d), 25), random_state=0).index]
    idx += list(A.drop(idx).sample(100 - len(idx), random_state=0).index)     # bù nếu nhãn nào có < 25 cặp
    E = A.loc[idx].sample(frac=1, random_state=1).reset_index(drop=True)
    E.insert(0, "stt", range(1, len(E) + 1))
    sheet = E[["stt", "cv_id", "jd_id"]].assign(jd_text=E.jd_id.map(jdt), cv_text=E.cv_id.map(cvt), giai_thich=E.giai_thich)
    for i in (1, 2, 3):
        sheet[f"nguoi{i}_dung_1_5"], sheet[f"nguoi{i}_huu_ich_1_5"] = "", ""
    os.makedirs(os.path.join(ROOT, "report", "annotation"), exist_ok=True)
    with pd.ExcelWriter(os.path.join(ROOT, "report", "annotation", "explanations_100.xlsx")) as xw:
        sheet.to_excel(xw, sheet_name="cham", index=False)
        pd.DataFrame({"cot": ["dung_1_5", "huu_ich_1_5"],
                      "huong_dan": ["Tính đúng: các yêu cầu ghi 'đã đáp ứng'/'chưa đáp ứng' và bằng chứng trích từ CV có đúng với văn bản không (1 = sai nhiều, 5 = đúng hoàn toàn)",
                                    "Tính hữu ích: lời giải thích có giúp nhà tuyển dụng quyết định nhanh và đúng hơn không (1 = vô ích, 5 = rất hữu ích)"]}).to_excel(xw, sheet_name="huong_dan", index=False)
        E[["stt", "cv_id", "jd_id", "grade", "score"]].to_excel(xw, sheet_name="an_nhan_khong_dua_nguoi_cham", index=False)
    print("đã lưu")
