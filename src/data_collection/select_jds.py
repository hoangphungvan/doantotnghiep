"""
Chọn JD phân tầng từ VietJobs_cntt.csv (dữ liệu thật) để ghép với CV.

Cách chọn không dùng ngẫu nhiên, kết quả luôn giống nhau giữa các lần chạy:
1. Lọc JD đủ chất lượng (có tiêu đề, phần yêu cầu, văn bản >= MIN_TEXT_LEN ký tự),
   bỏ JD trùng (cùng tiêu đề + kỹ năng).
2. Với mỗi cụm trong jd_clusters.csv: sắp theo (nhóm kinh nghiệm, khoảng cách tới tâm cụm)
   rồi lấy k vị trí cách đều. Nhờ vậy mỗi cụm có đủ JD từ trung tâm tới rìa và đủ mức kinh nghiệm.

Chạy:
    python src/data_collection/select_jds.py                  # 9 JD/cụm x 20 cụm = 180 JD
    python src/data_collection/select_jds.py --per-cluster 12
Kết quả: data/raw/selected_jds.csv (cột jd_brief là bản rút gọn để dán vào ChatGPT).
"""

import argparse
import ast
import os
import re
import sys

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config

CLUSTERS_CSV = os.path.join(config.DATA_PROCESSED_DIR, "jd_clusters.csv")
OUT_CSV = os.path.join(config.DATA_RAW_DIR, "selected_jds.csv")
MIN_TEXT_LEN = 400
REQ_BRIEF_CHARS = 800


def parse_exp_years(text) -> float:
    """'2 năm' -> 2.0, '6 tháng' -> 0.5, 'Không yêu cầu' hoặc lạ -> 0.0."""
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(năm|tháng)", str(text).strip().lower())
    if not m:
        return 0.0
    n = float(m.group(1).replace(",", "."))
    return n if m.group(2) == "năm" else n / 12


def exp_bucket(years: float) -> int:
    return 0 if years == 0 else 1 if years <= 1 else 2 if years <= 3 else 3


def pick_evenly(df: pd.DataFrame, k: int) -> pd.DataFrame:
    """Lấy k dòng cách đều trên df đã sắp xếp (xác định, không ngẫu nhiên)."""
    if len(df) <= k:
        return df
    return df.iloc[np.linspace(0, len(df) - 1, k).round().astype(int)]


def _clean(value) -> str:
    """Chuỗi sạch; cột dạng "['a', 'b']" được đổi thành "a, b"."""
    s = str(value).strip()
    if s in ("nan", "[]"):
        return ""
    if s.startswith("["):
        try:
            items = ast.literal_eval(s)
            if isinstance(items, list):
                return ", ".join(str(x).strip() for x in items if str(x).strip())
        except (ValueError, SyntaxError):
            pass
    return s


def build_brief(row) -> str:
    parts = [
        f"Vị trí: {_clean(row['job_title'])}",
        f"Kinh nghiệm: {_clean(row['experience_required'])}",
        f"Học vấn: {_clean(row['qualifications'])}",
        f"Kỹ năng chuyên môn: {_clean(row['technical_skills'])}",
        f"Yêu cầu: {_clean(row['requirements_text'])[:REQ_BRIEF_CHARS]}",
    ]
    return "\n".join(p for p in parts if not p.endswith(": "))


def select_jds(jds: pd.DataFrame, clusters: pd.DataFrame, per_cluster: int) -> pd.DataFrame:
    df = jds.merge(clusters[["jd_id", "cluster_id", "cluster_name", "distance_to_centroid"]],
                   on="jd_id", how="inner").sort_values("jd_id")

    ok = (df["job_title"].map(_clean) != "") \
        & (df["requirements_text"].map(_clean) != "") \
        & (df["formatted_jd_text"].astype(str).str.len() >= MIN_TEXT_LEN)
    df = df[ok]

    key = df["job_title"].map(_clean).str.lower() + "|" + df["technical_skills"].map(_clean).str.lower()
    df = df[~key.duplicated(keep="first")].copy()

    df["exp_years"] = df["experience_required"].map(parse_exp_years)
    df["exp_bucket"] = df["exp_years"].map(exp_bucket)

    picked = [
        pick_evenly(g.sort_values(["exp_bucket", "distance_to_centroid", "jd_id"]), per_cluster)
        for _, g in df.groupby("cluster_id")
    ]
    out = pd.concat(picked).sort_values(["cluster_id", "jd_id"])
    out["jd_brief"] = out.apply(build_brief, axis=1)
    return out[["jd_id", "cluster_id", "cluster_name", "job_title", "experience_required",
                "exp_years", "jd_brief"]]


def main():
    parser = argparse.ArgumentParser(description="Chọn JD phân tầng từ dữ liệu thật")
    parser.add_argument("--per-cluster", type=int, default=9)
    parser.add_argument("--out", default=OUT_CSV)
    args = parser.parse_args()

    jds = pd.read_csv(config.VIETJOBS_IT_CSV)
    clusters = pd.read_csv(CLUSTERS_CSV)
    out = select_jds(jds, clusters, args.per_cluster)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")

    print(f"[OK] {len(out)} JD -> {args.out}")
    print(out.groupby("cluster_id").size().rename("so_JD").to_string())
    print("Phân bố kinh nghiệm (năm):", out["exp_years"].describe()[["min", "50%", "max"]].round(2).to_dict())


if __name__ == "__main__":
    main()
