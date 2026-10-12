"""
Self-check pair_features.to_vector và stacker.build_features (không gọi LLM). Chạy: python tests/test_pair_features.py
"""

import os
import sys

import numpy as np
import torch
from torch_geometric.data import Data

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.extraction.pair_features import FEATURE_NAMES, to_vector
from src.modeling.stacker import build_features, predict_grade

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

d = 8
x = torch.rand(config.NUM_NODES, 3 * d)
g = Data(x=x, g_feat=torch.tensor([[v[n] for n in FEATURE_NAMES]], dtype=torch.float32))
feats = build_features([g, g], [0.3, 0.9])
assert feats.shape == (2, len(FEATURE_NAMES) + 1 + len(config.ENTITY_TYPES) + 1), feats.shape
assert np.allclose(feats[:, -1], [0.3, 0.9])

assert [predict_grade(s) for s in (-0.4, 0.49, 0.51, 1.5, 2.6, 3.7)] == [0, 0, 1, 2, 3, 3]
print("all pair_features/stacker self-checks passed")
