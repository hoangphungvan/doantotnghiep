"""
Đánh giá cặp CV–JD bằng LLM, CHỈ dùng để sinh diễn giải cho nhà tuyển dụng (không tham gia chấm điểm).

LLM đọc trực tiếp hai văn bản và trả về: các yêu cầu BẮT BUỘC của JD mà CV có bằng chứng đáp ứng hay không, các điều
kiện cứng, số năm kinh nghiệm yêu cầu so với CV, và công nghệ trong tiêu đề JD có xuất hiện ở CV không.
Kết quả cache theo hash (phiên bản prompt, model LLM, CV, JD) trong data/cache/pair_features.jsonl.
"""

import hashlib
import json
import os
import re
import sys
import threading
import time


if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.extraction.entity_extractor import _get_client

CACHE_FILE = os.path.join(config.DATA_CACHE_DIR, "pair_features.jsonl")
FEATURE_NAMES = ["pf_coverage", "pf_n_req", "pf_years_gap", "pf_hard_missing", "pf_title_tech_missing", "pf_valid"]

PROMPT_VERSION = "v2-batch"
PROMPT = """Bạn là chuyên viên tuyển dụng. Dưới đây là MỘT CV và {n} JD. Hãy đánh giá CV với TỪNG JD một cách độc lập (kết quả của JD này không được ảnh hưởng tới JD khác).

Với mỗi JD:
1. "requirements": liệt kê các YÊU CẦU BẮT BUỘC về chuyên môn của JD (kỹ năng, công nghệ, nghiệp vụ). BỎ QUA các ý ghi "ưu tiên", "là lợi thế", "nice to have", "điểm cộng", các phẩm chất chung chung (nhiệt tình, trung thực, chịu áp lực...) và các điều kiện ở mục 2. Mỗi yêu cầu một dòng ngắn; "met" = true nếu CV có BẰNG CHỨNG đáp ứng (kỹ năng được nêu hoặc dùng trong kinh nghiệm; công nghệ tương đương rõ ràng được tính), ngược lại false. Không suy diễn kỹ năng CV không nhắc tới.
2. "conditions": các ĐIỀU KIỆN CỨNG JD ghi bắt buộc: bằng cấp/ngành bắt buộc, chứng chỉ, ngoại ngữ có mức cụ thể, tình trạng sinh viên, yêu cầu gửi CV tiếng Anh... (không tính tuổi, giới tính). "met" = true nếu CV đáp ứng.
3. "jd_min_years": số năm kinh nghiệm tối thiểu JD yêu cầu (số, 0 nếu không yêu cầu hoặc là thực tập).
4. "cv_years": số năm kinh nghiệm làm việc liên quan trực tiếp tới vai trò của JD mà CV có (số, 0 nếu chưa có).
5. "title_tech_in_cv": nếu tiêu đề JD nêu một công nghệ/nền tảng cụ thể (ví dụ Sitecore, Flutter, PHP Laravel, Swift, Java, Salesforce) thì true/false tùy CV có công nghệ đó không; nếu tiêu đề chung chung thì null.

Chỉ trả về JSON đúng dạng, mỗi JD đúng một phần tử, giữ nguyên "jd_id":
{{"results": [{{"jd_id": "...", "requirements": [{{"text": "...", "met": true}}], "conditions": [{{"text": "...", "met": false}}], "jd_min_years": 0, "cv_years": 0, "title_tech_in_cv": null}}]}}

=== CV ===
{cv}

{jds}"""

_lock = threading.Lock()
_cache = None


def _key(cv_text: str, jd_text: str) -> str:
    return hashlib.sha256((PROMPT_VERSION + "\n" + config.LLM_MODEL + "\n" + cv_text.strip() + "\n||\n" + jd_text.strip()).encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        _cache = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        _cache[rec["key"]] = rec["data"]
    return _cache


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _call(cv_text: str, jds: dict, max_retries: int = 4) -> dict:
    """Một lần gọi LLM cho một CV và nhiều JD. Trả về {jd_id: dict thô}; JD nào LLM bỏ sót thì không có trong kết quả."""
    jd_block = "\n\n".join(f"=== JD id={jid} ===\n{txt.strip()}" for jid, txt in jds.items())
    msg = [{"role": "user", "content": PROMPT.format(n=len(jds), cv=cv_text.strip(), jds=jd_block)}]
    for attempt in range(1, max_retries + 1):
        try:
            raw = _get_client().chat.completions.create(
                model=config.LLM_MODEL, messages=msg, temperature=0, max_tokens=16000).choices[0].message.content
            raw = re.sub(r"<think>[\s\S]*?</think>", "", raw)
            res = json.loads(re.search(r"\{[\s\S]*\}", raw).group())["results"]
            return {str(r["jd_id"]): r for r in res
                    if isinstance(r, dict) and str(r.get("jd_id")) in jds and isinstance(r.get("requirements"), list)}
        except Exception as e:
            time.sleep(10 * attempt if ("429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower()) else 1)
    return {}


def extract_cv_features(cv_text: str, jds: dict, use_cache: bool = True) -> dict:
    """Đặc trưng thô cho một CV với nhiều JD ({jd_id: jd_text}); gọi LLM một lần cho các JD chưa cache.
    Lô hỏng hẳn thì chia đôi và thử lại; JD bị LLM bỏ sót thì gọi lại phần còn thiếu."""
    with _lock:
        cache = _load_cache()
        out = {j: cache[_key(cv_text, tx)] for j, tx in jds.items() if use_cache and _key(cv_text, tx) in cache}
    todo = {j: tx for j, tx in jds.items() if j not in out}
    while todo:
        got = _call(cv_text, todo)
        if not got:
            if len(todo) > 1:
                items = list(todo.items())
                half = len(items) // 2
                for part in (dict(items[:half]), dict(items[half:])):
                    out.update(extract_cv_features(cv_text, part, use_cache=False))
            break
        with _lock:
            with open(CACHE_FILE, "a", encoding="utf-8") as f:
                for j, d in got.items():
                    cache[_key(cv_text, todo[j])] = d
                    f.write(json.dumps({"key": _key(cv_text, todo[j]), "data": d}, ensure_ascii=False) + "\n")
        out.update(got)
        todo = {j: tx for j, tx in todo.items() if j not in got}
    return out


def extract_pair_features(cv_text: str, jd_text: str, use_cache: bool = True) -> dict:
    """Một cặp (dùng khi suy luận): cùng prompt với chạy hàng loạt, lô 1 JD. Trả về dict thô hoặc {} nếu lỗi."""
    return extract_cv_features(cv_text, {"J": jd_text}, use_cache=use_cache).get("J", {})


def to_vector(d: dict) -> dict:
    """Dict thô → 6 đặc trưng số (FEATURE_NAMES). pf_valid = 0 nếu LLM lỗi/bỏ sót JD (các đặc trưng khác để 0)."""
    if "requirements" not in d:
        return dict(zip(FEATURE_NAMES, [0.0] * 6))   # LLM lỗi / bỏ sót
    reqs = [r for r in d["requirements"] if isinstance(r, dict)]
    conds = [c for c in d.get("conditions", []) if isinstance(c, dict)]
    cov = sum(bool(r.get("met")) for r in reqs) / len(reqs) if reqs else 0.5   # JD không nêu yêu cầu chuyên môn: trung tính, n_req = 0
    gap = max(0.0, _num(d.get("jd_min_years")) - _num(d.get("cv_years")))
    return {"pf_coverage": cov, "pf_n_req": float(len(reqs)), "pf_years_gap": min(gap, 6.0) / 6.0,
            "pf_hard_missing": float(sum(not c.get("met") for c in conds)),
            "pf_title_tech_missing": float(d.get("title_tech_in_cv") is False), "pf_valid": 1.0}
