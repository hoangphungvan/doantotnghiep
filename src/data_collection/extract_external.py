"""
Trích xuất mức yêu cầu (schema r1) cho bộ dữ liệu ngoài cnamuangtoun/resume-job-description-fit (train + test).
Ghi cache định kỳ (mỗi 100 văn bản) và chạy lại các văn bản còn rỗng tối đa --passes lượt.
Chạy: python src/data_collection/extract_external.py [--limit N] [--passes 4]
"""
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from src.extraction import requirement_extractor as R

D = os.path.join(config.DATA_RAW_DIR, "cnamuangtoun")


def load():
    df = pd.concat([pd.read_csv(os.path.join(D, f"{s}.csv")) for s in ("train", "test")])
    return ([(t, "CV") for t in sorted(df.resume_text.unique())] + [(t, "JD") for t in sorted(df.job_description_text.unique())])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    todo = load()
    todo = todo[: a.limit] if a.limit else todo
    print("tổng văn bản:", len(todo), flush=True)
    for p in range(a.passes):
        cache = R._load()
        miss = [x for x in todo if R._key(x[0], x[1]) not in cache]
        print(f"lượt {p}: còn {len(miss)} văn bản chưa có", flush=True)
        if not miss:
            break
        with ThreadPoolExecutor(a.workers) as ex:
            for i in range(0, len(miss), 100):
                list(ex.map(lambda x: R.extract_requirements(*x), miss[i:i + 100]))
                R.save_cache()
                print(f"  đã xử lý {min(i + 100, len(miss))}/{len(miss)}", flush=True)
    cache = R._load()
    print("xong, còn thiếu:", sum(R._key(t, k) not in cache for t, k in todo))
