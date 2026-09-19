"""
Module trích xuất thực thể từ văn bản CV/JD sử dụng Groq API (OpenAI-compatible).
Trích xuất 6 loại: soft_skills, hard_skills, education,
field_of_education, industry_sector, role.

Hỗ trợ 2 chế độ:
- Text mode : Đọc text từ PDF/TXT → gửi Groq API
- Vision mode: PDF scan/ảnh → chuyển ảnh base64 → gửi Vision Model
"""

import base64
import json
import os
import re
import sys
import time
from typing import Optional

import hashlib
import fitz  # PyMuPDF
from openai import OpenAI

# Hỗ trợ chạy trực tiếp: python src/extraction/entity_extractor.py (từ thư mục gốc dự án)
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config


def _print(*args, **kwargs):
    """Print with flush for immediate output."""
    print(*args, **kwargs, flush=True)


# ---------------------------------------------------------------------------
# Entity Cache Mechanism (Hash-based & File-based)
# ---------------------------------------------------------------------------

_entity_cache: Optional[dict] = None


def _load_cache() -> dict:
    global _entity_cache
    if _entity_cache is None:
        if os.path.exists(config.ENTITY_CACHE_FILE):
            try:
                with open(config.ENTITY_CACHE_FILE, "r", encoding="utf-8") as f:
                    _entity_cache = json.load(f)
            except Exception:
                _entity_cache = {}
        else:
            _entity_cache = {}
    return _entity_cache


def _save_cache():
    global _entity_cache
    if _entity_cache is not None:
        os.makedirs(config.DATA_CACHE_DIR, exist_ok=True)
        with open(config.ENTITY_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_entity_cache, f, ensure_ascii=False, indent=2)


def get_cache_key(text: str) -> str:
    """Tạo hash SHA256 cho nội dung văn bản."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def get_cached_entity(key: str) -> Optional[dict]:
    """Lấy thực thể từ cache theo hash hoặc đường dẫn."""
    cache = _load_cache()
    return cache.get(key)


def set_cached_entity(key: str, data: dict, save: bool = True):
    """Lưu thực thể vào cache."""
    cache = _load_cache()
    cache[key] = data
    if save:
        _save_cache()


def save_entire_cache():
    """Ghi toàn bộ cache ra đĩa."""
    _save_cache()


# Groq Rate Limit retry wait time (giây)
RETRY_WAIT_SECONDS = 10

# Ngưỡng ký tự tối thiểu để coi PDF có text layer hợp lệ
PDF_TEXT_MIN_CHARS = 50

# Số trang tối đa gửi lên Vision (tránh vượt token limit)
VISION_MAX_PAGES = 5

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """Lazy-init OpenAI client cho LLM API — chỉ tạo khi thực sự gọi LLM."""
    global _client
    if _client is None:
        if not config.LLM_API_KEY:
            raise RuntimeError(
                "Thiếu LLM_API_KEY (hoặc GROQ_API_KEY). Set biến môi trường trong file .env "
                "để dùng tính năng trích xuất thực thể bằng LLM."
            )
        _client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            timeout=120.0,
        )
    return _client

EXTRACTION_PROMPT_TEXT = """Bạn là chuyên gia phân tích CV và Job Description (JD).
Hãy trích xuất các thực thể từ đoạn văn bản dưới đây và trả về **chỉ** JSON thuần túy (không markdown, không giải thích).

6 loại thực thể cần trích xuất:
1. "soft_skills": Kỹ năng mềm (giao tiếp, teamwork, lãnh đạo, quản lý thời gian, ...)
2. "hard_skills": Kỹ năng chuyên môn (Python, SQL, Machine Learning, Excel, ...)
3. "education": Trình độ học vấn (Cử nhân, Thạc sĩ, Tiến sĩ, ...)
4. "field_of_education": Ngành/Chuyên ngành học (Khoa học máy tính, Quản trị kinh doanh, ...)
5. "industry_sector": Ngành nghề/Lĩnh vực (Công nghệ thông tin, Tài chính, Y tế, ...)
6. "role": Vị trí/Vai trò (Software Engineer, Data Analyst, Project Manager, ...)

Mỗi loại trả về dạng danh sách các chuỗi. Nếu không tìm thấy, trả về danh sách rỗng [].

Văn bản:
---
{text}
---

Trả về JSON đúng định dạng:
{{"soft_skills": [...], "hard_skills": [...], "education": [...], "field_of_education": [...], "industry_sector": [...], "role": [...]}}"""

EXTRACTION_PROMPT_VISION = """Bạn là chuyên gia phân tích CV và Job Description (JD).
Hãy đọc nội dung từ hình ảnh tài liệu bên dưới, sau đó trích xuất thực thể và trả về **chỉ** JSON thuần túy (không markdown, không giải thích).

6 loại thực thể cần trích xuất:
1. "soft_skills": Kỹ năng mềm (giao tiếp, teamwork, lãnh đạo, quản lý thời gian, ...)
2. "hard_skills": Kỹ năng chuyên môn (Python, SQL, Machine Learning, Excel, ...)
3. "education": Trình độ học vấn (Cử nhân, Thạc sĩ, Tiến sĩ, ...)
4. "field_of_education": Ngành/Chuyên ngành học (Khoa học máy tính, Quản trị kinh doanh, ...)
5. "industry_sector": Ngành nghề/Lĩnh vực (Công nghệ thông tin, Tài chính, Y tế, ...)
6. "role": Vị trí/Vai trò (Software Engineer, Data Analyst, Project Manager, ...)

Mỗi loại trả về dạng danh sách các chuỗi. Nếu không tìm thấy, trả về danh sách rỗng [].

Trả về JSON đúng định dạng:
{"soft_skills": [...], "hard_skills": [...], "education": [...], "field_of_education": [...], "industry_sector": [...], "role": [...]}"""


# ---------------------------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------------------------

def read_pdf_text(pdf_path: str) -> str:
    """Đọc text layer từ PDF. Trả về chuỗi rỗng nếu PDF là file scan."""
    doc = fitz.open(pdf_path)
    parts = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(parts).strip()


def pdf_to_images_base64(pdf_path: str, dpi: int = 150, max_pages: int = VISION_MAX_PAGES) -> list[str]:
    """
    Chuyển từng trang PDF thành ảnh PNG, encode base64.
    dpi=150 đủ rõ để Gemini Vision đọc, không quá nặng.
    """
    doc = fitz.open(pdf_path)
    images_b64 = []
    total = min(len(doc), max_pages)
    for i in range(total):
        pix = doc[i].get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        images_b64.append(base64.b64encode(img_bytes).decode("utf-8"))
    doc.close()
    return images_b64


def normalize_path(file_path: str) -> str:
    """Bỏ khoảng trắng và dấu ngoặc kép thừa người dùng nhập."""
    path = file_path.strip().strip('"').strip("'")
    return os.path.normpath(path)


def read_text_file(file_path: str) -> str:
    """Đọc file text thuần."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_document(file_path: str) -> str:
    """Đọc tài liệu, hỗ trợ PDF (text layer) và file text."""
    path = normalize_path(file_path)
    if path.lower().endswith(".pdf"):
        return read_pdf_text(path)
    return read_text_file(path)


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------

def _parse_entities(raw: str) -> dict:
    """Parse JSON từ response LLM, luôn trả về dict đúng cấu trúc."""
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        raw = match.group()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        _print(f"[WARN] Không parse được JSON từ LLM.\nRaw: {raw[:400]}")
        parsed = {}

    result = {etype: [] for etype in config.ENTITY_TYPES}
    for key in result:
        if key in parsed and isinstance(parsed[key], list):
            result[key] = [str(item) for item in parsed[key]]
    return result


# ---------------------------------------------------------------------------
# Core API call with retry
# ---------------------------------------------------------------------------

def _call_llm(messages: list, model: str, max_retries: int = 3) -> Optional[str]:
    """Gọi LLM API (Groq), retry khi 429. Trả về raw string hoặc None nếu thất bại."""
    for attempt in range(1, max_retries + 1):
        try:
            _print(f"[INFO] Gọi {model} (lần {attempt}/{max_retries})...")
            resp = _get_client().chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
            )
            raw = resp.choices[0].message.content.strip()
            _print("[INFO] Thành công!")
            return raw
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower() or "quota" in err.lower():
                if attempt < max_retries:
                    _print(f"[WARN] Rate limit — chờ {RETRY_WAIT_SECONDS}s để thử lại...")
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    _print(f"[ERROR] Đã thử {max_retries} lần, vẫn bị rate limit.")
            else:
                _print(f"[ERROR] {err[:300]}")
                break
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_entities(text: str, model: Optional[str] = None, max_retries: int = 3, use_cache: bool = True) -> dict:
    """
    Trích xuất thực thể từ chuỗi văn bản (text mode).
    Dùng khi đã có text từ PDF hoặc file txt.
    """
    model = model or config.LLM_MODEL

    if not text.strip():
        _print("[ERROR] Text rỗng — không thể trích xuất. Với PDF scan hãy dùng extract_entities_vision().")
        return {etype: [] for etype in config.ENTITY_TYPES}

    cache_key = get_cache_key(text)
    if use_cache:
        cached = get_cached_entity(cache_key)
        if cached:
            return cached

    messages = [
        {
            "role": "system",
            "content": "Bạn là trợ lý AI chuyên trích xuất thông tin có cấu trúc. Luôn trả về JSON thuần túy.",
        },
        {
            "role": "user",
            "content": EXTRACTION_PROMPT_TEXT.format(text=text[:8000]),
        },
    ]

    raw = _call_llm(messages, model, max_retries)
    if not raw:
        return {etype: [] for etype in config.ENTITY_TYPES}
    result = _parse_entities(raw)
    if use_cache and result:
        set_cached_entity(cache_key, result)
    return result


def extract_entities_vision(pdf_path: str, model: Optional[str] = None, max_retries: int = 3, use_cache: bool = True) -> dict:
    """
    Trích xuất thực thể từ PDF scan.
    Chuyển từng trang PDF → ảnh PNG base64 → gửi multimodal message.
    """
    model = model or config.LLM_MODEL
    pdf_path = normalize_path(pdf_path)

    if use_cache:
        cached = get_cached_entity(pdf_path)
        if cached:
            return cached

    _print(f"[INFO] Vision mode: chuyển '{os.path.basename(pdf_path)}' sang ảnh...")
    images_b64 = pdf_to_images_base64(pdf_path)

    if not images_b64:
        _print("[ERROR] Không render được trang nào từ PDF.")
        return {etype: [] for etype in config.ENTITY_TYPES}

    _print(f"[INFO] Gửi {len(images_b64)} trang lên Vision Model...")

    # Tạo multimodal message: text prompt + danh sách ảnh
    content = [{"type": "text", "text": EXTRACTION_PROMPT_VISION}]
    for b64 in images_b64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"},
        })

    messages = [{"role": "user", "content": content}]

    raw = _call_llm(messages, model, max_retries)
    if not raw:
        return {etype: [] for etype in config.ENTITY_TYPES}
    result = _parse_entities(raw)
    if use_cache and result:
        set_cached_entity(pdf_path, result)
    return result


_vietjobs_df = None


def get_vietjobs_df():
    """Lazy-load DataFrame của VietJobs_cntt.csv với index theo jd_id."""
    global _vietjobs_df
    if _vietjobs_df is None:
        csv_path = getattr(config, "VIETJOBS_IT_CSV", os.path.join(config.DATA_RAW_DIR, "VietJobs_cntt.csv"))
        if os.path.exists(csv_path):
            import pandas as pd
            df = pd.read_csv(csv_path)
            if "jd_id" in df.columns:
                _vietjobs_df = df.set_index("jd_id", drop=False)
            else:
                _vietjobs_df = df
        else:
            _vietjobs_df = None
    return _vietjobs_df


def get_jd_text_by_id(identifier: str) -> Optional[str]:
    """
    Tra cứu formatted_jd_text từ file CSV VietJobs_cntt.csv theo jd_id hoặc tên file cũ.
    Hỗ trợ:
    - 'jd_0021'
    - 21 hoặc '21'
    - 'jd_0021_nha_phan_tich_kinh_doanh_cao_cap.txt'
    - 'data/raw/jds/cntt/jd_0021_nha_phan_tich_kinh_doanh_cao_cap.txt'
    """
    df = get_vietjobs_df()
    if df is None or len(df) == 0:
        return None

    clean_id = str(identifier).strip().replace("\\", "/")
    match = re.search(r"jd_(\d+)", clean_id)
    if match:
        target_id = f"jd_{int(match.group(1)):04d}"
    elif clean_id.isdigit():
        target_id = f"jd_{int(clean_id):04d}"
    else:
        target_id = clean_id

    if target_id in df.index:
        row = df.loc[target_id]
        if hasattr(row, "iloc"):
            import pandas as pd
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
        return str(row.get("formatted_jd_text", ""))
    return None


def extract_from_file(file_path: str, model: Optional[str] = None, use_cache: bool = True) -> dict:
    """
    Entry point tự động: đọc file hoặc tra cứu từ VietJobs_cntt.csv và trích xuất thực thể.
    - PDF có text layer  → text mode
    - PDF scan (text < 50 ký tự) → Vision mode
    - File text (.txt, v.v.) → text mode
    - jd_id (vd: 'jd_0021') hoặc đường dẫn JD VietJobs → nạp trực tiếp từ VietJobs_cntt.csv
    """
    path = normalize_path(file_path)

    if use_cache:
        cached = get_cached_entity(path)
        if cached:
            return cached
        # Kiểm tra theo jd_id nếu path có chứa jd_xxxx
        match = re.search(r"jd_(\d+)", path)
        if match:
            target_id = f"jd_{int(match.group(1)):04d}"
            cached = get_cached_entity(target_id)
            if cached:
                return cached

    # 1. Nếu file thực sự tồn tại trên đĩa
    if os.path.exists(path):
        if path.lower().endswith(".pdf"):
            text = read_pdf_text(path)
            char_count = len(text)
            _print(f"[INFO] PDF '{os.path.basename(path)}': đọc được {char_count} ký tự.")

            if char_count < PDF_TEXT_MIN_CHARS:
                _print("[INFO] Ít text → chuyển sang Vision mode (PDF scan).")
                res = extract_entities_vision(path, model, use_cache=use_cache)
                if use_cache and res:
                    set_cached_entity(path, res)
                return res

            res = extract_entities(text, model, use_cache=use_cache)
            if use_cache and res:
                set_cached_entity(path, res)
            return res

        # File text thường trên đĩa
        text = read_text_file(path)
        res = extract_entities(text, model, use_cache=use_cache)
        if use_cache and res:
            set_cached_entity(path, res)
        return res

    # 2. Nếu không phải file trên đĩa, tra cứu trực tiếp từ VietJobs_cntt.csv theo jd_id
    jd_text = get_jd_text_by_id(path)
    if jd_text:
        res = extract_entities(jd_text, model, use_cache=use_cache)
        if use_cache and res:
            set_cached_entity(path, res)
            match = re.search(r"jd_(\d+)", path)
            if match:
                set_cached_entity(f"jd_{int(match.group(1)):04d}", res)
        return res

    raise FileNotFoundError(f"Không tìm thấy file hoặc JD ID trong VietJobs: {file_path}")


if __name__ == "__main__":
    sample_cv = """
    Nguyễn Văn A - Software Engineer
    Học vấn: Cử nhân Khoa học Máy tính, Đại học Bách Khoa TP.HCM
    Kỹ năng: Python, Java, Machine Learning, SQL, Docker, Git
    Kỹ năng mềm: Làm việc nhóm, thuyết trình, giải quyết vấn đề
    Kinh nghiệm: 3 năm tại công ty Công nghệ thông tin
    Vị trí: Backend Developer, Data Engineer
    """
    _print("=== Test Text Mode ===")
    result = extract_entities(sample_cv)
    print(json.dumps(result, ensure_ascii=False, indent=2))
