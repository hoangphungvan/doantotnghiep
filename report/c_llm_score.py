"""
Baseline LLM chấm điểm trực tiếp (nhận xét của cô): LLM đọc nguyên văn JD và CV rồi cho mức 0-3 và điểm 0-100, nhiệt độ 0.
Không huấn luyện, không thấy nhãn. Prompt dùng đúng thang 0-3 mô tả bộ nhãn (README), xếp hạng theo điểm 0-100.
Chạy: python report/c_llm_score.py [own|ext] [--model gemini-3.5-flash-lite] [--workers 2]
      (có cache data/cache/llm_score_cache.json: hết hạn mức thì chạy lại để chấm tiếp phần còn thiếu)
Ra:   thêm cột 'llm|<model>' (điểm 0-100) và 'llmgrade|<model>' (mức 0-3) vào report/results/static_scores.csv (own)
      hoặc ext_cna_static.csv (ext: chỉ các JD đủ điều kiện đánh giá, cặp khác để trống)
"""
import argparse
import hashlib
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
import config
from src.data_collection.extract_requirements_all import load_texts
from src.extraction import entity_extractor as E
from src.extraction.entity_extractor import _call_llm

E.RETRY_WAIT_SECONDS = 30                                 # giới hạn theo phút của Gemini: chờ lâu hơn mặc định 10 s

RES = os.path.join(ROOT, "report", "results")
CACHE = os.path.join(config.DATA_CACHE_DIR, "llm_score_cache.json")
VERSION = "v1"
SYSTEM = """Bạn là chuyên viên tuyển dụng. Đánh giá mức độ phù hợp của ứng viên (CV) với tin tuyển dụng (JD) theo thang:
3 = Phù hợp tốt: cùng vai trò, đáp ứng phần lớn yêu cầu bắt buộc, đủ cấp độ.
2 = Phù hợp một phần: đáng cân nhắc nhưng thiếu yêu cầu quan trọng hoặc lệch cấp.
1 = Liên quan ngành: cùng ngành/vai trò nhưng thiếu phần lớn yêu cầu.
0 = Không phù hợp: khác hẳn lĩnh vực.
Đánh giá năng lực làm được việc: ứng viên dư kinh nghiệm không bị trừ điểm. Bỏ qua tên, giới tính, trường học và cách trình bày.
Ngoài mức, cho điểm 0-100 nhất quán với mức (mức 3: 75-100, mức 2: 50-74, mức 1: 25-49, mức 0: 0-24) để phân biệt các ứng viên cùng mức.
Chỉ trả về JSON: {"grade": <0-3>, "score": <0-100>}"""


def parse(raw):
    m = re.search(r"\{[^{}]*\}", raw or "")
    try:
        d = json.loads(m.group())
        g, s = int(d["grade"]), float(d["score"])
        return {"grade": g, "score": s} if 0 <= g <= 3 and 0 <= s <= 100 else None
    except (AttributeError, KeyError, TypeError, ValueError):
        return None


assert parse('```json\n{"grade": 2, "score": 61}\n```') == {"grade": 2, "score": 61.0} and parse("lỗi") is None and parse('{"grade": 5, "score": 9}') is None

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", nargs="?", default="own", choices=["own", "ext"])
    ap.add_argument("--model", default="gemini-3.5-flash-lite")   # tên cố định: bí danh *-latest có thể đổi mô hình giữa các ngày chạy
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.which == "own":
        cvt, jdt = load_texts()
        out = os.path.join(RES, "static_scores.csv")
    else:
        from src.modeling.train_ext import load, sid
        d = load()
        df = pd.concat([d["train"], d["test"]])
        cvt, jdt = {sid(t): t for t in df.resume_text.unique()}, {sid(t): t for t in df.job_description_text.unique()}
        out = os.path.join(RES, "ext_cna_static.csv")
    S = pd.read_csv(out)
    idx = S.index
    if a.which == "ext":                                  # như c_rerank.py: chỉ JD đủ điều kiện (>=2 cặp, >=1 Good Fit)
        ok = [j for j, x in S.groupby("jd_id") if len(x) >= 2 and (x.grade >= 2).any()]
        idx = S.index[S.jd_id.isin(ok)]
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    key = lambda j, c: hashlib.sha256(f"{VERSION}|{a.model}|{jdt[j].strip()}|{cvt[c].strip()}".encode("utf-8")).hexdigest()

    fails = [0]                                           # số lần lỗi liên tiếp; >= 4 coi như hết hạn mức ngày, bỏ qua phần còn lại của đợt

    def one(jc):
        if fails[0] >= 4:
            return
        j, c = jc
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"JD:\n{jdt[j]}\n\nCV:\n{cvt[c]}"}]
        r = parse(_call_llm(msgs, a.model, max_retries=5, temperature=0.0))
        if r:
            cache[key(j, c)] = r
        fails[0] = 0 if r else fails[0] + 1

    todo = [(j, c) for j, c in zip(S.jd_id[idx], S.cv_id[idx]) if key(j, c) not in cache]
    print("cần chấm:", len(todo), "/", len(S), flush=True)
    for i in range(0, len(todo), 40):                    # ghi cache từng đợt để hết hạn mức / mất mạng không mất kết quả
        n0 = len(cache)
        with ThreadPoolExecutor(a.workers) as ex:
            list(ex.map(one, todo[i:i + 40]))
        json.dump(cache, open(CACHE + ".tmp", "w", encoding="utf-8"), ensure_ascii=False)
        os.replace(CACHE + ".tmp", CACHE)
        if fails[0] >= 4:
            sys.exit(f"HET_HAN_MUC: 4 cặp liên tiếp lỗi (đợt này chấm được {len(cache) - n0}). Đổi khóa rồi chạy lại.")
        print("đã chấm", min(i + 40, len(todo)), "/", len(todo), flush=True)
    r = [cache.get(key(j, c)) for j, c in zip(S.jd_id[idx], S.cv_id[idx])]
    miss = sum(x is None for x in r)
    if miss:
        sys.exit(f"còn {miss} cặp chưa chấm được (hết hạn mức?). Chạy lại để chấm tiếp; chưa ghi cột vào {out}.")
    S[f"llm|{a.model}"], S[f"llmgrade|{a.model}"] = np.nan, np.nan
    S.loc[idx, f"llm|{a.model}"] = [x["score"] for x in r]
    S.loc[idx, f"llmgrade|{a.model}"] = [x["grade"] for x in r]
    S.to_csv(out, index=False)
    S = S.loc[idx]
    y = S[f"llmgrade|{a.model}"].astype(int)
    if a.which == "ext":                                  # nhãn ext là 0-2, không so trực tiếp với mức 0-3 của LLM
        sys.exit(print("đã lưu", out) or print(pd.crosstab(S.grade, y, rownames=["nhãn"], colnames=["LLM"])))
    print("đã lưu", out, "| mức LLM so với nhãn: khớp", f"{(y == S.grade).mean():.3f}", "QWK", f"{cohen_kappa_score(S.grade, y, weights='quadratic'):.3f}")
    print(pd.crosstab(S.grade, y, rownames=["nhãn"], colnames=["LLM"]))
