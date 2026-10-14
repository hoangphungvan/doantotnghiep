"""
Self-check cho src/inference/explain.py. Chạy: python tests/test_explain.py
"""

import os
import sys

import numpy as np
import torch
from torch_geometric.data import Data

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.inference.explain import gcn_attribution, match_entities, recruiter_summary, summarize, NODE_NAMES


class FakeEmbedder:
    """Trả vector cố định theo text, để kiểm tra khớp ngữ nghĩa không cần SBERT."""

    def __init__(self, table):
        self.table = table

    def encode(self, texts):
        return np.array([self.table[t] for t in texts], dtype=float)


def _empty():
    return {e: [] for e in config.ENTITY_TYPES}


def test_exact_match_case_insensitive():
    cv = _empty() | {"hard_skills": ["Python", "Docker"]}
    jd = _empty() | {"hard_skills": ["python", "Kubernetes"]}
    m = match_entities(cv, jd)
    h = m["hard_skills"]
    assert [(c, j) for c, j, _ in h["matched"]] == [("Python", "python")]
    assert h["missing"] == ["Kubernetes"]
    assert h["extra"] == ["Docker"]
    assert h["coverage"] == 0.5


def test_semantic_match_and_threshold():
    table = {"ML": [1.0, 0.0], "Machine Learning": [0.9, 0.1],
             "Docker": [0.0, 1.0], "Cooking": [-1.0, 0.0]}  # Cooking đối nghĩa, không được khớp
    cv = _empty() | {"hard_skills": ["ML", "Docker"]}
    jd = _empty() | {"hard_skills": ["Machine Learning", "Cooking"]}
    m = match_entities(cv, jd, FakeEmbedder(table))["hard_skills"]
    assert [(c, j) for c, j, _ in m["matched"]] == [("ML", "Machine Learning")]
    assert m["missing"] == ["Cooking"]
    assert m["extra"] == ["Docker"]


def test_one_to_one_assignment():
    table = {"ML": [1.0, 0.0], "AI": [0.99, 0.01], "Machine Learning": [1.0, 0.0]}
    cv = _empty() | {"hard_skills": ["ML", "AI"]}
    jd = _empty() | {"hard_skills": ["Machine Learning"]}
    m = match_entities(cv, jd, FakeEmbedder(table))["hard_skills"]
    assert [(c, j) for c, j, _ in m["matched"]] == [("ML", "Machine Learning")]
    assert m["extra"] == ["AI"]


def test_empty_jd_gives_no_coverage():
    cv = _empty() | {"hard_skills": ["Python"]}
    m = match_entities(cv, _empty())
    assert m["hard_skills"]["coverage"] is None
    assert m["weighted_coverage"] is None


def test_weighted_coverage_uses_entity_weights():
    cv = _empty() | {"role": ["Engineer"], "soft_skills": []}
    jd = _empty() | {"role": ["Engineer"], "soft_skills": ["Teamwork"]}
    m = match_entities(cv, jd)
    w_role, w_soft = config.ENTITY_WEIGHTS["role"], config.ENTITY_WEIGHTS["soft_skills"]
    expected = (w_role * 1.0 + w_soft * 0.0) / (w_role + w_soft)
    assert abs(m["weighted_coverage"] - expected) < 1e-9


def test_gcn_attribution_sign():
    class SumModel(torch.nn.Module):
        def forward(self, data):
            return data.x.sum().reshape(1, 1)

    x = torch.zeros(len(NODE_NAMES), 4)
    x[config.NODE_JD] = 1.0  # node JD chính đẩy logit lên
    data = Data(x=x, edge_index=torch.zeros(2, 0, dtype=torch.long))
    attr = gcn_attribution(SumModel(), data)
    assert len(attr) == len(NODE_NAMES) == 14
    assert attr["jd_main"] > 0
    assert attr["cv_main"] == 0


def test_recruiter_summary():
    llm = {"requirements": [{"text": "Python", "met": True}, {"text": "SQL", "met": True}, {"text": "Spark", "met": False}],
           "conditions": [{"text": "IELTS 6.0", "met": False}], "jd_min_years": 2, "cv_years": 0.5, "title_tech_in_cv": False}
    s = recruiter_summary(2, llm)
    assert "Phù hợp một phần" in s["vi"] and "2/3" in s["vi"]
    assert "Đáp ứng (2/3" in s["vi"] and "Spark" in s["vi"].split("Chưa thấy trong CV:")[1]
    assert "IELTS 6.0" in s["vi"] and "2 năm" in s["vi"] and "0.5 năm" in s["vi"] and "tiêu đề" in s["vi"]
    assert "Partial match" in s["en"] and "Not found in CV: Spark" in s["en"]
    assert "Cần lưu ý" not in recruiter_summary(3, {"requirements": [{"text": "Python", "met": True}], "jd_min_years": 1, "cv_years": 3})["vi"]
    assert "chưa có kinh nghiệm liên quan" in recruiter_summary(1, {"requirements": [{"text": "a", "met": False}], "jd_min_years": 3, "cv_years": 0})["vi"]
    many = {"requirements": [{"text": f"kỹ năng {i}", "met": False} for i in range(9)]}
    assert "và 3 mục khác" in recruiter_summary(0, many)["vi"]
    fallback = recruiter_summary(1, None, match_entities({"hard_skills": ["Python"]}, {"hard_skills": ["Python", "Java"]}))
    assert "Ước lượng nhanh" in fallback["vi"] and "Java" in fallback["vi"]


def test_summarize_bilingual():
    cv = _empty() | {"hard_skills": ["Python"]}
    jd = _empty() | {"hard_skills": ["Python", "Docker"]}
    text = summarize(match_entities(cv, jd), {"jd_main": 0.2, "cv:hard_skills": -0.1})
    assert "Docker" in text["vi"] and "Docker" in text["en"]
    assert "Node đẩy điểm lên" in text["vi"] and "Nodes raising" in text["en"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all explain self-checks passed")
