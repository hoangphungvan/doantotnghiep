"""
Tạo file gán tay 100 văn bản để đánh giá chất lượng trích xuất (P/R/F1 theo từng loại), theo yêu cầu của cô.
Mẫu: 25 JD VietJobs + 25 CV tổng hợp (tiếng Việt) + 25 CV + 25 JD của cnamuangtoun/resume-job-description-fit (tiếng Anh), chọn ngẫu nhiên seed 0.
File cho người gán KHÔNG chứa kết quả của mô hình (tránh gán theo máy); kết quả mô hình lưu riêng để chấm sau.

Chạy: python report/make_gold_template.py
Ra:   report/annotation/extraction_gold_100.xlsx   (người gán điền các cột vàng)
      report/annotation/extraction_pred_100.json   (kết quả Gemini, KHÔNG mở khi gán)
"""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.data_collection.extract_requirements_all import load_texts
from src.extraction import requirement_extractor as R
from src.modeling.train_ext import load as load_cna

OUT = os.path.join(ROOT, "report", "annotation")
TYPES = ["hard_skill", "soft_skill", "education", "role", "industry"]


def pick(d, n, seed=0):
    keys = sorted(d)
    return [keys[i] for i in pd.Series(range(len(keys))).sample(n, random_state=seed)]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cv, jd = load_texts()
    cna = load_cna()
    both = pd.concat([cna["train"], cna["test"]])
    ccv = dict(zip(both.cv_id, both.resume_text))
    cjd = dict(zip(both.jd_id, both.job_description_text))
    rows = []
    for src, kind, d in (("VietJobs", "JD", jd), ("CV tổng hợp", "CV", cv), ("resume-job-fit", "CV", ccv), ("resume-job-fit", "JD", cjd)):
        for k in pick(d, 25):
            rows.append({"doc_id": f"{src}|{kind}|{k}", "nguon": src, "loai_van_ban": kind, "van_ban": d[k][:32000]})
    cache = R._load()
    pred = {r["doc_id"]: cache.get(R._key(d_text, r["loai_van_ban"])) for r, d_text in ((r, r["van_ban"]) for r in rows)}
    df = pd.DataFrame(rows)
    for t in TYPES:
        df[t] = ""                      # mỗi mục một dòng (xuống dòng Alt+Enter) hoặc ngăn bằng dấu ;
    df["required_false"] = ""           # chỉ JD: các mục là "ưu tiên/lợi thế" (chép đúng chữ đã điền ở cột loại)
    df["level"] = ""                    # intern|fresher|junior|middle|senior|lead hoặc để trống
    df["total_years"] = ""              # số hoặc để trống
    df["nguoi_gan"] = ""
    df["ghi_chu"] = ""
    guide = pd.DataFrame({"Hướng dẫn": [
        "Đọc cột van_ban, điền các mục THỰC SỰ có trong văn bản vào đúng cột loại. Không suy diễn.",
        "Mỗi mục là MỘT ý ngắn (tối đa 8 từ), không gộp nhiều kỹ năng. Ngăn các mục bằng dấu ; hoặc xuống dòng.",
        "hard_skill: kỹ năng/công nghệ/công cụ chuyên môn. soft_skill: kỹ năng mềm. education: trình độ/ngành học.",
        "role: vị trí/vai trò. industry: lĩnh vực/ngành nghề.",
        "JD: mục ghi 'ưu tiên', 'là lợi thế', 'nice to have', 'plus' thì chép thêm vào cột required_false.",
        "CV: chỉ ghi những gì ứng viên ĐÃ CÓ; bỏ qua những gì CV nói đang học hoặc muốn học.",
        "level và total_years: ghi nếu văn bản nêu rõ hoặc suy ra trực tiếp được; không chắc thì để trống.",
        "Không mở file extraction_pred_100.json trong lúc gán (đó là kết quả của máy, để chấm sau).",
    ]})
    with pd.ExcelWriter(os.path.join(OUT, "extraction_gold_100.xlsx")) as w:
        guide.to_excel(w, sheet_name="huong_dan", index=False)
        df.to_excel(w, sheet_name="gan_nhan", index=False)
    json.dump(pred, open(os.path.join(OUT, "extraction_pred_100.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(df.groupby(["nguon", "loai_van_ban"]).size().to_string())
    print("có kết quả máy:", sum(v is not None for v in pred.values()), "/", len(pred))
