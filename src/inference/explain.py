"""
Diễn giải kết quả ghép CV–JD (Explainability).

Hai nguồn giải thích:
1. Đối chiếu thực thể: kỹ năng nào khớp (chuỗi hoặc ngữ nghĩa), JD còn thiếu gì, CV thừa gì.
2. Đóng góp của node GCN: đặt feature từng node về 0 rồi đo mức thay đổi điểm (occlusion).

Lưu ý: phần 1 là đối chiếu thực thể, không phải giải thích trọng số của GCN.
Phần 2 là xấp xỉ: zero feature của node làm đồ thị lệch khỏi phân bố lúc huấn luyện.
"""

import re

import numpy as np
import torch

import config

ENTITY_LABELS = {
    "soft_skills": ("Kỹ năng mềm", "Soft skills"),
    "hard_skills": ("Kỹ năng chuyên môn", "Hard skills"),
    "education": ("Học vấn", "Education"),
    "field_of_education": ("Ngành học", "Field of education"),
    "industry_sector": ("Lĩnh vực", "Industry sector"),
    "role": ("Vị trí", "Role"),
}


def _norm(text) -> str:
    return re.sub(r"\s+", " ", str(text).strip().lower())


def _unique(items) -> list:
    return list(dict.fromkeys(str(x).strip() for x in (items or []) if str(x).strip()))


def match_entities(cv_entities: dict, jd_entities: dict,
                   embedding_gen=None, threshold: float = None) -> dict:
    """
    Ghép thực thể CV với JD theo từng loại.

    Ưu tiên khớp chuỗi (không phân biệt hoa thường), sau đó khớp ngữ nghĩa
    bằng cosine của embedding nếu có embedding_gen. Mỗi mục chỉ được ghép một lần.

    Trả về {etype: {matched, missing, extra, coverage}, "weighted_coverage": float|None}.
    matched là danh sách (cv_item, jd_item, similarity).
    """
    threshold = config.SEMANTIC_MATCH_THRESHOLD if threshold is None else threshold
    result = {}
    cov_by_type = {}

    for etype in config.ENTITY_TYPES:
        cv_items = _unique(cv_entities.get(etype))
        jd_items = _unique(jd_entities.get(etype))
        matched, used_cv, used_jd = [], set(), set()

        cv_index = {}
        for i, item in enumerate(cv_items):
            cv_index.setdefault(_norm(item), i)
        for j, item in enumerate(jd_items):
            i = cv_index.get(_norm(item))
            if i is not None and i not in used_cv:
                matched.append((cv_items[i], item, 1.0))
                used_cv.add(i)
                used_jd.add(j)

        rest_cv = [i for i in range(len(cv_items)) if i not in used_cv]
        rest_jd = [j for j in range(len(jd_items)) if j not in used_jd]
        if embedding_gen is not None and rest_cv and rest_jd:
            ce = embedding_gen.encode([cv_items[i] for i in rest_cv])
            je = embedding_gen.encode([jd_items[j] for j in rest_jd])
            ce = ce / (np.linalg.norm(ce, axis=1, keepdims=True) + 1e-12)
            je = je / (np.linalg.norm(je, axis=1, keepdims=True) + 1e-12)
            sim = ce @ je.T
            # Ghép tham lam theo độ tương đồng giảm dần, mỗi mục một lần
            order = np.argsort(-sim, axis=None)
            for flat in order:
                a, b = divmod(int(flat), len(rest_jd))
                s = float(sim[a, b])
                if s < threshold:
                    break
                i, j = rest_cv[a], rest_jd[b]
                if i in used_cv or j in used_jd:
                    continue
                matched.append((cv_items[i], jd_items[j], s))
                used_cv.add(i)
                used_jd.add(j)

        coverage = len(matched) / len(jd_items) if jd_items else None
        cov_by_type[etype] = coverage
        result[etype] = {
            "matched": matched,
            "missing": [jd_items[j] for j in range(len(jd_items)) if j not in used_jd],
            "extra": [cv_items[i] for i in range(len(cv_items)) if i not in used_cv],
            "coverage": coverage,
        }

    weights = {e: config.ENTITY_WEIGHTS[e] for e, c in cov_by_type.items() if c is not None}
    total_w = sum(weights.values())
    result["weighted_coverage"] = (
        sum(weights[e] * cov_by_type[e] for e in weights) / total_w if total_w else None
    )
    return result


NODE_NAMES = (["cv_main", "jd_main"]
              + [f"cv:{e}" for e in config.ENTITY_TYPES]
              + [f"jd:{e}" for e in config.ENTITY_TYPES])


@torch.no_grad()
def gcn_attribution(model, data) -> dict:
    """
    Occlusion: đặt feature của từng node về 0, đo mức giảm điểm sigmoid.
    Giá trị dương = node đang đẩy điểm lên; âm = node đang kéo điểm xuống.
    """
    model.eval()
    base = torch.sigmoid(model(data)).item()
    out = {}
    for node, name in enumerate(NODE_NAMES):
        occluded = data.clone()
        occluded.x = data.x.clone()
        occluded.x[node] = 0
        out[name] = base - torch.sigmoid(model(occluded)).item()
    return out


def summarize(match: dict, attribution: dict = None, top_k: int = 3) -> dict:
    """Tạo diễn giải song ngữ {"vi": str, "en": str} từ kết quả match_entities và gcn_attribution."""
    lines = {"vi": [], "en": []}

    wc = match["weighted_coverage"]
    if wc is not None:
        lines["vi"].append(f"Mức phủ yêu cầu JD (theo trọng số): {wc:.0%}.")
        lines["en"].append(f"JD requirement coverage (weighted): {wc:.0%}.")

    for etype in config.ENTITY_TYPES:
        info = match[etype]
        if info["coverage"] is None:
            continue
        vi_name, en_name = ENTITY_LABELS[etype]
        n_jd = len(info["matched"]) + len(info["missing"])
        pairs = ", ".join(
            f"{c} ≈ {j}" if _norm(c) != _norm(j) else c for c, j, _ in info["matched"]
        )
        missing = ", ".join(info["missing"])
        extra = ", ".join(info["extra"])
        lines["vi"].append(
            f"{vi_name}: khớp {len(info['matched'])}/{n_jd}"
            f"{' (' + pairs + ')' if pairs else ''}. "
            f"Thiếu: {missing or 'không có'}. Thừa: {extra or 'không có'}."
        )
        lines["en"].append(
            f"{en_name}: matched {len(info['matched'])}/{n_jd}"
            f"{' (' + pairs + ')' if pairs else ''}. "
            f"Missing: {missing or 'none'}. Extra: {extra or 'none'}."
        )

    if attribution:
        ranked = sorted(attribution.items(), key=lambda kv: kv[1], reverse=True)
        top_pos = [f"{n} ({v:+.3f})" for n, v in ranked[:top_k] if v > 0]
        top_neg = [f"{n} ({v:+.3f})" for n, v in ranked[::-1][:top_k] if v < 0]
        lines["vi"].append("Node đẩy điểm lên: " + (", ".join(top_pos) or "không có") + ".")
        lines["vi"].append("Node kéo điểm xuống: " + (", ".join(top_neg) or "không có") + ".")
        lines["en"].append("Nodes raising the score: " + (", ".join(top_pos) or "none") + ".")
        lines["en"].append("Nodes lowering the score: " + (", ".join(top_neg) or "none") + ".")

    return {"vi": "\n".join(lines["vi"]), "en": "\n".join(lines["en"])}
