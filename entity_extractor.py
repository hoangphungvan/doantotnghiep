"""
Module trích xuất thực thể từ văn bản CV/JD sử dụng Google Gemini API.
Trích xuất 6 loại: soft_skills, hard_skills, education,
field_of_education, industry_sector, role.
"""

import json
import re
import sys
import time
from typing import Optional

import fitz  # PyMuPDF
from openai import OpenAI

import config


def _print(*args, **kwargs):
    """Print with flush for immediate output."""
    print(*args, **kwargs, flush=True)

# Free tier quota: 15 RPM cho gemini-2.0-flash.
# Tất cả Gemini models dùng chung quota theo API key nên không fallback giữa chúng.
# Chỉ retry với cùng model và chờ đủ 60s để quota reset.
RETRY_WAIT_SECONDS = 62  # chờ hơn 60s để đảm bảo Gemini reset quota

client = OpenAI(
    api_key=config.GEMINI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    timeout=120.0,
)

EXTRACTION_PROMPT = """Bạn là chuyên gia phân tích CV và Job Description (JD).
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


def read_pdf(pdf_path: str) -> str:
    """Đọc toàn bộ text từ file PDF bằng PyMuPDF."""
    doc = fitz.open(pdf_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)


def read_text_file(file_path: str) -> str:
    """Đọc file text thường."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_document(file_path: str) -> str:
    """Đọc tài liệu, hỗ trợ PDF và text."""
    if file_path.lower().endswith(".pdf"):
        return read_pdf(file_path)
    return read_text_file(file_path)


def extract_entities(text: str, model: Optional[str] = None, max_retries: int = 3) -> dict:
    """
    Gọi Gemini API để trích xuất 6 loại thực thể từ văn bản.
    Khi bị rate limit (429), chờ 62s rồi retry (đủ để Gemini reset quota 1 phút).

    Returns:
        dict với keys: soft_skills, hard_skills, education,
                       field_of_education, industry_sector, role
    """
    current_model = model or config.LLM_MODEL
    prompt = EXTRACTION_PROMPT.format(text=text[:8000])
    messages = [
        {"role": "system", "content": "Bạn là trợ lý AI chuyên trích xuất thông tin có cấu trúc. Luôn trả về JSON thuần túy."},
        {"role": "user", "content": prompt},
    ]

    raw = None
    for attempt in range(1, max_retries + 1):
        try:
            _print(f"[INFO] Gọi {current_model} (lần {attempt}/{max_retries})...")
            response = client.chat.completions.create(
                model=current_model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
            )
            raw = response.choices[0].message.content.strip()
            _print(f"[INFO] Thành công!")
            break
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate" in err_str.lower() or "quota" in err_str.lower():
                if attempt < max_retries:
                    _print(f"[WARN] Rate limit (429) — chờ {RETRY_WAIT_SECONDS}s để Gemini reset quota...")
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    _print(f"[ERROR] Đã thử {max_retries} lần, vẫn bị rate limit. Trả về entity rỗng.")
            else:
                _print(f"[ERROR] Lỗi không phải rate limit: {err_str[:300]}")
                break

    if not raw:
        return {etype: [] for etype in config.ENTITY_TYPES}

    json_match = re.search(r'\{[\s\S]*\}', raw)
    if json_match:
        raw = json_match.group()

    try:
        entities = json.loads(raw)
    except json.JSONDecodeError:
        _print(f"[WARN] Cannot parse JSON from LLM, returning empty.\nRaw: {raw[:500]}")
        entities = {}

    default = {etype: [] for etype in config.ENTITY_TYPES}
    for key in default:
        if key in entities and isinstance(entities[key], list):
            default[key] = [str(item) for item in entities[key]]

    return default


def extract_from_file(file_path: str, model: Optional[str] = None) -> dict:
    """Đọc file và trích xuất thực thể."""
    text = read_document(file_path)
    return extract_entities(text, model)


if __name__ == "__main__":
    sample_cv = """
    Nguyễn Văn A - Software Engineer
    Học vấn: Cử nhân Khoa học Máy tính, Đại học Bách Khoa TP.HCM
    Kỹ năng: Python, Java, Machine Learning, SQL, Docker, Git
    Kỹ năng mềm: Làm việc nhóm, thuyết trình, giải quyết vấn đề
    Kinh nghiệm: 3 năm tại công ty Công nghệ thông tin
    Vị trí: Backend Developer, Data Engineer
    """
    print("=== Trích xuất từ CV mẫu ===")
    result = extract_entities(sample_cv)
    print(json.dumps(result, ensure_ascii=False, indent=2))
