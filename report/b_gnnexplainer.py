"""
So sánh giải thích bằng attention của chính mô hình với GNNExplainer (nhận xét của cô: "Lấy bằng chứng từ chính mô hình (attention, GNNExplainer)").
Cấu hình chính pair_skip_mlp_specfeat, chia theo JD, 5 seed (cùng fold/validation/seed như mô hình chính).

Cả hai cách cho một độ quan trọng trên mỗi CẠNH KHỚP (yêu cầu JD, mục CV):
 - attention : w_r · σ(s_e)  (trọng số attention của yêu cầu × độ khớp của cạnh, đúng các đại lượng dùng để sinh lời giải thích)
 - GNNExplainer (Ying et al., 2019): học mặt nạ mềm m_e = σ(θ_e) trên cạnh khớp (s_e -> m_e·s_e + (1-m_e)·(-4)),
   mục tiêu bài toán hồi quy như PyG: (f(m) - f_gốc)^2 + 0,005·Σm + 1,0·entropy(m); Adam lr 0,01, 100 bước (mặc định PyG), θ khởi tạo N(1; 0,1).
 - ngẫu nhiên: đối chứng.
Độ đo (mỗi cặp kiểm tra, mỗi seed):
 - xóa top-k cạnh (k = 1, 3) theo từng cách -> điểm giảm bao nhiêu (càng lớn càng trung thành)
 - chỉ giữ top-k cạnh -> |điểm − điểm gốc| (càng nhỏ càng đủ)
 - trùng top-1, Jaccard top-3 giữa attention và GNNExplainer; thời gian tính.
Chạy: python report/b_gnnexplainer.py [--seeds 5]
Ra:   report/results/b_gnnexplainer.json, b_gnnexplainer_pairs.csv
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Batch
from torch_geometric.utils import scatter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from src.modeling.train_req import build_all, run, splits

RES = os.path.join(ROOT, "report", "results")
MAIN = "pair_skip_mlp_specfeat"
KS = (1, 3)


def fwd(m, B, mask=None):
    m.edge_mask = mask
    out = m(B)
    m.edge_mask = None
    return out


def gnnexplainer(m, B, f0, eg, n_graph, epochs=100, lr=0.01, size=0.005, ent=1.0, seed=0):
    torch.manual_seed(seed)
    E = eg.numel()
    th = torch.nn.Parameter(1 + 0.1 * torch.randn(E))
    opt = torch.optim.Adam([th], lr=lr)
    for _ in range(epochs):
        mk = torch.sigmoid(th)
        h = -(mk * torch.log(mk + 1e-15) + (1 - mk) * torch.log(1 - mk + 1e-15))
        loss = ((fwd(m, B, mk) - f0) ** 2).sum() + size * mk.sum() + ent * scatter(h, eg, 0, dim_size=n_graph, reduce="mean").sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return torch.sigmoid(th).detach()


def topk_masks(imp, eg, n_graph, k):
    """Mặt nạ 0/1: 'del' = bỏ top-k cạnh mỗi đồ thị, 'keep' = chỉ giữ top-k."""
    keep = torch.zeros_like(imp)
    for gi in range(n_graph):
        idx = (eg == gi).nonzero().flatten()
        keep[idx[torch.argsort(-imp[idx])[:k]]] = 1.0
    return 1 - keep, keep


def top_sets(imp, eg, n_graph, k):
    return [set(((eg == gi).nonzero().flatten()[torch.argsort(-imp[eg == gi])[:k]]).tolist()) for gi in range(n_graph)]


# tự kiểm tra top-k theo từng đồ thị
_eg = torch.tensor([0, 0, 0, 1, 1])
_d, _k = topk_masks(torch.tensor([0.1, 0.9, 0.5, 0.2, 0.8]), _eg, 2, 1)
assert _k.tolist() == [0, 1, 0, 0, 1] and _d.tolist() == [1, 0, 1, 1, 0]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    gs = build_all({})
    dims = {k: gs[0][k].x.size(1) for k in ("req", "item", "spec")}
    folds, _ = splits(gs, "jd")
    rows, secs = [], {"attention": 0.0, "gnnexplainer": 0.0}
    for seed in range(a.seeds):
        rng = torch.Generator().manual_seed(1000 + seed)
        for f, pool, test in folds:
            js = sorted({g.jd_id for g in pool})
            vj = set(np.random.default_rng(seed).choice(js, size=max(1, int(0.15 * len(js))), replace=False))
            _, _, m = run([g for g in pool if g.jd_id not in vj], [g for g in pool if g.jd_id in vj], [], MAIN, seed, dims, ret_model=True)
            m.eval().requires_grad_(False)
            B = Batch.from_data_list(test)
            ng = len(test)
            t0 = time.time()
            with torch.no_grad():
                f0 = fwd(m, B)
                w, c, s = m.last
            ei = B["req", "match", "item"].edge_index
            eg = B["req"].batch[ei[0]]
            imp = {"attention": w[ei[0]] * torch.sigmoid(s)}
            secs["attention"] += time.time() - t0
            t0 = time.time()
            imp["gnnexplainer"] = gnnexplainer(m, B, f0, eg, ng, seed=seed)
            secs["gnnexplainer"] += time.time() - t0
            imp["random"] = torch.rand(eg.numel(), generator=rng)
            ne = torch.bincount(eg, minlength=ng)
            res = {}
            with torch.no_grad():
                for name, v in imp.items():
                    for k in KS:
                        dm, km = topk_masks(v, eg, ng, k)
                        res[f"{name}_del{k}"] = (f0 - fwd(m, B, dm)).tolist()
                        res[f"{name}_keep{k}"] = (fwd(m, B, km) - f0).abs().tolist()
            a1, g1 = top_sets(imp["attention"], eg, ng, 1), top_sets(imp["gnnexplainer"], eg, ng, 1)
            a3, g3 = top_sets(imp["attention"], eg, ng, 3), top_sets(imp["gnnexplainer"], eg, ng, 3)
            for i, g in enumerate(test):
                rows.append({"seed": seed, "fold": f, "cv_id": g.cv_id, "jd_id": g.jd_id, "grade": g.grade, "n_edges": int(ne[i]), "score": float(f0[i]),
                             **{k: v[i] for k, v in res.items()}, "top1_same": float(a1[i] == g1[i]),
                             "jacc3": len(a3[i] & g3[i]) / max(1, len(a3[i] | g3[i]))})
        print("xong seed", seed, flush=True)
        pd.DataFrame(rows).to_csv(os.path.join(RES, "b_gnnexplainer_pairs.csv"), index=False)

    D = pd.DataFrame(rows)
    D = D[D.n_edges >= 2]                                  # cần ít nhất 2 cạnh để so thứ tự
    S = D.groupby("seed").mean(numeric_only=True)
    out = {"n_pairs_per_seed": int(len(D) / a.seeds), "sec_per_pair": {k: v / len(rows) for k, v in secs.items()}, "metrics": {}}
    print(f"\n{len(D) // a.seeds} cặp mỗi seed (>= 2 cạnh khớp), {a.seeds} seed; giá trị = TB theo cặp, ± độ lệch chuẩn giữa các seed")
    print(f"{'':<16}" + "".join(f"{f'xóa top-{k} (↑)':>18}{f'giữ top-{k}: |Δ| (↓)':>22}" for k in KS))
    for name in ("attention", "gnnexplainer", "random"):
        cols = [f"{name}_{t}{k}" for k in KS for t in ("del", "keep")]
        print(f"{name:<16}" + "".join(f"{S[c].mean():>12.3f}±{S[c].std():.3f}" + " " * (4 if 'keep' in c else 0) for c in cols))
        out["metrics"][name] = {c: [float(S[c].mean()), float(S[c].std())] for c in cols}
    for k in KS:
        x = D.groupby(["cv_id", "jd_id"])[[f"attention_del{k}", f"gnnexplainer_del{k}"]].mean()
        d = (x[f"attention_del{k}"] - x[f"gnnexplainer_del{k}"]).to_numpy()
        bs = [d[np.random.default_rng(b).integers(len(d), size=len(d))].mean() for b in range(2000)]
        out[f"attention_minus_gnnexplainer_del{k}"] = {"mean": float(d.mean()), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                                                         "share_attention_ge": float((d >= 0).mean())}
        print(f"xóa top-{k}: attention − GNNExplainer = {d.mean():+.3f}  CI95 [{np.percentile(bs, 2.5):+.3f}, {np.percentile(bs, 97.5):+.3f}]"
              f"  (attention >= GNNExplainer ở {(d >= 0).mean():.0%} cặp; bootstrap trên cặp, điểm TB các seed)")
    out["top1_same"], out["jaccard_top3"] = float(D.top1_same.mean()), float(D.jacc3.mean())
    print(f"trùng cạnh top-1: {D.top1_same.mean():.1%}; Jaccard top-3: {D.jacc3.mean():.3f}")
    print("thời gian / cặp: " + ", ".join(f"{k} {v * 1000:.2f} ms" for k, v in out["sec_per_pair"].items()))
    json.dump(out, open(os.path.join(RES, "b_gnnexplainer.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
