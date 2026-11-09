"""
Trích xuất mức yêu cầu (schema r1) cho toàn bộ CV và JD của bộ dữ liệu có nhãn, ghi vào data/cache/req_cache.json.
Chạy:  python src/data_collection/extract_requirements_all.py [--limit N]
"""

import argparse
import glob
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from src.extraction import requirement_extractor as R

RAW = config.DATA_RAW_DIR


def load_texts():
    pairs = pd.read_csv(os.path.join(RAW, "pairs_labeled.csv"), usecols=["cv_id", "jd_id"])
    jds = pd.read_csv(os.path.join(RAW, "selected_jds.csv")).set_index("jd_id").jd_brief
    cv = {c: Path(glob.glob(os.path.join(RAW, "cvs_synth", f"{c}.*"))[0]).read_text(encoding="utf-8") for c in sorted(pairs.cv_id.unique())}
    jd = {j: str(jds[j]) for j in sorted(pairs.jd_id.unique())}
    return cv, jd


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    cv, jd = load_texts()
    todo = [(t, "CV") for t in cv.values()] + [(t, "JD") for t in jd.values()]
    todo = todo[: a.limit] if a.limit else todo
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda x: R.extract_requirements(*x), todo))
    R.save_cache()
    empty = sum(1 for r in res if not r["items"])
    print(f"xong {len(todo)} văn bản, rỗng: {empty}")
