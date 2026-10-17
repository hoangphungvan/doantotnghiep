"""
Self-check bộ nhãn: mỗi cặp duy nhất, nhãn trong thang, CV/JD tồn tại.
Chạy: python tests/test_dataset_labels.py
"""

import glob
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.data_collection.prepare_training_data import load_pairs

pairs = load_pairs()  # tự báo lỗi nếu trùng cặp hoặc nhãn ngoài thang
jds = set(pd.read_csv(os.path.join(config.DATA_RAW_DIR, "selected_jds.csv")).jd_id)

assert set(pairs.jd_id) <= jds, "JD không có trong selected_jds.csv"
missing = [c for c in pairs.cv_id.unique() if not glob.glob(os.path.join(config.DATA_RAW_DIR, "cvs_synth", f"{c}.*"))]
assert not missing, f"thiếu file CV: {missing}"
assert set(pairs.grade.unique()) == {0, 1, 2, 3}, "thiếu một mức nhãn"
print(f"OK: {len(pairs)} pairs, {pairs.cv_id.nunique()} CV, {pairs.jd_id.nunique()} JD")
