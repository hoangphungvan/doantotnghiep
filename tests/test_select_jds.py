"""
Self-check cho src/data_collection/select_jds.py. Chạy: python tests/test_select_jds.py
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection.select_jds import exp_bucket, parse_exp_years, pick_evenly, select_jds

LONG = "x" * 500


def _jd(i, title=None, exp="2 năm", skills="Java", req="yêu cầu", text=LONG):
    return {"jd_id": f"jd_{i:04d}", "job_title": title or f"Dev {i}", "experience_required": exp,
            "qualifications": "ĐH", "technical_skills": skills, "requirements_text": req,
            "formatted_jd_text": text}


def _clusters(ids, cid=0):
    return pd.DataFrame({"jd_id": ids, "cluster_id": cid, "cluster_name": "c",
                         "distance_to_centroid": [i * 0.1 for i in range(len(ids))]})


def test_parse_exp_years():
    assert parse_exp_years("2 năm") == 2
    assert parse_exp_years("6 tháng") == 0.5
    assert parse_exp_years("Không yêu cầu") == 0
    assert [exp_bucket(x) for x in (0, 0.5, 2, 5)] == [0, 1, 2, 3]


def test_clean_turns_list_strings_into_text():
    from src.data_collection.select_jds import _clean
    assert _clean("['Java', 'SQL']") == "Java, SQL"
    assert _clean("[]") == "" and _clean(float("nan")) == ""
    assert _clean("[chưa đóng") == "[chưa đóng"  # chuỗi lỗi giữ nguyên, không văng exception


def test_pick_evenly_spans_whole_range():
    df = pd.DataFrame({"v": range(10)})
    assert pick_evenly(df, 4)["v"].tolist() == [0, 3, 6, 9]
    assert len(pick_evenly(df, 20)) == 10  # ít hơn k thì lấy hết


def test_filters_dedupes_and_is_deterministic():
    rows = [_jd(i) for i in range(1, 9)]
    rows.append(_jd(9, title="Dev 1", skills="Java"))          # trùng tiêu đề + kỹ năng với jd_0001
    rows.append(_jd(10, text="ngắn"))                          # văn bản quá ngắn
    rows.append(_jd(11, req=""))                               # thiếu phần yêu cầu
    jds = pd.DataFrame(rows)
    cl = _clusters(jds["jd_id"].tolist())
    a = select_jds(jds, cl, per_cluster=4)
    b = select_jds(jds.sample(frac=1, random_state=1), cl, per_cluster=4)
    assert a["jd_id"].tolist() == b["jd_id"].tolist()          # không phụ thuộc thứ tự đầu vào
    assert len(a) == 4
    assert not {"jd_0009", "jd_0010", "jd_0011"} & set(a["jd_id"])
    assert "Vị trí: " in a["jd_brief"].iloc[0]


def test_each_cluster_gets_its_quota():
    jds = pd.DataFrame([_jd(i) for i in range(1, 13)])
    cl = pd.concat([_clusters(jds["jd_id"][:6].tolist(), 0), _clusters(jds["jd_id"][6:].tolist(), 1)])
    out = select_jds(jds, cl, per_cluster=3)
    assert out.groupby("cluster_id").size().tolist() == [3, 3]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all select_jds self-checks passed")
