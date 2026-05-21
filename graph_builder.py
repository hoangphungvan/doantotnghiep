"""
Module xây dựng đồ thị Bipartite Graph cho cặp Candidate-JD.

Cấu trúc đồ thị (14 nút):
- Node 0: Candidate (v_c)
- Node 1: Job Description (v_jd)
- Nodes 2-7: Candidate entities (soft_skills, hard_skills, education,
             field_of_education, industry_sector, role)  — theo thứ tự ENTITY_TYPES
- Nodes 8-13: JD entities (tương tự)

Loại cạnh:
1. Star edges       : v_c ↔ entity_candidate, v_jd ↔ entity_jd  (trọng số = ENTITY_WEIGHTS)
2. Cross edges      : entity_candidate[i] ↔ entity_jd[i]  (cùng loại, trọng số = cosine_sim * weight)
3. Bridge edge      : v_c ↔ v_jd  (trọng số = 1.0)

Cross-edges cho phép GCN so sánh trực tiếp từng loại entity giữa CV và JD,
thay vì chỉ thông qua 1 cạnh v_c-v_jd duy nhất.
"""

import numpy as np
import torch
from torch_geometric.data import Data

import config


# ---------------------------------------------------------------------------
# Edge builders
# ---------------------------------------------------------------------------

def build_star_edges() -> tuple[list[tuple[int, int]], list[float]]:
    """
    Cạnh hình sao v_c ↔ entity_candidate và v_jd ↔ entity_jd.
    Trọng số = ENTITY_WEIGHTS theo loại entity (cả 2 chiều).
    """
    edges, weights = [], []
    for i, etype in enumerate(config.ENTITY_TYPES):
        w = config.ENTITY_WEIGHTS[etype]

        c_node = config.CANDIDATE_ENTITY_START + i
        edges.append((config.NODE_CANDIDATE, c_node))
        weights.append(w)
        edges.append((c_node, config.NODE_CANDIDATE))
        weights.append(w)

        jd_node = config.JD_ENTITY_START + i
        edges.append((config.NODE_JD, jd_node))
        weights.append(w)
        edges.append((jd_node, config.NODE_JD))
        weights.append(w)

    # Bridge edge v_c ↔ v_jd
    edges.append((config.NODE_CANDIDATE, config.NODE_JD))
    weights.append(1.0)
    edges.append((config.NODE_JD, config.NODE_CANDIDATE))
    weights.append(1.0)

    return edges, weights


def build_cross_entity_edges(features: torch.Tensor) -> tuple[list[tuple[int, int]], list[float]]:
    """
    Cạnh ngang nối trực tiếp entity_candidate[i] ↔ entity_jd[i] (cùng loại).
    Trọng số = cosine_similarity * ENTITY_WEIGHTS[etype].

    Điều này cho phép GCN thấy rõ: role CV có giống role JD không?
    hard_skills CV có khớp hard_skills JD không? — thay vì phải suy luận gián tiếp.
    """
    edges, weights = [], []

    norms = features.norm(dim=1, keepdim=True).clamp(min=1e-8)
    normalized = features / norms

    for i, etype in enumerate(config.ENTITY_TYPES):
        c_node = config.CANDIDATE_ENTITY_START + i
        jd_node = config.JD_ENTITY_START + i

        cos_sim = float(torch.dot(normalized[c_node], normalized[jd_node]).clamp(min=0.0))
        w = cos_sim * config.ENTITY_WEIGHTS[etype]

        # Chỉ thêm cạnh nếu có tín hiệu tương đồng > 0
        if w > 0.0:
            edges.append((c_node, jd_node))
            weights.append(w)
            edges.append((jd_node, c_node))
            weights.append(w)

    return edges, weights


def build_knn_edges(features: torch.Tensor,
                    k: int = None) -> tuple[list[tuple[int, int]], list[float]]:
    """
    k-NN edges giữa tất cả các nút.
    Trọng số = (cosine_sim)^p, chuẩn hóa theo hàng (sharpening).
    Bổ sung cho cross-edges bằng cách nắm bắt tương đồng không kỳ vọng.
    """
    k = k or config.KNN_K
    p = config.SHARPENING_P
    num_nodes = features.shape[0]
    k = min(k, num_nodes - 1)

    norms = features.norm(dim=1, keepdim=True).clamp(min=1e-8)
    sim_matrix = torch.mm(features / norms, (features / norms).t())

    edges, weights = [], []
    for i in range(num_nodes):
        sims = sim_matrix[i].clone()
        sims[i] = -1.0

        topk_vals, topk_idx = torch.topk(sims, k)
        sharpened = torch.clamp(topk_vals, min=0.0) ** p
        norm_factor = sharpened.sum()
        if norm_factor > 0:
            sharpened = sharpened / norm_factor

        for j_idx, w in zip(topk_idx.tolist(), sharpened.tolist()):
            edges.append((i, j_idx))
            weights.append(w)

    return edges, weights


def merge_edges(
    star_edges:   list[tuple[int, int]],
    star_weights: list[float],
    cross_edges:  list[tuple[int, int]],
    cross_weights: list[float],
    knn_edges:    list[tuple[int, int]],
    knn_weights:  list[float],
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Hợp nhất tất cả loại cạnh.
    Ưu tiên: star/cross (semantic) > kNN (structural).
    Nếu cùng cạnh, lấy giá trị lớn nhất.
    """
    edge_dict: dict[tuple[int, int], float] = {}

    # kNN trước (priority thấp nhất)
    for (s, d), w in zip(knn_edges, knn_weights):
        edge_dict[(s, d)] = w

    # Cross-entity edges (priority trung bình)
    for (s, d), w in zip(cross_edges, cross_weights):
        key = (s, d)
        edge_dict[key] = max(edge_dict.get(key, 0.0), w)

    # Star edges (priority cao nhất — luôn có mặt)
    for (s, d), w in zip(star_edges, star_weights):
        key = (s, d)
        edge_dict[key] = max(edge_dict.get(key, 0.0), w)

    if not edge_dict:
        return torch.zeros(2, 0, dtype=torch.long), torch.zeros(0)

    src_list, dst_list, weight_list = [], [], []
    for (s, d), w in edge_dict.items():
        src_list.append(s)
        dst_list.append(d)
        weight_list.append(w)

    edge_index = torch.tensor([src_list, dst_list], dtype=torch.long)
    edge_weight = torch.tensor(weight_list, dtype=torch.float)
    return edge_index, edge_weight


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_graph(candidate_main_feat: np.ndarray,
                candidate_entity_feats: dict,
                jd_main_feat: np.ndarray,
                jd_entity_feats: dict,
                label: float = None) -> Data:
    """
    Xây dựng đồ thị PyG Data cho một cặp Candidate-JD.

    Nodes (14):
        0: Candidate,  1: JD
        2-7: CV entities (thứ tự ENTITY_TYPES)
        8-13: JD entities (thứ tự ENTITY_TYPES)

    Edges:
        Star  : v_c/v_jd ↔ entity nodes (ENTITY_WEIGHTS)
        Cross : entity_cv[i] ↔ entity_jd[i] (cosine_sim * ENTITY_WEIGHTS)
        kNN   : k nearest neighbors toàn đồ thị
    """
    node_features = []
    node_features.append(candidate_main_feat)   # Node 0: v_c
    node_features.append(jd_main_feat)           # Node 1: v_jd

    for etype in config.ENTITY_TYPES:            # Nodes 2-7: CV entities
        feat = candidate_entity_feats.get(etype, np.zeros_like(candidate_main_feat))
        node_features.append(feat)

    for etype in config.ENTITY_TYPES:            # Nodes 8-13: JD entities
        feat = jd_entity_feats.get(etype, np.zeros_like(jd_main_feat))
        node_features.append(feat)

    x = torch.tensor(np.array(node_features), dtype=torch.float)

    star_edges,  star_weights  = build_star_edges()
    cross_edges, cross_weights = build_cross_entity_edges(x)
    knn_edges,   knn_weights   = build_knn_edges(x, k=config.KNN_K)

    edge_index, edge_weight = merge_edges(
        star_edges, star_weights,
        cross_edges, cross_weights,
        knn_edges, knn_weights,
    )

    data = Data(
        x=x,
        edge_index=edge_index,
        edge_attr=edge_weight,
        num_nodes=config.NUM_NODES,
    )
    if label is not None:
        data.y = torch.tensor([label], dtype=torch.float)

    return data


if __name__ == "__main__":
    np.random.seed(42)
    feat_dim = 384 * 3

    c_main = np.random.randn(feat_dim)
    c_ents = {e: np.random.randn(feat_dim) for e in config.ENTITY_TYPES}
    j_main = np.random.randn(feat_dim)
    j_ents = {e: np.random.randn(feat_dim) for e in config.ENTITY_TYPES}

    graph = build_graph(c_main, c_ents, j_main, j_ents, label=1.0)
    print(f"Graph: {graph}")
    print(f"  Nodes: {graph.num_nodes}, Features: {graph.x.shape}")
    print(f"  Edges: {graph.edge_index.shape[1]}")
    print(f"  Edge weight range: [{graph.edge_attr.min():.4f}, {graph.edge_attr.max():.4f}]")
    print(f"\nEntity weights (star edges):")
    for etype in config.ENTITY_TYPES:
        print(f"  {etype}: {config.ENTITY_WEIGHTS[etype]}")
