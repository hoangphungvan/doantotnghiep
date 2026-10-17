"""
Self-check pair_features.to_vector (không gọi LLM). Chạy: python tests/test_pair_features.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extraction.pair_features import to_vector

raw = {"requirements": [{"text": "a", "met": True}, {"text": "b", "met": False}, {"text": "c", "met": True}, {"text": "d", "met": True}],
       "conditions": [{"text": "đại học", "met": False}, {"text": "IELTS", "met": True}],
       "jd_min_years": 3, "cv_years": 1, "title_tech_in_cv": False}
v = to_vector(raw)
assert v["pf_coverage"] == 0.75 and v["pf_n_req"] == 4 and v["pf_hard_missing"] == 1
assert abs(v["pf_years_gap"] - 2 / 6) < 1e-9 and v["pf_title_tech_missing"] == 1 and v["pf_valid"] == 1

assert to_vector({})["pf_valid"] == 0                                   # LLM lỗi/bỏ sót
empty = to_vector({"requirements": []})                                  # JD không nêu yêu cầu chuyên môn
assert empty["pf_valid"] == 1 and empty["pf_coverage"] == 0.5 and empty["pf_n_req"] == 0
assert to_vector({"requirements": [{"met": True}], "title_tech_in_cv": None})["pf_title_tech_missing"] == 0
print("pair_features self-checks passed")
