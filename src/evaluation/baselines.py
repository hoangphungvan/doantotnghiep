"""
Baseline methods để so sánh với GCN / Hybrid Score (chỉ dùng ngữ nghĩa,
không khai thác cấu trúc đồ thị):

1. TF-IDF + cosine  — bag-of-words trên text thực thể (từ cv_entities/jd_entities
                      đã trích xuất) của CV và JD
2. SBERT + cosine   — semantic embedding thuần (chính là semantic_score
                      trong hybrid.py)

Đánh giá bằng cùng bộ ranking metrics (NDCG@K, MRR, Recall@K) trên cùng
tập validation (split theo nhóm CV, seed cố định → trùng với split khi train).

Chạy:
    python src/evaluation/baselines.py
"""

import json
import os
import sys
from collections import OrderedDict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Hỗ trợ chạy trực tiếp: python src/evaluation/baselines.py (từ thư mục gốc dự án)
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.evaluation.metrics import evaluate_ranking
from src.evaluation.hybrid import compute_semantic_scores, build_query_groups, print_comparison_table


def _entity_text(entities_json) -> str:
    """Ghép toàn bộ thực thể thành một chuỗi text để vector hóa."""
    if not entities_json:
        return ""
    try:
        ents = json.loads(entities_json)
    except (TypeError, json.JSONDecodeError):
        return ""
    return " ".join(str(item) for items in ents.values() for item in items)


def tfidf_cosine_scores(graphs: list) -> np.ndarray:
    """
    TF-IDF + cosine: fit TfidfVectorizer trên toàn bộ text (CV + JD) của
    tập đang xét, rồi tính cosine giữa vector của cặp (CV_i, JD_i).
    """
    cv_texts = [_entity_text(getattr(g, "cv_entities", None)) for g in graphs]
    jd_texts = [_entity_text(getattr(g, "jd_entities", None)) for g in graphs]

    if not any(t.strip() for t in cv_texts + jd_texts):
        print("[WARN] Graph không có thuộc tính cv_entities/jd_entities "
              "→ TF-IDF trả về điểm 0 cho tất cả.")
        return np.zeros(len(graphs), dtype=float)

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(cv_texts + jd_texts)
    cv_vecs, jd_vecs = matrix[:len(graphs)], matrix[len(graphs):]

    scores = [cosine_similarity(cv_vecs[i], jd_vecs[i])[0, 0]
              for i in range(len(graphs))]
    return np.array(scores, dtype=float)


def evaluate_baselines(graphs: list) -> OrderedDict:
    """Đánh giá 2 baseline trên danh sách graph, trả về OrderedDict metrics."""
    results = OrderedDict()
    results["TF-IDF + cosine"] = evaluate_ranking(
        build_query_groups(graphs, tfidf_cosine_scores(graphs)),
        ks=config.RANKING_KS)
    results["SBERT + cosine"] = evaluate_ranking(
        build_query_groups(graphs, compute_semantic_scores(graphs)),
        ks=config.RANKING_KS)
    return results


if __name__ == "__main__":
    from src.modeling.train import split_by_query
    from src.data_collection.prepare_training_data import load_all_graphs

    graphs = load_all_graphs()
    if not graphs:
        print("[ERROR] Chưa có dữ liệu graphs. Chạy prepare_training_data trước.")
        raise SystemExit(1)

    _, val_data = split_by_query(graphs)
    print(f"\n[Baselines] Đánh giá trên tập validation: {len(val_data)} cặp")
    print()
    print_comparison_table(evaluate_baselines(val_data))
