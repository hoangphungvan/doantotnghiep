"""
Module xây dựng đồ thị Bipartite Graph cho cặp Candidate-JD.

Cấu trúc đồ thị (14 nút):
- Node 0: Candidate (v_c)
- Node 1: Job Description (v_jd)
- Nodes 2-7: Candidate entities (soft_skills, hard_skills, education,
             field_of_education, industry_sector, role)
- Nodes 8-13: JD entities (tương tự)

Kết nối Star Topology + k-NN cross-edges.
Trọng số cạnh: cosine similarity^p (sharpening).
"""

import numpy as np
import torch
from torch_geometric.data import Data

import config


def build_star_edges() -> list[tuple[int, int]]:
    """
    Tạo danh sách cạnh theo Star Topology.

    Cạnh:
    - v_c <-> mỗi entity node của candidate (0 <-> 2..7)
    - v_jd <-> mỗi entity node của JD (1 <-> 8..13)
    - v_c <-> v_jd (0 <-> 1)
    """
    edges = []

    for i in range(config.NUM_ENTITY_TYPES):
        node_idx = config.CANDIDATE_ENTITY_START + i
        edges.append((config.NODE_CANDIDATE, node_idx))
        edges.append((node_idx, config.NODE_CANDIDATE))

    for i in range(config.NUM_ENTITY_TYPES):
        node_idx = config.JD_ENTITY_START + i
        edges.append((config.NODE_JD, node_idx))
        edges.append((node_idx, config.NODE_JD))

    edges.append((config.NODE_CANDIDATE, config.NODE_JD))
    edges.append((config.NODE_JD, config.NODE_CANDIDATE))

    return edges


def compute_cosine_similarity(features: torch.Tensor) -> torch.Tensor:
    """Tính cosine similarity matrix giữa tất cả các nút."""
    norms = features.norm(dim=1, keepdim=True).clamp(min=1e-8)
    normalized = features / norms
    sim_matrix = torch.mm(normalized, normalized.t())
    return sim_matrix


def build_knn_edges(features: torch.Tensor, k: int = None) -> tuple[list[tuple[int, int]], list[float]]:
    """
    Xây dựng cạnh dựa trên k-NN với sharpening.

    Với mỗi nút, chọn k láng giềng gần nhất dựa trên cosine similarity.
    Trọng số = sim^p (sharpening coefficient).
    """
    k = k or config.KNN_K
    p = config.SHARPENING_P
    num_nodes = features.shape[0]
    k = min(k, num_nodes - 1)

    sim_matrix = compute_cosine_similarity(features)

    edges = []
    weights = []

    for i in range(num_nodes):
        sims = sim_matrix[i].clone()
        sims[i] = -1  # exclude self-loop

        topk_vals, topk_idx = torch.topk(sims, k)

        sharpened = torch.clamp(topk_vals, min=0) ** p
        norm_factor = sharpened.sum()
        if norm_factor > 0:
            sharpened = sharpened / norm_factor

        for j_idx, w in zip(topk_idx.tolist(), sharpened.tolist()):
            edges.append((i, j_idx))
            weights.append(w)

    return edges, weights


def merge_edges(star_edges: list[tuple[int, int]],
                knn_edges: list[tuple[int, int]],
                knn_weights: list[float],
                base_weight: float = 1.0) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Hợp nhất cạnh Star Topology và k-NN, loại bỏ trùng lặp.
    Star edges nhận trọng số base_weight.
    k-NN edges sử dụng trọng số đã tính.
    """
    edge_dict = {}

    for src, dst in star_edges:
        edge_dict[(src, dst)] = base_weight

    for (src, dst), w in zip(knn_edges, knn_weights):
        key = (src, dst)
        if key in edge_dict:
            edge_dict[key] = max(edge_dict[key], w)
        else:
            edge_dict[key] = w

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


def build_graph(candidate_main_feat: np.ndarray,
                candidate_entity_feats: dict,
                jd_main_feat: np.ndarray,
                jd_entity_feats: dict,
                label: float = None) -> Data:
    """
    Xây dựng một đồ thị PyG Data cho cặp Candidate-JD.

    Args:
        candidate_main_feat: Feature vector cho nút Candidate
        candidate_entity_feats: dict[entity_type -> feature_vector]
        jd_main_feat: Feature vector cho nút JD
        jd_entity_feats: dict[entity_type -> feature_vector]
        label: 1.0 = match, 0.0 = không match

    Returns:
        torch_geometric.data.Data object
    """
    node_features = []

    node_features.append(candidate_main_feat)  # Node 0
    node_features.append(jd_main_feat)          # Node 1

    for etype in config.ENTITY_TYPES:
        feat = candidate_entity_feats.get(etype, np.zeros_like(candidate_main_feat))
        node_features.append(feat)  # Nodes 2-7

    for etype in config.ENTITY_TYPES:
        feat = jd_entity_feats.get(etype, np.zeros_like(jd_main_feat))
        node_features.append(feat)  # Nodes 8-13

    x = torch.tensor(np.array(node_features), dtype=torch.float)

    star_edges = build_star_edges()

    knn_edges, knn_weights = build_knn_edges(x, k=config.KNN_K)

    edge_index, edge_weight = merge_edges(star_edges, knn_edges, knn_weights)

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
    c_entities = {e: np.random.randn(feat_dim) for e in config.ENTITY_TYPES}
    j_main = np.random.randn(feat_dim)
    j_entities = {e: np.random.randn(feat_dim) for e in config.ENTITY_TYPES}

    graph = build_graph(c_main, c_entities, j_main, j_entities, label=1.0)
    print(f"Graph: {graph}")
    print(f"  Nodes: {graph.num_nodes}, Features: {graph.x.shape}")
    print(f"  Edges: {graph.edge_index.shape[1]}")
    print(f"  Edge weights range: [{graph.edge_attr.min():.4f}, {graph.edge_attr.max():.4f}]")
    print(f"  Label: {graph.y}")
