"""
Hybrid Score: kết hợp điểm ngữ nghĩa (Semantic) và điểm đồ thị (GNN).

    Hybrid Score = α · graph_score + (1 − α) · semantic_score

Trong đó:
- graph_score    : sigmoid output của GCN model ∈ [0,1] — khai thác cấu trúc
                   quan hệ ứng viên – kỹ năng – công việc
- semantic_score : cosine similarity giữa SBERT embedding của CV và JD,
                   chuẩn hóa min-max về [0,1] theo tập tune
- α              : hệ số trộn, tune trên tập validation tối đa hóa NDCG@K
                   (grid 0..1, bước 0.05)

Semantic score lấy trực tiếp từ đồ thị: node 0 (Candidate) và node 1 (JD)
lưu SBERT embedding của toàn bộ text thực thể ở embedding_dim chiều đầu
(feature vector 3*embedding_dim là zero-padding), nên không cần encode lại.

Chạy trên dữ liệu thật đã chuẩn bị:
    python src/evaluation/hybrid.py
Alpha cố định:
    python src/evaluation/hybrid.py --alpha 0.7
Demo end-to-end với sample data (không cần API key):
    python main.py --mode hybrid
"""

import argparse
import os
import sys
from collections import OrderedDict

import numpy as np
import torch
from torch_geometric.loader import DataLoader

# Hỗ trợ chạy trực tiếp: python src/evaluation/hybrid.py (từ thư mục gốc dự án)
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.evaluation.metrics import evaluate_ranking
from src.modeling.model import GCNModel
from src.modeling.train import get_query_id


# ---------------------------------------------------------------------------
# Component scores
# ---------------------------------------------------------------------------

def compute_semantic_scores(graphs: list) -> np.ndarray:
    """
    Semantic score = cosine similarity giữa SBERT embedding của CV và JD.

    Đọc trực tiếp từ node 0 và node 1 của đồ thị (384 chiều đầu là SBERT
    embedding của text thực thể gộp, phần còn lại là zero padding).
    emb_dim suy ra từ input_dim // 3 để không phụ thuộc model embedding.
    """
    scores = []
    for g in graphs:
        input_dim = g.x.shape[1]
        if input_dim % 3 != 0:
            raise ValueError(
                f"Feature dim {input_dim} không chia hết cho 3 — "
                "đồ thị không được build từ pipeline (3*embedding_dim)."
            )
        emb_dim = input_dim // 3
        cv_emb = g.x[0, :emb_dim].float()
        jd_emb = g.x[1, :emb_dim].float()
        cos = torch.nn.functional.cosine_similarity(cv_emb, jd_emb, dim=0)
        scores.append(float(cos))
    return np.array(scores, dtype=float)


@torch.no_grad()
def compute_graph_scores(model: GCNModel, graphs: list,
                         device: torch.device = None,
                         batch_size: int = 64) -> np.ndarray:
    """Graph score = sigmoid output của GCN cho từng cặp (CV, JD)."""
    if not graphs:
        return np.array([], dtype=float)
    model.eval()
    if device is None:
        device = next(model.parameters()).device

    loader = DataLoader(graphs, batch_size=batch_size, shuffle=False)
    out = []
    for batch in loader:
        batch = batch.to(device)
        logits = model(batch).squeeze(-1)
        out.append(torch.sigmoid(logits).cpu())
    return torch.cat(out).numpy().astype(float)


# ---------------------------------------------------------------------------
# Fusion & tuning
# ---------------------------------------------------------------------------

def _minmax_fit(values: np.ndarray):
    """Tạo hàm chuẩn hóa min-max về [0,1] từ min/max của tập tune."""
    lo, hi = float(values.min()), float(values.max())

    def apply(v: np.ndarray) -> np.ndarray:
        if hi - lo < 1e-9:
            return np.zeros_like(v, dtype=float)
        return np.clip((np.asarray(v, dtype=float) - lo) / (hi - lo), 0.0, 1.0)

    return apply


def build_query_groups(graphs: list, scores: np.ndarray) -> dict:
    """Group (grade, score) theo CV để tính ranking metrics."""
    groups = {}
    for g, s in zip(graphs, scores):
        qid = get_query_id(g)
        if qid is None:
            continue
        groups.setdefault(qid, []).append((g.y.item(), float(s)))
    return groups


def tune_alpha(graphs: list, graph_scores: np.ndarray,
               semantic_scores: np.ndarray,
               ndcg_k: int = 10, grid: np.ndarray = None) -> tuple:
    """
    Tune α trên tập validation: chọn α maximize NDCG@K.

    Trả về (best_alpha, metrics_tại_α_tốt_nhất).
    Nếu không tune được (thiếu query hợp lệ) → trả về (0.5, None).
    """
    normalize = _minmax_fit(semantic_scores)
    semantic_norm = normalize(semantic_scores)
    grid = np.linspace(0.0, 1.0, 21) if grid is None else grid

    best_alpha, best_metrics, best_score = 0.5, None, -1.0
    for alpha in grid:
        blended = alpha * graph_scores + (1.0 - alpha) * semantic_norm
        metrics = evaluate_ranking(build_query_groups(graphs, blended),
                                   ks=config.RANKING_KS)
        # Ưu tiên NDCG@ndcg_k; nếu không có thì lấy NDCG@K đầu tiên khả dụng
        target = metrics.get(f"ndcg@{ndcg_k}")
        if target is None:
            target = next((m for k, m in metrics.items()
                           if k.startswith("ndcg@") and m is not None), None)
        if target is not None and target > best_score:
            best_score, best_alpha, best_metrics = target, float(alpha), metrics

    if best_metrics is None:
        print("[WARN] Không tune được α (thiếu query hợp lệ) → dùng α = 0.5")
        return 0.5, None
    return best_alpha, best_metrics


# ---------------------------------------------------------------------------
# Comparison: baselines vs GCN vs Hybrid
# ---------------------------------------------------------------------------

def print_comparison_table(results: OrderedDict):
    """In bảng so sánh các phương pháp theo ranking metrics."""
    ks = config.RANKING_KS
    headers = (["Phương pháp"]
               + [f"ndcg@{k}" for k in ks] + [f"recall@{k}" for k in ks]
               + ["mrr"])

    def fmt(v):
        return f"{v:.4f}" if v is not None else "  —  "

    rows = []
    for name, m in results.items():
        rows.append([name]
                    + [fmt(m.get(f"ndcg@{k}")) for k in ks]
                    + [fmt(m.get(f"recall@{k}")) for k in ks]
                    + [fmt(m.get("mrr"))])

    widths = [max(len(r[i]) for r in [headers] + rows) for i in range(len(headers))]
    line = "-+-".join("-" * w for w in widths)

    def render(row):
        return " | ".join(str(c).ljust(w) for c, w in zip(row, widths))

    print(render(headers))
    print(line)
    for row in rows:
        print(render(row))


def run_comparison(graphs: list, model: GCNModel = None,
                   model_path: str = None, alpha="auto",
                   ndcg_k: int = 10, device: torch.device = None,
                   verbose: bool = True) -> OrderedDict:
    """
    So sánh trên tập validation (split theo nhóm CV, seed cố định —
    trùng với split khi huấn luyện):

        1. TF-IDF + cosine      (baseline bag-of-words)
        2. SBERT + cosine       (baseline semantic thuần)
        3. GCN (graph only)     (graph_score)
        4. Hybrid Score         (α·graph + (1−α)·semantic, α = "auto" → tune)

    Trả về OrderedDict {tên phương pháp: metrics dict}.
    """
    from src.modeling.train import split_by_query
    from src.evaluation.baselines import tfidf_cosine_scores

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if model is None:
        model_path = model_path or os.path.join(config.MODEL_DIR, "best_model.pt")
        checkpoint = torch.load(model_path, weights_only=False, map_location=device)
        model = GCNModel(input_dim=checkpoint["input_dim"]).to(device)
        model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)

    _, val_data = split_by_query(graphs)

    tfidf_scores = tfidf_cosine_scores(val_data)
    semantic_raw = compute_semantic_scores(val_data)
    graph_scores = compute_graph_scores(model, val_data, device)

    normalize = _minmax_fit(semantic_raw)
    semantic_norm = normalize(semantic_raw)

    results = OrderedDict()
    results["TF-IDF + cosine"] = evaluate_ranking(
        build_query_groups(val_data, tfidf_scores), ks=config.RANKING_KS)
    results["SBERT + cosine"] = evaluate_ranking(
        build_query_groups(val_data, semantic_raw), ks=config.RANKING_KS)
    results["GCN (graph only)"] = evaluate_ranking(
        build_query_groups(val_data, graph_scores), ks=config.RANKING_KS)

    if alpha == "auto":
        alpha_used, hybrid_metrics = tune_alpha(
            val_data, graph_scores, semantic_raw, ndcg_k=ndcg_k)
    else:
        alpha_used = float(alpha)
        blended = alpha_used * graph_scores + (1.0 - alpha_used) * semantic_norm
        hybrid_metrics = evaluate_ranking(
            build_query_groups(val_data, blended), ks=config.RANKING_KS)
    results[f"Hybrid (α={alpha_used:.2f})"] = hybrid_metrics

    if verbose:
        num_queries = len(build_query_groups(val_data, graph_scores))
        print(f"\n[Hybrid] Đánh giá trên tập validation: {len(val_data)} cặp, "
              f"{num_queries} query CV")
        print(f"[Hybrid] α = {alpha_used:.2f}"
              + (f" (tune theo NDCG@{ndcg_k})" if alpha == "auto" else " (cố định)"))
        print()
        print_comparison_table(results)
        print("\n[Lưu ý] α được tune và số liệu báo cáo trên cùng tập validation. "
              "Cho báo cáo khóa luận nên giữ một tập test riêng để số liệu khách quan.")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hybrid Score: GCN + SBERT cosine")
    parser.add_argument("--model", type=str, default=None,
                        help="Đường dẫn model GCN đã train (mặc định models/best_model.pt)")
    parser.add_argument("--alpha", type=str, default="auto",
                        help="'auto' để tune theo NDCG@K, hoặc số trong [0,1]")
    parser.add_argument("--ndcg-k", type=int, default=10,
                        help="K dùng làm mục tiêu khi tune α (mặc định 10)")
    args = parser.parse_args()

    from src.data_collection.prepare_training_data import load_all_graphs

    graphs = load_all_graphs()
    if not graphs:
        print("[ERROR] Chưa có dữ liệu graphs. Chạy prepare_training_data trước.")
        raise SystemExit(1)

    alpha_val = "auto" if args.alpha == "auto" else float(args.alpha)
    run_comparison(graphs, model_path=args.model, alpha=alpha_val,
                   ndcg_k=args.ndcg_k)
