"""
Module trích xuất thực thể từ văn bản CV/JD sử dụng LLM API (OpenRouter).
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

FALLBACK_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "google/gemma-4-26b-a4b-it:free",
]

client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    timeout=60.0,
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
    Gọi LLM API để trích xuất 6 loại thực thể từ văn bản.
    Tự động retry với model khác nếu bị rate limit.

    Returns:
        dict với keys: soft_skills, hard_skills, education,
                       field_of_education, industry_sector, role
    """
    models_to_try = [model or config.LLM_MODEL] + FALLBACK_MODELS
    seen = set()
    unique_models = []
    for m in models_to_try:
        if m not in seen:
            seen.add(m)
            unique_models.append(m)

    prompt = EXTRACTION_PROMPT.format(text=text[:8000])
    messages = [
        {"role": "system", "content": "Bạn là trợ lý AI chuyên trích xuất thông tin có cấu trúc. Luôn trả về JSON thuần túy."},
        {"role": "user", "content": prompt},
    ]

    raw = None
    for current_model in unique_models:
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000,
                )
                raw = response.choices[0].message.content.strip()
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate" in err_str.lower():
                    wait = 2 ** (attempt + 1)
                    _print(f"[WARN] Rate limited on {current_model}, retry in {wait}s...")
                    time.sleep(wait)
                else:
                    _print(f"[WARN] Error with {current_model}: {err_str[:200]}")
                    break
        if raw:
            break

    if not raw:
        _print("[ERROR] All models failed, returning empty entities.")
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
