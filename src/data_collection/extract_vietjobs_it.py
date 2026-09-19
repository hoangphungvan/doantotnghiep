"""
Script trích xuất và lọc các Job Descriptions (JD) ngành Công nghệ thông tin (CNTT)
từ tập dữ liệu VietJobs.

Dữ liệu nguồn: D:\VietJobs\data\VietJobs.csv
Dữ liệu đầu ra:
1. D:\VietJobs\data\VietJobs_cntt.csv (Tập CSV chứa 1906 JD ngành CNTT)
2. D:\doantotnghiep\data\raw\VietJobs_cntt.csv (Bản sao cho đồ án tốt nghiệp)
3. D:\doantotnghiep\data\raw\jds\cntt\*.txt (Các file text JD riêng lẻ phục vụ kiểm tra & huấn luyện)
"""

import os
import re
import ast
import unicodedata
import pandas as pd
from tqdm import tqdm


VIETJOBS_CSV = r"D:\VietJobs\data\VietJobs.csv"
OUTPUT_VIETJOBS_CSV = r"D:\VietJobs\data\VietJobs_cntt.csv"
OUTPUT_DOAN_CSV = r"D:\doantotnghiep\data\raw\VietJobs_cntt.csv"
OUTPUT_TXT_DIR = r"D:\doantotnghiep\data\raw\jds\cntt"

IT_CATEGORY = "công_nghệ_thông_tin_kỹ_thuật_số"


def slugify(text: str) -> str:
    """Tạo slug an toàn cho tên file từ tiêu đề công việc."""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text)[:40]


def clean_list_str(val) -> str:
    """Chuyển chuỗi biểu diễn list python sang chuỗi phân cách bởi dấu phẩy."""
    if pd.isna(val) or not str(val).strip() or str(val) == "[]":
        return ""
    val_str = str(val).strip()
    try:
        parsed = ast.literal_eval(val_str)
        if isinstance(parsed, list):
            return ", ".join(str(x).strip() for x in parsed if str(x).strip())
    except Exception:
        pass
    return val_str


def format_jd_text(row) -> str:
    """Định dạng bản ghi JD thành văn bản hoàn chỉnh có cấu trúc rõ ràng."""
    sections = []

    title = str(row.get("job_title", "")).strip()
    if title:
        sections.append(f"VỊ TRÍ TUYỂN DỤNG: {title}")

    category = str(row.get("category", "")).strip()
    if category:
        sections.append(f"LĨNH VỰC / NGÀNH NGHỀ: {category}")

    tech_skills = clean_list_str(row.get("technical_skills"))
    if tech_skills:
        sections.append(f"KỸ NĂNG CHUYÊN MÔN: {tech_skills}")

    soft_skills = clean_list_str(row.get("soft_skills"))
    if soft_skills:
        sections.append(f"KỸ NĂNG MỀM: {soft_skills}")

    exp = str(row.get("experience_required", "")).strip()
    if exp and exp.lower() != "nan":
        sections.append(f"KINH NGHIỆM YÊU CẦU: {exp}")

    edu = clean_list_str(row.get("qualifications"))
    if edu:
        sections.append(f"TRÌNH ĐỘ HỌC VẤN: {edu}")

    location = str(row.get("location", "")).strip()
    if location and location.lower() != "nan":
        sections.append(f"ĐỊA ĐIỂM: {location}")

    salary = str(row.get("salary", "")).strip()
    if salary and salary != "0.0 triệu" and salary.lower() != "nan":
        sections.append(f"MỨC LƯƠNG: {salary}")

    desc = str(row.get("description", "")).strip()
    if desc and desc.lower() != "nan":
        sections.append(f"\nMÔ TẢ CÔNG VIỆC:\n{desc}")

    reqs = str(row.get("requirements_text", "")).strip()
    if reqs and reqs.lower() != "nan":
        sections.append(f"\nYÊU CẦU CÔNG VIỆC:\n{reqs}")

    return "\n".join(sections).strip()


def main():
    print(f"[1/4] Đọc dữ liệu từ {VIETJOBS_CSV}...")
    if not os.path.exists(VIETJOBS_CSV):
        raise FileNotFoundError(f"Không tìm thấy file: {VIETJOBS_CSV}")

    df = pd.read_csv(VIETJOBS_CSV)
    print(f"  Tổng số bản ghi trong VietJobs: {len(df):,}")

    print(f"\n[2/4] Lọc riêng ngành CNTT ('{IT_CATEGORY}')...")
    it_df = df[df["category"] == IT_CATEGORY].copy().reset_index(drop=True)
    print(f"  Số lượng JD ngành CNTT tìm thấy: {len(it_df):,}")

    print("\n[3/4] Chuẩn hóa và format văn bản JD...")
    it_df["formatted_jd_text"] = [format_jd_text(row) for _, row in it_df.iterrows()]
    it_df["jd_id"] = [f"jd_{i+1:04d}" for i in range(len(it_df))]
    # Đặt jd_id lên đầu
    cols = ["jd_id"] + [c for c in it_df.columns if c != "jd_id"]
    it_df = it_df[cols]

    # Tạo các thư mục đầu ra
    os.makedirs(os.path.dirname(OUTPUT_VIETJOBS_CSV), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_DOAN_CSV), exist_ok=True)

    # Lưu CSV sang cả VietJobs và doantotnghiep
    it_df.to_csv(OUTPUT_VIETJOBS_CSV, index=False, encoding="utf-8-sig")
    print(f"  ✓ Đã lưu CSV VietJobs CNTT: {OUTPUT_VIETJOBS_CSV}")

    it_df.to_csv(OUTPUT_DOAN_CSV, index=False, encoding="utf-8-sig")
    print(f"  ✓ Đã lưu CSV sang đồ án tốt nghiệp: {OUTPUT_DOAN_CSV}")

    print("\n" + "=" * 60)
    print(f"HOÀN TẤT: GÓI GỌN {len(it_df)} JD CNTT VÀO 1 FILE CSV DUY NHẤT!")
    print(f"File: {OUTPUT_DOAN_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    main()
