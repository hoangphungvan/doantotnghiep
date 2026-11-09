"""
Trích xuất MỨC YÊU CẦU bằng Gemini (schema JSON cố định) cho đồ thị mức yêu cầu.

Mỗi văn bản trả về:
  {"level": "intern|fresher|junior|middle|senior|lead"|null, "total_years": số|null,
   "items": [{"text": str, "type": hard_skill|soft_skill|education|role|industry, "required": bool, "years": số|null}]}
JD: mỗi item là một yêu cầu; required=false cho ý "ưu tiên/lợi thế"; years = số năm tối thiểu cho yêu cầu đó.
CV: mỗi item là một thứ ứng viên thực sự có; required luôn true; years = số năm thực tế dùng/làm (nếu nêu).

Cache riêng: data/cache/req_cache.json (khóa = sha256 của văn bản + phiên bản prompt).
"""

import hashlib
import json
import os
import re
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.extraction.entity_extractor import _call_llm

PROMPT_VERSION = "r1"
ITEM_TYPES = ["hard_skill", "soft_skill", "education", "role", "industry"]
LEVELS = ["intern", "fresher", "junior", "middle", "senior", "lead"]
CACHE_FILE = os.path.join(config.DATA_CACHE_DIR, "req_cache.json")

PROMPT = """Bạn là chuyên gia phân tích CV và Job Description (JD). Đọc văn bản dưới đây (loại: {kind}) và trả về **chỉ** JSON thuần túy theo đúng schema, không markdown, không giải thích.

Schema:
{{"level": "intern|fresher|junior|middle|senior|lead hoặc null",
  "total_years": số năm kinh nghiệm làm việc liên quan (JD: số năm tối thiểu yêu cầu; CV: tổng số năm ứng viên có) hoặc null,
  "items": [{{"text": "...", "type": "hard_skill|soft_skill|education|role|industry", "required": true|false, "years": số hoặc null}}]}}

Loại item:
- hard_skill: kỹ năng/công nghệ/công cụ chuyên môn (Python, SQL, Docker, phân tích yêu cầu, ...)
- soft_skill: kỹ năng mềm (giao tiếp, làm việc nhóm, ...)
- education: trình độ hoặc ngành học (Cử nhân CNTT, Thạc sĩ, ...)
- role: vị trí/vai trò (Backend Developer, Business Analyst, ...)
- industry: lĩnh vực/ngành nghề (Fintech, Thương mại điện tử, ...)

Quy tắc:
- Mỗi item là MỘT ý ngắn gọn (tối đa 8 từ), không gộp nhiều kỹ năng vào một item.
- {rules}
- "years": số năm gắn với RIÊNG item đó nếu văn bản nêu rõ (ví dụ "3 năm Java" thì years=3); nếu không nêu thì null. Không tự suy diễn.
- "level": mức cấp bậc tổng thể ({level_hint}); null nếu không xác định được.
- Không tự suy diễn kỹ năng mà văn bản không nhắc tới.

Văn bản:
---
{text}
---"""

RULES = {
    "JD": 'required=true cho yêu cầu bắt buộc; required=false cho ý ghi "ưu tiên", "là lợi thế", "điểm cộng", "nice to have", "plus". Không đưa quyền lợi, mô tả công ty hay lương vào items.',
    "CV": "required luôn là true. Chỉ đưa vào những gì ứng viên THỰC SỰ CÓ hoặc đã từng dùng; BỎ QUA mọi thứ CV nói là chưa có, đang tìm hiểu hoặc muốn học.",
}
LEVEL_HINT = {"JD": "mức cấp bậc mà vị trí tuyển", "CV": "mức cấp bậc của ứng viên dựa trên kinh nghiệm"}

_cache = None


def _key(text, kind):
    return f"{PROMPT_VERSION}:{kind}:" + hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def _load():
    global _cache
    if _cache is None:
        _cache = json.load(open(CACHE_FILE, encoding="utf-8")) if os.path.exists(CACHE_FILE) else {}
    return _cache


def save_cache():
    """Gộp với bản trên đĩa rồi mới ghi: nhiều tiến trình cùng trích xuất không ghi đè mất mục của nhau."""
    os.makedirs(config.DATA_CACHE_DIR, exist_ok=True)
    cache = _load()
    if os.path.exists(CACHE_FILE):
        for k, v in json.load(open(CACHE_FILE, encoding="utf-8")).items():
            cache.setdefault(k, v)
    tmp = f"{CACHE_FILE}.{os.getpid()}.tmp"
    json.dump(cache, open(tmp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    os.replace(tmp, CACHE_FILE)


def _num(x):
    try:
        v = float(x)
        return v if 0 <= v <= 40 else None
    except (TypeError, ValueError):
        return None


def parse(raw: str) -> dict:
    m = re.search(r"\{[\s\S]*\}", re.sub(r"<think>[\s\S]*?</think>", "", raw))
    try:
        d = json.loads(m.group()) if m else {}
    except json.JSONDecodeError:
        d = {}
    items = []
    for it in d.get("items", []) if isinstance(d.get("items"), list) else []:
        if isinstance(it, dict) and str(it.get("text", "")).strip() and it.get("type") in ITEM_TYPES:
            items.append({"text": str(it["text"]).strip(), "type": it["type"], "required": bool(it.get("required", True)), "years": _num(it.get("years"))})
    lv = d.get("level")
    return {"level": lv if lv in LEVELS else None, "total_years": _num(d.get("total_years")), "items": items}


def extract_requirements(text: str, kind: str, max_retries: int = 3) -> dict:
    """kind: 'JD' hoặc 'CV'. Trả về dict theo schema; rỗng (items=[]) nếu LLM lỗi và không ghi cache."""
    cache, key = _load(), _key(text, kind)
    if key in cache:
        return cache[key]
    msgs = [{"role": "system", "content": "Bạn là trợ lý AI trích xuất thông tin có cấu trúc. Luôn trả về JSON thuần túy."},
            {"role": "user", "content": PROMPT.format(kind=kind, rules=RULES[kind], level_hint=LEVEL_HINT[kind], text=text[:8000])}]
    raw = _call_llm(msgs, config.LLM_MODEL, max_retries)
    res = parse(raw) if raw else {"level": None, "total_years": None, "items": []}
    if res["items"]:
        cache[key] = res
    return res
