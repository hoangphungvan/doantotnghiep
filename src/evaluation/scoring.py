"""Các hàm điểm dùng chung cho realtime inference và offline evaluation."""

from __future__ import annotations

import numpy as np


def cosine_to_semantic_score(cosine):
    """Đưa cosine [-1, 1] về semantic score [0, 1]."""
    values = np.asarray(cosine, dtype=float)
    return np.clip((values + 1.0) / 2.0, 0.0, 1.0)


def combine_hybrid_score(graph_score, semantic_score, alpha: float):
    """Kết hợp graph score và semantic score theo cùng một công thức."""
    return alpha * np.asarray(graph_score, dtype=float) + (
        1.0 - alpha
    ) * np.asarray(semantic_score, dtype=float)
