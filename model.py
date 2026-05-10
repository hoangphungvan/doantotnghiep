"""
GCN Model cho Candidate-Job Matching.

Kiến trúc:
1. Pre-aggregation: Linear projection từ input_dim -> hidden_dim
2. GCNConv layers với edge weights
3. Readout: Concatenate node embeddings của v_c và v_jd
4. Classification head: MLP -> single logit

Sử dụng BCEWithLogitsLoss với pos_weight để xử lý mất cân bằng lớp.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool
from torch_geometric.data import Data, Batch

import config


class PreAggregation(nn.Module):
    """Lớp Pre-aggregation: chiếu embedding về cùng hidden dimension."""

    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.linear = nn.Linear(input_dim, hidden_dim)
        self.norm = nn.LayerNorm(hidden_dim)
        self.activation = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(self.norm(self.linear(x)))


class GCNModel(nn.Module):
    """
    Graph Convolutional Network cho Candidate-Job Matching.

    Input: Đồ thị bipartite 14 nút
    Output: Logit score (match probability sau sigmoid)
    """

    def __init__(self, input_dim: int,
                 hidden_dim: int = None,
                 num_layers: int = None,
                 dropout: float = None):
        super().__init__()

        hidden_dim = hidden_dim or config.HIDDEN_DIM
        num_layers = num_layers or config.NUM_GCN_LAYERS
        dropout = dropout or config.DROPOUT

        self.pre_agg = PreAggregation(input_dim, hidden_dim)

        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()
        for _ in range(num_layers):
            self.convs.append(GCNConv(hidden_dim, hidden_dim))
            self.norms.append(nn.LayerNorm(hidden_dim))

        self.dropout = nn.Dropout(dropout)

        # v_c và v_jd concat -> 2 * hidden_dim
        # Thêm element-wise difference và product cho richer interaction
        classifier_input = hidden_dim * 4

        self.classifier = nn.Sequential(
            nn.Linear(classifier_input, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, data: Data) -> torch.Tensor:
        """
        Forward pass.

        Args:
            data: PyG Data object (single graph hoặc Batch)

        Returns:
            logits: (batch_size, 1) raw logits
        """
        x = data.x
        edge_index = data.edge_index
        edge_weight = data.edge_attr if hasattr(data, 'edge_attr') and data.edge_attr is not None else None

        x = self.pre_agg(x)

        for conv, norm in zip(self.convs, self.norms):
            residual = x
            x = conv(x, edge_index, edge_weight=edge_weight)
            x = norm(x)
            x = F.relu(x)
            x = self.dropout(x)
            x = x + residual  # residual connection

        batch_vec = getattr(data, 'batch', None)
        if batch_vec is not None:
            batch_size = batch_vec.max().item() + 1

            v_c_list = []
            v_jd_list = []
            for b in range(batch_size):
                mask = (batch_vec == b)
                nodes_in_graph = mask.nonzero(as_tuple=True)[0]
                v_c_list.append(x[nodes_in_graph[0]])
                v_jd_list.append(x[nodes_in_graph[1]])

            h_c = torch.stack(v_c_list)
            h_jd = torch.stack(v_jd_list)
        else:
            h_c = x[config.NODE_CANDIDATE].unsqueeze(0)
            h_jd = x[config.NODE_JD].unsqueeze(0)

        h_diff = h_c - h_jd
        h_prod = h_c * h_jd
        h_combined = torch.cat([h_c, h_jd, h_diff, h_prod], dim=-1)

        logits = self.classifier(h_combined)
        return logits

    def predict_proba(self, data: Data) -> torch.Tensor:
        """Trả về xác suất match sau sigmoid."""
        logits = self.forward(data)
        return torch.sigmoid(logits)


def get_loss_fn(pos_weight: float = None) -> nn.BCEWithLogitsLoss:
    """
    Tạo loss function BCEWithLogitsLoss với pos_weight.

    pos_weight=10 vì dữ liệu có ~95% negative (bị loại),
    giúp model không "lười" predict toàn negative.
    """
    pw = pos_weight or config.POS_WEIGHT
    return nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor([pw])
    )


if __name__ == "__main__":
    import numpy as np
    from graph_builder import build_graph

    feat_dim = 384 * 3
    np.random.seed(42)

    c_main = np.random.randn(feat_dim)
    c_ents = {e: np.random.randn(feat_dim) for e in config.ENTITY_TYPES}
    j_main = np.random.randn(feat_dim)
    j_ents = {e: np.random.randn(feat_dim) for e in config.ENTITY_TYPES}

    data = build_graph(c_main, c_ents, j_main, j_ents, label=1.0)

    model = GCNModel(input_dim=feat_dim)
    print(f"Model:\n{model}")
    print(f"\nTotal parameters: {sum(p.numel() for p in model.parameters()):,}")

    logits = model(data)
    prob = torch.sigmoid(logits)
    print(f"\nLogits: {logits.item():.4f}")
    print(f"Probability: {prob.item():.4f}")

    loss_fn = get_loss_fn()
    loss = loss_fn(logits.squeeze(), data.y)
    print(f"Loss: {loss.item():.4f}")
