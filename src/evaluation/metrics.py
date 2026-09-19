"""
Ranking metrics cho Candidate-Job Matching: NDCG@K, MRR, Recall@K.

Nhãn là mức độ phù hợp (graded relevance) theo thang 0..config.NUM_GRADES:
    0 = Không phù hợp, 1 = Liên quan ngành,
    2 = Phù hợp một phần, 3 = Phù hợp tốt

Mỗi "query" là một CV (hoặc một JD); model chấm điểm liên tục cho các JD
của query đó và xếp hạng. Các metric được tính per-query rồi lấy trung bình.

- NDCG@K  : dùng graded gain 2^grade - 1, discount log2(rank+1)
- Recall@K: tỉ lệ JD "relevant" (grade >= RELEVANT_GRADE) nằm trong top-K
- MRR     : nghịch đảo hạng của JD relevant đầu tiên
"""

import numpy as np

import config


def _ranked_grades(grades, scores) -> np.ndarray:
    """Trả về mảng grades sắp xếp theo score giảm dần."""
    grades = np.asarray(grades, dtype=float)
    scores = np.asarray(scores, dtype=float)
    return grades[np.argsort(-scores)]


def ndcg_at_k(grades, scores, k: int) -> float:
    """
    NDCG@K với graded gain: DCG = sum((2^rel_i - 1) / log2(i+1)).

    Query không có grade > 0 nào (IDCG = 0) trả về 0.0.
    """
    ranked = _ranked_grades(grades, scores)[:k]
    discounts = 1.0 / np.log2(np.arange(2, len(ranked) + 2))

    dcg = float(((2 ** ranked - 1) * discounts).sum())

    ideal = np.sort(np.asarray(grades, dtype=float))[::-1][:k]
    idcg = float(((2 ** ideal - 1) * discounts).sum())

    return dcg / idcg if idcg > 0 else 0.0


def recall_at_k(grades, scores, k: int, relevant_grade: int = None) -> float:
    """
    Recall@K: |top-K ∩ relevant| / |relevant|.

    Query không có JD nào relevant trả về None (bị loại khi lấy trung bình).
    """
    relevant_grade = config.RELEVANT_GRADE if relevant_grade is None else relevant_grade

    grades = np.asarray(grades, dtype=float)
    relevant = np.nonzero(grades >= relevant_grade)[0]
    if len(relevant) == 0:
        return None

    top_k = np.argsort(-np.asarray(scores, dtype=float))[:k]
    hits = len(set(top_k.tolist()) & set(relevant.tolist()))
    return hits / len(relevant)


def mrr(grades, scores, relevant_grade: int = None) -> float:
    """Mean Reciprocal Rank của JD relevant đầu tiên. Không có relevant → None."""
    relevant_grade = config.RELEVANT_GRADE if relevant_grade is None else relevant_grade

    ranked = _ranked_grades(grades, scores)
    for rank, grade in enumerate(ranked, start=1):
        if grade >= relevant_grade:
            return 1.0 / rank
    return None


def evaluate_ranking(query_groups: dict,
                     ks: list = None,
                     relevant_grade: int = None) -> dict:
    """
    Tính trung bình các ranking metrics trên tập query.

    Args:
        query_groups: dict {query_id: list[(grade, score)]} —
                      mỗi query là 1 CV với các JD được chấm điểm.
        ks: danh sách các K (mặc định config.RANKING_KS)
        relevant_grade: ngưỡng relevant (mặc định config.RELEVANT_GRADE)

    Returns:
        dict {"ndcg@1": ..., "ndcg@3": ..., "recall@1": ..., "mrr": ...,
              "num_queries": ..., "num_rankable_queries": ...}
    """
    ks = ks or config.RANKING_KS
    relevant_grade = config.RELEVANT_GRADE if relevant_grade is None else relevant_grade

    ndcg_vals = {k: [] for k in ks}
    recall_vals = {k: [] for k in ks}
    mrr_vals = []

    for qid, pairs in query_groups.items():
        if len(pairs) < 2:
            continue  # query chỉ có 1 JD thì không có ý nghĩa xếp hạng

        grades = [p[0] for p in pairs]
        scores = [p[1] for p in pairs]

        # NDCG: chỉ tính trên query có ít nhất 1 grade > 0
        if any(g > 0 for g in grades):
            for k in ks:
                ndcg_vals[k].append(ndcg_at_k(grades, scores, k))

        # Recall / MRR: chỉ tính trên query có JD relevant
        if any(g >= relevant_grade for g in grades):
            for k in ks:
                r = recall_at_k(grades, scores, k, relevant_grade)
                if r is not None:
                    recall_vals[k].append(r)
            mrr_vals.append(mrr(grades, scores, relevant_grade))

    result = {"num_queries": len(query_groups)}
    for k in ks:
        result[f"ndcg@{k}"] = float(np.mean(ndcg_vals[k])) if ndcg_vals[k] else None
        result[f"recall@{k}"] = float(np.mean(recall_vals[k])) if recall_vals[k] else None
    result["mrr"] = float(np.mean(mrr_vals)) if mrr_vals else None
    return result


def format_ranking_metrics(metrics: dict) -> str:
    """Định dạng dict metrics thành chuỗi bảng in ra terminal."""
    lines = []
    ndcg_parts = [f"NDCG@{k.split('@')[1]}={v:.4f}" for k, v in metrics.items()
                  if k.startswith("ndcg@") and v is not None]
    recall_parts = [f"Recall@{k.split('@')[1]}={v:.4f}" for k, v in metrics.items()
                    if k.startswith("recall@") and v is not None]
    mrr_val = metrics.get("mrr")
    if ndcg_parts:
        lines.append("  ".join(ndcg_parts))
    if recall_parts:
        lines.append("  ".join(recall_parts))
    if mrr_val is not None:
        lines.append(f"MRR={mrr_val:.4f}")
    if not lines:
        lines.append("(Không đủ query hợp lệ để tính ranking metrics)")
    return "\n".join(lines)


if __name__ == "__main__":
    # Sanity check: 1 CV với 5 JD, grade 0-3
    groups = {
        "cv_1": [(3, 0.9), (2, 0.6), (0, 0.8), (1, 0.2), (0, 0.1)],
        "cv_2": [(0, 0.3), (3, 0.7), (2, 0.95), (0, 0.05), (1, 0.4)],
    }
    result = evaluate_ranking(groups)
    print(f"Queries: {result['num_queries']}")
    print(format_ranking_metrics(result))
