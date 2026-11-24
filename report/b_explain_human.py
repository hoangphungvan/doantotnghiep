"""
Đánh giá bởi người cho 100 lời giải thích (nhận xét của cô: 3 người chấm, tính đúng và tính hữu ích, thang 1-5).
Đọc report/annotation/gui_nguoi_cham/giai_thich_nguoi{1,2,3}.xlsx, nhãn/điểm mô hình từ sheet ẩn của explanations_100.xlsx.
Ra: điểm trung bình (CI95 bootstrap theo cặp), phân bố, độ đồng thuận giữa người chấm
    (Krippendorff alpha ordinal/interval, ICC(2,1) và ICC(2,k) hai chiều ngẫu nhiên, tuyệt đối; tỉ lệ trùng/lệch <= 1 theo cặp người),
    điểm theo nhãn 0-3, và toàn bộ ghi chú -> report/results/b_explain_human.json, .log
Chạy: python report/b_explain_human.py
"""
import json
import os
import sys
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
ANN = os.path.join(ROOT, "report", "annotation")
RES = os.path.join(ROOT, "report", "results")
CRIT = {"dung_1_5": "Tính đúng", "huu_ich_1_5": "Tính hữu ích"}


def kalpha(data, level="ordinal"):
    """Krippendorff alpha; data: mảng (người chấm × đơn vị), np.nan = thiếu."""
    data = np.asarray(data, float)
    vals = np.unique(data[~np.isnan(data)])
    ix = {v: i for i, v in enumerate(vals)}
    o = np.zeros((len(vals), len(vals)))
    for u in data.T:
        u = u[~np.isnan(u)]
        if len(u) < 2:
            continue
        for a in range(len(u)):
            for b in range(len(u)):
                if a != b:
                    o[ix[u[a]], ix[u[b]]] += 1 / (len(u) - 1)
    nc = o.sum(1)
    n = nc.sum()
    if level == "nominal":
        d = 1.0 - np.eye(len(vals))
    elif level == "interval":
        d = (vals[:, None] - vals[None, :]) ** 2
    else:
        cs = np.cumsum(nc)
        d = np.array([[(cs[max(c, k)] - (cs[min(c, k) - 1] if min(c, k) else 0) - (nc[c] + nc[k]) / 2) ** 2 for k in range(len(vals))] for c in range(len(vals))])
    return 1 - (o * d).sum() / n / ((np.outer(nc, nc) * d).sum() / (n * (n - 1)))


def icc2(Y):
    """ICC(2,1) và ICC(2,k) (Shrout–Fleiss); Y: (đơn vị × người chấm), đủ dữ liệu."""
    Y = np.asarray(Y, float)
    n, k = Y.shape
    g = Y.mean()
    msr = k * ((Y.mean(1) - g) ** 2).sum() / (n - 1)
    msc = n * ((Y.mean(0) - g) ** 2).sum() / (k - 1)
    mse = (((Y - g) ** 2).sum() - msr * (n - 1) - msc * (k - 1)) / ((n - 1) * (k - 1))
    return (msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n), (msr - mse) / (msr + (msc - mse) / n)


# tự kiểm tra: ví dụ chuẩn của Krippendorff (4 người chấm, 12 đơn vị) -> nominal 0,743, ordinal 0,815, interval 0,849
_N = np.nan
_K = [[1, 2, 3, 3, 2, 1, 4, 1, 2, _N, _N, _N], [1, 2, 3, 3, 2, 2, 4, 1, 2, 5, _N, 3],
      [_N, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, _N], [1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, _N]]
assert [round(kalpha(_K, m), 3) for m in ("nominal", "ordinal", "interval")] == [0.743, 0.815, 0.849]
assert np.allclose(icc2([[1, 1], [3, 3], [5, 5]]), (1, 1))

if __name__ == "__main__":
    R = [pd.read_excel(os.path.join(ANN, "gui_nguoi_cham", f"giai_thich_nguoi{i}.xlsx"), sheet_name="cham").sort_values("stt").reset_index(drop=True) for i in (1, 2, 3)]
    key = R[0][["stt", "cv_id", "jd_id"]]
    assert all(r[["stt", "cv_id", "jd_id"]].equals(key) for r in R), "các file không cùng thứ tự cặp"
    lab = pd.read_excel(os.path.join(ANN, "explanations_100.xlsx"), sheet_name="an_nhan_khong_dua_nguoi_cham")
    key = key.merge(lab, on=["stt", "cv_id", "jd_id"], how="left")
    rng = np.random.default_rng(0)
    out = {"n_pairs": len(key), "criteria": {}}
    for c, name in CRIT.items():
        Y = np.column_stack([r[c].astype(float) for r in R])          # 100 × 3
        assert not np.isnan(Y).any() and set(np.unique(Y)) <= {1, 2, 3, 4, 5}
        m = Y.mean(1)
        bs = [m[rng.integers(len(m), size=len(m))].mean() for _ in range(2000)]
        a_o, a_i = kalpha(Y.T, "ordinal"), kalpha(Y.T, "interval")
        i1, ik = icc2(Y)
        pw = {f"{a + 1}-{b + 1}": {"trung": float((Y[:, a] == Y[:, b]).mean()), "lech<=1": float((abs(Y[:, a] - Y[:, b]) <= 1).mean()),
                                   "spearman": float(spearmanr(Y[:, a], Y[:, b]).correlation)} for a, b in combinations(range(3), 2)}
        by = {int(g): float(m[key.grade == g].mean()) for g in sorted(key.grade.dropna().unique())}
        dist = {int(v): float((Y == v).mean()) for v in range(1, 6)}
        out["criteria"][name] = {"mean": float(m.mean()), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "sd_pairs": float(m.std(ddof=1)),
                                 "mean_by_rater": [float(x) for x in Y.mean(0)], "share_ge4": float((Y >= 4).mean()), "dist": dist,
                                 "alpha_ordinal": float(a_o), "alpha_interval": float(a_i), "icc2_1": float(i1), "icc2_k": float(ik), "pairwise": pw, "mean_by_grade": by}
        print(f"\n== {name} (1-5), {len(m)} cặp × 3 người chấm")
        print(f"  trung bình {m.mean():.2f}  CI95 [{np.percentile(bs, 2.5):.2f}, {np.percentile(bs, 97.5):.2f}]  ; theo người: " + ", ".join(f"{x:.2f}" for x in Y.mean(0)))
        print("  phân bố: " + "  ".join(f"{v}:{p:.0%}" for v, p in dist.items()) + f"   ; tỉ lệ >= 4: {(Y >= 4).mean():.0%}")
        print(f"  Krippendorff alpha ordinal {a_o:.3f}, interval {a_i:.3f} ; ICC(2,1) {i1:.3f}, ICC(2,k=3) {ik:.3f}")
        print("  theo cặp người: " + " ; ".join(f"{k}: trùng {v['trung']:.0%}, lệch<=1 {v['lech<=1']:.0%}, rho {v['spearman']:.2f}" for k, v in pw.items()))
        print("  theo nhãn: " + ", ".join(f"nhãn {g}: {v:.2f}" for g, v in by.items()))
    d, h = (np.column_stack([r[c].astype(float) for r in R]).mean(1) for c in CRIT)
    out["spearman_dung_huu_ich"] = float(spearmanr(d, h).correlation)
    print(f"\nSpearman (tính đúng, tính hữu ích) trên điểm trung bình cặp: {out['spearman_dung_huu_ich']:.2f}")
    low = key.assign(dung=d, huu_ich=h).sort_values("dung").head(10)
    out["thap_nhat"] = low[["stt", "cv_id", "jd_id", "grade", "dung", "huu_ich"]].to_dict("records")
    notes = [(int(r.stt), i + 1, str(r.ghi_chu)) for i, x in enumerate(R) for r in x.itertuples() if isinstance(r.ghi_chu, str) and r.ghi_chu.strip()]
    out["ghi_chu"] = [{"stt": s, "nguoi": p, "ghi_chu": t} for s, p, t in notes]
    print(f"\n{len(notes)} ghi chú:")
    for s, p, t in sorted(notes):
        print(f"  cặp {s:>3} người {p}: {t}")
    json.dump(out, open(os.path.join(RES, "b_explain_human.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
