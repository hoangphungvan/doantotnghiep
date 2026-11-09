"""
Huấn luyện mô hình mức yêu cầu theo giao thức của cô:
  - protocol 'jd'    : k-fold CHIA THEO NHÓM JD (5 fold, giống report/jd_split_eval.py); truy vấn = JD.
  - protocol 'double': loại trừ CẢ HAI chiều (2 nhóm CV x 5 nhóm JD, giống report/double_split_eval.py); truy vấn = (ô, JD).
Mỗi lượt: 15% JD của phần huấn luyện làm validation (dừng sớm bằng loss xếp hạng, và NDCG@10 để CHỌN cấu hình);
tập kiểm tra chỉ được chấm một lần sau khi mô hình đã chốt. Nhiều seed.

Chạy: python src/modeling/train_req.py <jd|double> [--seeds 5] [--configs pair,pair_skip,...]
Ra:   report/results/req_<protocol>.csv      (cv_id, jd_id, qid, config, seed, score)  điểm trên tập kiểm tra
      report/results/req_<protocol>_val.csv  (config, seed, fold, val_ndcg10)           để chọn cấu hình
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch_geometric.data import Batch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import config
from src.data_collection.extract_requirements_all import load_texts
from src.evaluation.metrics import ndcg_at_k
from src.extraction import requirement_extractor as R
from src.modeling.req_model import ReqGNN
from src.representation.req_graph import DEFAULT_GRAPH, Embedder, build_pair_graph

RES = os.path.join(ROOT, "report", "results")
os.makedirs(RES, exist_ok=True)  # report/ không nằm trong repo
# cấu hình: tên -> (loss, tham số ReqGNN). 'bce' giữ lại làm ablation hàm mất mát.
CONFIGS = {
    "pair": ("pair", {}),
    "pair_skip": ("pair", {"skip": True}),
    "bce_skip": ("bce", {"skip": True}),
    "pair_skip_noattn": ("pair", {"skip": True, "attn": False}),
    "pair_skip_nospec": ("pair", {"skip": True, "spec": False}),
    "pair_skip_mean": ("pair", {"skip": True, "agg": "mean"}),
    # thay GNN bằng MLP trên CÙNG đặc trưng: 0 lớp truyền tin, giữ nguyên chiếu đặc trưng, điểm cạnh, max, attention, phạt
    "pair_skip_mlp": ("pair", {"skip": True, "layers": 0}),
    "pair_skip_L1": ("pair", {"skip": True, "layers": 1}),
    "pair_skip_L3": ("pair", {"skip": True, "layers": 3}),
    # hướng 2: truyền tin trên cạnh NGỮ CẢNH (MLP pair_skip_mlp không thấy được các cạnh này)
    "pair_skip_ctx": ("pair", {"skip": True, "ctx": ("doc", "any", "spec")}),
    "pair_skip_ctx_doc": ("pair", {"skip": True, "ctx": ("doc",)}),
    "pair_skip_ctx_any": ("pair", {"skip": True, "ctx": ("any",)}),
    "pair_skip_ctx_spec": ("pair", {"skip": True, "ctx": ("spec",)}),
    # đối chứng công bằng cho ctx_spec: MLP (0 lớp) nhưng nút yêu cầu/mục được nối thẳng đặc trưng cấp độ/số năm
    "pair_skip_mlp_specfeat": ("pair", {"skip": True, "layers": 0, "spec_feat": True}),
    "pair_skip_specfeat": ("pair", {"skip": True, "spec_feat": True}),
}
# ablation quanh CẤU HÌNH CHÍNH (pair_skip_mlp_specfeat); top-m và embedding chạy bằng biến môi trường REQ_M_TOP / REQ_EMB_MODEL
MAIN = {"skip": True, "layers": 0, "spec_feat": True}
CONFIGS.update({
    "abl_nospec": ("pair", {**MAIN, "spec_feat": False, "spec": False}),   # bỏ hẳn cấp độ/số năm (đặc trưng + phạt)
    "abl_nopen": ("pair", {**MAIN, "spec": False}),                        # chỉ bỏ phần phạt đơn điệu
    "abl_noreq": ("pair", {**MAIN, "use_req": False}),                     # bỏ phân biệt bắt buộc/ưu tiên
    "abl_mean": ("pair", {**MAIN, "agg": "mean"}),                         # max -> mean
    "abl_noattn": ("pair", {**MAIN, "attn": False}),                       # attention -> trọng số đều
    "abl_bce": ("bce", MAIN),                                              # loss pairwise -> BCE theo điểm
    "abl_noskip": ("pair", {**MAIN, "skip": False}),                       # bỏ đường tắt cosine
    "abl_L1": ("pair", {**MAIN, "layers": 1}),                             # thêm 1/2/3 lớp truyền tin GATv2
    "abl_L2": ("pair", {**MAIN, "layers": 2}),
    "abl_L3": ("pair", {**MAIN, "layers": 3}),
})
ABL = "pair_skip_mlp_specfeat," + ",".join(k for k in CONFIGS if k.startswith("abl_"))


def build_all(docs=None):
    """docs: dict tùy chọn, được điền {'cv': {id: kết quả trích xuất}, 'jd': {...}} (để dựng lại đồ thị khi kiểm tra diễn giải)."""
    cv, jd = load_texts()
    empty = {"level": None, "total_years": None, "items": []}
    ext = lambda t, kind: R._load().get(R._key(t, kind), empty)   # chỉ đọc cache: mọi lượt chạy dùng đúng cùng một tập cặp
    cvx = {k: ext(t, "CV") for k, t in cv.items()}
    jdx = {k: ext(t, "JD") for k, t in jd.items()}
    pairs = pd.read_csv(os.path.join(config.DATA_RAW_DIR, "pairs_labeled.csv"))
    if docs is not None:
        docs.update(cv=cvx, jd=jdx)
    emb, gs = Embedder(), []
    emb.encode(sorted({x["text"] for e in (*cvx.values(), *jdx.values()) for x in e["items"]}))  # mã hóa một lần (embedding mới)
    for r in pairs.itertuples():
        c, j = cvx[r.cv_id], jdx[r.jd_id]
        if c["items"] and j["items"]:
            g = build_pair_graph(c, j, emb, r.grade)
            g.cv_id, g.jd_id, g.grade = r.cv_id, r.jd_id, int(r.grade)
            gs.append(g)
    return gs


def maxsim_req(g):
    """MaxSim mức yêu cầu: trung bình có trọng số (bắt buộc 1, ưu tiên 0.5) của max cosine tới mục CV cùng loại."""
    ei, cos = g["req", "match", "item"].edge_index, g["req", "match", "item"].edge_attr.squeeze(-1)
    n = g["req"].x.size(0)
    m = torch.zeros(n)
    for r in range(n):
        v = cos[ei[0] == r]
        m[r] = v.max() if len(v) else 0.0
    w = torch.where(g["req"].x[:, -2] > 0.5, 1.0, 0.5)
    return float((m * w).sum() / w.sum())


def pair_loss(score, b, key="jd_id"):
    """RankNet theo từng truy vấn (mặc định JD; key='cv_id' khi mỗi CV xếp hạng các JD): cặp (tốt hơn, kém hơn) cùng truy vấn,
    phạt softplus(-(s_i - s_j)), trọng số = chênh nhãn."""
    q = getattr(b, key)
    ids = {j: i for i, j in enumerate(sorted(set(q)))}
    jd = torch.tensor([ids[j] for j in q])
    diff = b.y[:, None] - b.y[None, :]
    mask = (jd[:, None] == jd[None, :]) & (diff > 0)
    if not mask.any():
        return score.sum() * 0
    return (F.softplus(-(score[:, None] - score[None, :]))[mask] * diff[mask]).sum() / diff[mask].sum()


def jd_batches(L, k, shuffle, rng=None, key="jd_id"):
    """Gom đồ thị theo truy vấn (key) rồi ghép k truy vấn một batch, để loss xếp hạng có đủ cặp cùng truy vấn."""
    by = {}
    for g in L:
        by.setdefault(getattr(g, key), []).append(g)
    js = list(by)
    if shuffle:
        rng.shuffle(js)
    return [Batch.from_data_list([g for j in js[i:i + k] for g in by[j]]) for i in range(0, len(js), k)]


def val_ndcg(m, vb, key="jd_id"):
    """NDCG@10 trung bình theo truy vấn trên validation (chỉ truy vấn có >= 2 cặp và >= 1 cặp phù hợp)."""
    by = {}
    with torch.no_grad():
        for b in vb:
            for j, gr, s in zip(getattr(b, key), b.grade.tolist(), m(b).tolist()):
                by.setdefault(j, []).append((gr, s))
    v = [ndcg_at_k([a for a, _ in x], [s for _, s in x], 10) for x in by.values() if len(x) >= 2 and any(a >= 2 for a, _ in x)]
    return float(np.mean(v)) if v else float("nan")


def run(train, val, test, name, seed, dims, key="jd_id", ret_model=False):
    loss_kind, kw = CONFIGS[name]
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    m = ReqGNN(dims, **kw)
    lossf = (lambda m_, b: pair_loss(m_(b), b, key)) if loss_kind == "pair" else (lambda m_, b: F.binary_cross_entropy_with_logits(m_(b), b.y))
    vb = jd_batches(val, 16, False, key=key)
    opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-4)
    best, bad, state = 1e9, 0, None
    for _ in range(80):
        m.train()
        for b in jd_batches(train, 8, True, rng, key):
            opt.zero_grad()
            lossf(m, b).backward()
            opt.step()
        m.eval()
        with torch.no_grad():
            vloss = sum(lossf(m, b).item() for b in vb)
        if vloss < best - 1e-4:
            best, bad, state = vloss, 0, {k: v.clone() for k, v in m.state_dict().items()}
        else:
            bad += 1
            if bad >= 12:
                break
    m.load_state_dict(state)
    m.eval()
    vn = val_ndcg(m, vb, key)
    out = []
    with torch.no_grad():
        for b in jd_batches(test, 16, False):
            out += list(zip(b.cv_id, b.jd_id, m(b).tolist()))
    return (out, vn, m) if ret_model else (out, vn)


def splits(gs, protocol):
    """Trả về danh sách (fold_id, train_pool, test, hàm qid). Train_pool sẽ được tách tiếp 15% JD làm validation."""
    cvs = sorted({g.cv_id for g in gs})
    jds = sorted({g.jd_id for g in gs})
    shuf = lambda ids: np.random.default_rng(42).permutation(np.array(ids))
    if protocol == "jd":
        fold = {j: i for i, p in enumerate(np.array_split(shuf(jds), 5)) for j in p}
        return [(f, [g for g in gs if fold[g.jd_id] != f], [g for g in gs if fold[g.jd_id] == f]) for f in range(5)], lambda g: g.jd_id
    cg = {c: i for i, p in enumerate(np.array_split(shuf(cvs), 2)) for c in p}
    jg = {j: i for i, p in enumerate(np.array_split(shuf(jds), 5)) for j in p}
    out = []
    for a in range(2):
        for b in range(5):
            out.append((a * 5 + b, [g for g in gs if cg[g.cv_id] != a and jg[g.jd_id] != b],
                        [g for g in gs if cg[g.cv_id] == a and jg[g.jd_id] == b]))
    cell = {(g.cv_id, g.jd_id): cg[g.cv_id] * 5 + jg[g.jd_id] for g in gs}
    return out, lambda g: f"{cell[(g.cv_id, g.jd_id)]}|{g.jd_id}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("protocol", choices=["jd", "double"])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--tag", default="")
    ap.add_argument("--configs", default=",".join(CONFIGS))
    a = ap.parse_args()
    gs = build_all()
    dims = {k: gs[0][k].x.size(1) for k in ("req", "item", "spec")}
    folds, qf = splits(gs, a.protocol)
    rows, vrows = [], []
    for name in a.configs.split(","):
        for seed in range(a.seeds):
            for f, pool, test in folds:
                js = sorted({g.jd_id for g in pool})
                vj = set(np.random.default_rng(seed).choice(js, size=max(1, int(0.15 * len(js))), replace=False))
                tr, va = [g for g in pool if g.jd_id not in vj], [g for g in pool if g.jd_id in vj]
                out, vn = run(tr, va, test, name, seed, dims)
                vrows.append((name, seed, f, vn))
                q = {(g.cv_id, g.jd_id): qf(g) for g in test}
                rows += [(c, j, q[(c, j)], name, seed, s) for c, j, s in out]
            print("xong", name, "seed", seed, flush=True)
        pd.DataFrame(rows, columns=["cv_id", "jd_id", "qid", "config", "seed", "score"]).to_csv(os.path.join(RES, f"req_{a.protocol}{a.tag}.csv"), index=False)
        pd.DataFrame(vrows, columns=["config", "seed", "fold", "val_ndcg10"]).to_csv(os.path.join(RES, f"req_{a.protocol}{a.tag}_val.csv"), index=False)
    if DEFAULT_GRAPH:                                     # không ghi đè baseline MaxSim khi chạy ablation top-m/embedding
        ms = pd.DataFrame([(g.cv_id, g.jd_id, maxsim_req(g)) for g in gs], columns=["cv_id", "jd_id", "maxsim_req"])
        ms.to_csv(os.path.join(RES, "maxsim_req.csv"), index=False)
    print("đã lưu")
