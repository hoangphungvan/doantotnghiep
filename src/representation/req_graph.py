"""
Đồ thị MỨC YÊU CẦU cho mỗi cặp (CV, JD) (HeteroData), thay cho đồ thị 14 nút gộp nhóm.

Nút:
  req   — mỗi yêu cầu của JD:  [embedding | one-hot loại(5) | bắt buộc(1) | số năm tối thiểu/10]
  item  — mỗi mục của CV:      [embedding | one-hot loại(5) | số năm thực tế/10]
  spec  — 4 nút đặc biệt cố định: (cấp độ JD, cấp độ CV, số năm JD, số năm CV), đặc trưng [loại(2) | bên(2) | giá trị | thiếu]
Cạnh:
  (req -match-> item) và chiều ngược: nối yêu cầu với mục CV CÙNG LOẠI, thuộc tính = cosine; mỗi yêu cầu chỉ giữ top-m (M_TOP)
  (spec -cmp-> spec): JD→CV cho cấp độ và cho số năm; thuộc tính = [chênh JD−CV, max(0, JD−CV)] để phạt khi CV thấp hơn JD
Chuẩn hóa ESCO (tùy chọn, REQ_ESCO=<ngưỡng>): xem src/representation/esco.py.
Embedding: mô hình đa ngữ mạnh hơn MiniLM (mặc định BAAI/bge-m3), cache theo văn bản trong data/cache/req_emb_<tên>.npz.
"""

import os
import re

import numpy as np
import torch
from torch_geometric.data import HeteroData

import config
from src.extraction.requirement_extractor import ITEM_TYPES, LEVELS
from src.representation.esco import esco_text

EMB_MODEL = os.getenv("REQ_EMB_MODEL", "BAAI/bge-m3")
M_TOP = int(os.getenv("REQ_M_TOP", "3"))     # ablation top-m: đặt biến môi trường trước khi import
ESCO_TAU = float(os.getenv("REQ_ESCO", "0"))  # > 0: thay mục hard/soft skill bằng nhãn ESCO khi độ giống >= ngưỡng (src/representation/esco.py)
DEFAULT_GRAPH = "REQ_M_TOP" not in os.environ and "REQ_EMB_MODEL" not in os.environ and not ESCO_TAU
YEAR_SCALE = 10.0
_model = None
_store = None


def _cache_path():
    return os.path.join(config.DATA_CACHE_DIR, "req_emb_" + re.sub(r"\W+", "_", EMB_MODEL) + ".npz")


class Embedder:
    """encode(list[str]) -> ma trận chuẩn hóa; nhớ vector theo văn bản."""

    def __init__(self):
        p = _cache_path()
        self.vec = {}
        if os.path.exists(p):
            z = np.load(p, allow_pickle=True)
            self.vec = dict(zip(z["keys"].tolist(), z["vecs"]))

    def encode(self, texts):
        global _model
        miss = sorted({t for t in texts if t not in self.vec})
        if miss:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer(EMB_MODEL)
                _model.max_seq_length = 128  # mỗi mục chỉ là cụm từ ngắn
            v = _model.encode(miss, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
            self.vec.update(zip(miss, v.astype(np.float32)))
            np.savez(_cache_path(), keys=np.array(list(self.vec), dtype=object), vecs=np.stack(list(self.vec.values())))
        return np.stack([self.vec[t] for t in texts]) if texts else np.zeros((0, 1024), np.float32)


def _onehot(t):
    v = np.zeros(len(ITEM_TYPES), np.float32)
    v[ITEM_TYPES.index(t)] = 1
    return v


def _spec(kind, side, val, scale):
    miss = val is None
    return np.array([kind == 0, kind == 1, side == 0, side == 1, 0.0 if miss else val / scale, float(miss)], np.float32)


def build_pair_graph(cv: dict, jd: dict, emb: Embedder, grade=None, m_top: int = M_TOP) -> HeteroData:
    """cv, jd: kết quả extract_requirements. Mỗi bên cần ≥1 mục."""
    ri, ci = jd["items"], cv["items"]
    txt = (lambda x: esco_text(x["text"], x["type"], ESCO_TAU, EMB_MODEL)) if ESCO_TAU else (lambda x: x["text"])
    er, ec = emb.encode([txt(x) for x in ri]), emb.encode([txt(x) for x in ci])
    d = HeteroData()
    d["req"].x = torch.from_numpy(np.hstack([er, np.stack([np.concatenate([_onehot(x["type"]), [float(x["required"]), (x["years"] or 0) / YEAR_SCALE]]) for x in ri]).astype(np.float32)]))
    d["item"].x = torch.from_numpy(np.hstack([ec, np.stack([np.concatenate([_onehot(x["type"]), [(x["years"] or 0) / YEAR_SCALE]]) for x in ci]).astype(np.float32)]))
    lvl = lambda L: None if L is None else float(LEVELS.index(L))
    jl, cl, jy, cy = lvl(jd["level"]), lvl(cv["level"]), jd["total_years"], cv["total_years"]
    d["spec"].x = torch.from_numpy(np.stack([_spec(0, 0, jl, len(LEVELS) - 1), _spec(0, 1, cl, len(LEVELS) - 1), _spec(1, 0, jy, YEAR_SCALE), _spec(1, 1, cy, YEAR_SCALE)]))

    sim = er @ ec.T
    same = np.array([[a["type"] == b["type"] for b in ci] for a in ri]) if ci else np.zeros((len(ri), 0), bool)
    src, dst, w = [], [], []
    for r in range(len(ri)):
        idx = np.where(same[r])[0]
        for k in idx[np.argsort(-sim[r, idx])][:m_top]:
            src.append(r), dst.append(int(k)), w.append(float(sim[r, k]))
    ei = torch.tensor([src, dst], dtype=torch.long).reshape(2, -1)
    ea = torch.tensor(w, dtype=torch.float32).reshape(-1, 1)
    d["req", "match", "item"].edge_index, d["req", "match", "item"].edge_attr = ei, ea
    d["item", "rev_match", "req"].edge_index, d["item", "rev_match", "req"].edge_attr = ei.flip(0), ea

    # Cạnh NGỮ CẢNH (chỉ mô hình ctx dùng; coverage vẫn tính trên 'match'): thông tin mà điểm từng cạnh đơn lẻ không thấy được.
    def put(rel, s, t, a):
        d[rel].edge_index = torch.tensor([s, t], dtype=torch.long).reshape(2, -1)
        d[rel].edge_attr = torch.tensor(a, dtype=torch.float32).reshape(-1, 1)

    def within(e, k=3):                                   # top-k láng giềng cosine trong cùng văn bản (không tự nối)
        s, t, a = [], [], []
        S = e @ e.T
        for i in range(len(e)):
            for j in [j for j in np.argsort(-S[i]) if j != i][:k]:
                s.append(int(j)), t.append(i), a.append(float(S[i, j]))
        return s, t, a
    put(("req", "ctx", "req"), *within(er))
    put(("item", "ctx", "item"), *within(ec))
    s, t, a = [], [], []                                  # bằng chứng khác loại: top-m mục CV bất kể loại
    for r in range(len(ri)):
        for k in np.argsort(-sim[r])[:m_top]:
            s.append(r), t.append(int(k)), a.append(float(sim[r, k]))
    put(("req", "any", "item"), s, t, a)
    put(("item", "rev_any", "req"), t, s, a)
    put(("spec", "jd_ctx", "req"), [0] * len(ri) + [2] * len(ri), list(range(len(ri))) * 2, [1.0] * (2 * len(ri)))
    put(("spec", "cv_ctx", "item"), [1] * len(ci) + [3] * len(ci), list(range(len(ci))) * 2, [1.0] * (2 * len(ci)))

    gap = lambda j, c: 0.0 if j is None or c is None else (j - c)
    gl, gy = gap(jl, cl) / (len(LEVELS) - 1), gap(jy, cy) / YEAR_SCALE
    d["spec", "cmp", "spec"].edge_index = torch.tensor([[0, 2], [1, 3]], dtype=torch.long)
    d["spec", "cmp", "spec"].edge_attr = torch.tensor([[gl, max(0.0, gl)], [gy, max(0.0, gy)]], dtype=torch.float32)
    if grade is not None:
        d.y = torch.tensor([grade / config.NUM_GRADES], dtype=torch.float32)
    return d
