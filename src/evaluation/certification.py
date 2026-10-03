"""Điểm thưởng chứng chỉ cho cặp Candidate-JD."""

import json

import numpy as np

import config


def certification_match_ratio(candidate_entities: dict, jd_entities: dict) -> float:
    """Tính tỷ lệ chứng chỉ JD yêu cầu mà CV đang có.

    Nếu JD không yêu cầu chứng chỉ hoặc không có chứng chỉ trùng nhau,
    kết quả bằng 0 và điểm nền được giữ nguyên.
    """
    candidate_certs = set((candidate_entities or {}).get("certifications", []))
    jd_certs = set((jd_entities or {}).get("certifications", []))
    if not jd_certs:
        return 0.0
    return len(candidate_certs & jd_certs) / len(jd_certs)


def apply_certification_bonus(base_score: float, match_ratio: float) -> float:
    """Cộng thưởng chứng chỉ, không thay đổi điểm khi không liên quan."""
    bonus = config.CERTIFICATION_SCORE_BONUS * max(0.0, min(1.0, match_ratio))
    return min(1.0, float(base_score) + bonus)


def certification_bonus_for_graph(graph) -> float:
    """Lấy điểm thưởng từ metadata entity được lưu trong PyG Data."""
    stored_ratio = getattr(graph, "certification_match_ratio", None)
    if stored_ratio is not None:
        try:
            return config.CERTIFICATION_SCORE_BONUS * float(stored_ratio[0])
        except (TypeError, IndexError, KeyError):
            pass

    try:
        cv_entities = json.loads(getattr(graph, "cv_entities", "{}"))
        jd_entities = json.loads(getattr(graph, "jd_entities", "{}"))
    except (TypeError, json.JSONDecodeError):
        return 0.0

    ratio = certification_match_ratio(cv_entities, jd_entities)
    return config.CERTIFICATION_SCORE_BONUS * ratio


def apply_certification_bonus_to_scores(graphs: list, scores):
    """Áp dụng bonus theo từng graph cho mảng graph scores."""
    bonuses = [certification_bonus_for_graph(graph) for graph in graphs]
    return np.asarray(scores, dtype=float) + np.asarray(bonuses, dtype=float)
