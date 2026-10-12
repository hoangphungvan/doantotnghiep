"""
Mô hình xếp chồng: gộp điểm GCN (nắm chủ đề/vai trò) với đặc trưng LLM theo cặp (nắm độ phủ yêu cầu, điều kiện cứng,
chênh lệch kinh nghiệm), cosine SBERT toàn văn và cosine theo từng loại thực thể, bằng gradient boosting.

Chẩn đoán cho thấy GCN phân biệt tốt chủ đề (khác nghề / cùng nghề) nhưng không tách được mức 2-3 trong cùng nghề,
vì đầu vào của nó thiếu độ phủ yêu cầu; đặc trưng LLM bù đúng phần đó.

Thứ tự đặc trưng: 6 đặc trưng LLM (pair_features.FEATURE_NAMES) + 1 cosine toàn văn + 6 cosine theo loại thực thể
+ 1 điểm GCN. Khi huấn luyện, điểm GCN của mỗi cặp phải là điểm out-of-fold (mô hình GCN chưa thấy cặp đó).
"""

import os
import sys

import numpy as np
import torch
from sklearn.ensemble import HistGradientBoostingRegressor

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config


def _emb(g, i):
    return g.x[i, :g.x.shape[1] // 3].float()


def topic_features(graphs: list) -> np.ndarray:
    """Cosine SBERT giữa nút CV và nút JD (toàn văn) + cosine từng loại thực thể: (n, 1 + số loại thực thể)."""
    n = len(config.ENTITY_TYPES)
    cos = torch.nn.functional.cosine_similarity
    rows = [[float(cos(_emb(g, 0), _emb(g, 1), dim=0))]
            + [float(cos(_emb(g, 2 + k), _emb(g, 2 + n + k), dim=0)) for k in range(n)] for g in graphs]
    return np.array(rows, dtype=np.float32)


def build_features(graphs: list, gcn_scores) -> np.ndarray:
    """graphs cần có g_feat (đặc trưng LLM, shape (1, 6)); gcn_scores: điểm GCN tương ứng từng đồ thị."""
    pf = torch.cat([g.g_feat for g in graphs]).numpy()
    return np.hstack([pf, topic_features(graphs), np.asarray(gcn_scores, dtype=np.float32)[:, None]])


def make_stacker() -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_depth=4, random_state=0)


STACKER_FILE = os.path.join(config.MODEL_DIR, "stacker.pkl")


def predict_grade(score: float) -> int:
    """Stacker hồi quy trực tiếp trên grade 0..3 nên làm tròn là đủ (hiệu chỉnh ngưỡng không cải thiện thêm)."""
    return int(min(config.NUM_GRADES, max(0, round(float(score)))))


def train_final_stacker() -> None:
    """Huấn luyện stacker trên toàn bộ 1664 cặp. Điểm GCN dùng để huấn luyện là điểm out-of-fold
    (data/processed/cv_oof_predictions.csv, sinh bởi `train.py --cv 5`), đúng cách đã đánh giá."""
    import joblib
    import pandas as pd
    from src.data_collection.prepare_training_data import load_all_graphs
    from src.modeling.train import attach_pair_features

    graphs = load_all_graphs()
    attach_pair_features(graphs)
    oof = pd.read_csv(os.path.join(config.DATA_PROCESSED_DIR, "cv_oof_predictions.csv")).set_index(["cv_id", "jd_id"]).gcn_score
    scores = [oof[(g.cv_source, g.jd_source)] for g in graphs]
    model = make_stacker().fit(build_features(graphs, scores), [g.y.item() for g in graphs])
    joblib.dump(model, STACKER_FILE)
    print(f"[OK] Stacker lưu tại {STACKER_FILE} ({len(graphs)} cặp)")


if __name__ == "__main__":
    train_final_stacker()
